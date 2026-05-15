"""
=============================================================================
 BUILDING ELEVATOR CONTROL SYSTEM — OT CYBER SECURITY DEMO (SERVER)
 KipuCon Conference Demo | Sec-Llama
=============================================================================
 Runs the 3-elevator simulation with a Modbus-style TCP server (port 5020)
 and an aiohttp web server (port 8080) serving a real-time dashboard.

 Usage:
   python elevator_server.py                        # defaults
   python elevator_server.py --no-recovery          # original terminal LOCKED_FAULT
   python elevator_server.py --fault-ttl 10         # custom recovery time (seconds)
   python elevator_server.py --port 5020 --web-port 8080
=============================================================================
"""

import threading
import time
import random
import argparse
import queue
import socket
import asyncio
import sys
import os
from collections import deque
from datetime import datetime
from enum import Enum, auto

from ot_protocol import (
    HOST, PORT,
    FC_READ_REGISTERS, FC_WRITE_REGISTER, FC_WRITE_MULTIPLE, FC_LIST_UNITS,
    FC_SET_PHASE,
    HR_CURRENT_FLOOR, HR_TARGET_FLOOR, HR_DOOR_STATUS, HR_DIRECTION,
    HR_FAULT_CODE, HR_CMD_QUEUE_DEPTH, HR_CYCLE_COUNT, HR_STATE_ID,
    REGISTER_NAMES, send_message, recv_message,
)

try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# Fix Windows console encoding for Unicode box-drawing characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)


# ── Terminal colors ───────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    BG_RED  = "\033[41m"
    BG_YEL  = "\033[43m"


# ── OT Constants ─────────────────────────────────────────────────────────────
FLOORS         = 10
TRAVEL_TIME    = 1.2
DOOR_TIME      = 2.0
MAX_CMD_QUEUE  = 8
POLL_RATE      = 0.1
LOG_WIDTH      = 78


# ── Elevator states ──────────────────────────────────────────────────────────
class ElevatorState(Enum):
    IDLE          = auto()
    MOVING_UP     = auto()
    MOVING_DOWN   = auto()
    DOOR_OPEN     = auto()
    DOOR_CLOSING  = auto()
    FAULT         = auto()
    LOCKED_FAULT  = auto()


# ── Event bus (for dashboard) ────────────────────────────────────────────────
event_log = deque(maxlen=500)
network_packets = deque(maxlen=50)
attack_phase = 0  # 0=normal, 1=recon, 2=flood, 3=exploit, 4=impact
_start_time = time.time()
_print_lock = threading.Lock()


def _elapsed():
    return round(time.time() - _start_time, 1)


def log(msg, color="", source="SYSTEM", event_type="info"):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    with _print_lock:
        print(f"{C.DIM}[{ts}]{C.RESET} {color}{msg}{C.RESET}")
        sys.stdout.flush()
    event_log.append({
        "time": ts,
        "elapsed": _elapsed(),
        "source": source,
        "type": event_type,
        "msg": msg.replace("\033[0m", "").replace("\033[1m", "")
              .replace("\033[91m", "").replace("\033[92m", "")
              .replace("\033[93m", "").replace("\033[94m", "")
              .replace("\033[95m", "").replace("\033[96m", "")
              .replace("\033[97m", "").replace("\033[2m", "")
              .replace("\033[41m", "").replace("\033[43m", ""),
    })


def banner(msg, color=C.CYAN):
    bar = "\u2500" * LOG_WIDTH
    with _print_lock:
        print(f"\n{color}{bar}")
        print(f"  {msg}")
        print(f"{bar}{C.RESET}\n")
        sys.stdout.flush()


def _strip_ansi(s):
    """Remove ANSI escape sequences from string."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', s)


# ── PLCRegisters ─────────────────────────────────────────────────────────────
class PLCRegisters:
    def __init__(self):
        self.current_floor   = 1
        self.target_floor    = 1
        self.door_status     = 0
        self.direction       = 0
        self.fault_code      = 0x00
        self.cmd_queue_depth = 0
        self.cycle_count     = 0
        self.state_id        = 0

    def to_dict(self):
        return {
            HR_CURRENT_FLOOR:   self.current_floor,
            HR_TARGET_FLOOR:    self.target_floor,
            HR_DOOR_STATUS:     self.door_status,
            HR_DIRECTION:       self.direction,
            HR_FAULT_CODE:      self.fault_code,
            HR_CMD_QUEUE_DEPTH: self.cmd_queue_depth,
            HR_CYCLE_COUNT:     self.cycle_count,
            HR_STATE_ID:        self.state_id,
        }


# ── ElevatorPLC ──────────────────────────────────────────────────────────────
class ElevatorPLC(threading.Thread):
    def __init__(self, eid: int, start_floor: int = 1,
                 fault_ttl: float = 8.0, no_recovery: bool = False):
        super().__init__(daemon=True, name=f"ElevatorPLC-{eid}")
        self.eid          = eid
        self.state        = ElevatorState.IDLE
        self.floor        = start_floor
        self.cmd_queue    = queue.Queue(maxsize=MAX_CMD_QUEUE)
        self.registers    = PLCRegisters()
        self.registers.current_floor = start_floor
        self._alive       = True
        self._lock        = threading.Lock()
        self._trip_log    = deque(maxlen=20)
        self._scan_cycle  = 0
        self._color       = [C.GREEN, C.BLUE, C.MAGENTA][eid - 1]
        # Recovery mechanism
        self._fault_ttl        = fault_ttl
        self._no_recovery      = no_recovery
        self._fault_refresh_time = None

    def dispatch(self, floor: int):
        if self.state in (ElevatorState.FAULT, ElevatorState.LOCKED_FAULT):
            return False
        try:
            self.cmd_queue.put_nowait(floor)
            return True
        except queue.Full:
            log(f"  ELV-{self.eid} | CMD BUFFER OVERFLOW \u2014 command dropped",
                C.YELLOW, source=f"ELV-{self.eid}", event_type="overflow")
            return False

    def get_registers(self) -> PLCRegisters:
        with self._lock:
            r = self.registers
            r.cmd_queue_depth = self.cmd_queue.qsize()
            r.state_id        = self.state.value
            return r

    def inject_fault(self, fault_code: int):
        with self._lock:
            self.registers.fault_code = fault_code
            self.state = ElevatorState.LOCKED_FAULT
            self._fault_refresh_time = time.time()
        log(f"  {C.BG_RED}[ATTACK]{C.RESET}{C.RED} ELV-{self.eid} | "
            f"FAULT REGISTER WRITTEN \u2014 fault_code=0x{fault_code:02X} | "
            f"Controller LOCKED{C.RESET}",
            source=f"ELV-{self.eid}", event_type="attack")

    def refresh_fault(self):
        """Attacker refreshes fault TTL to maintain persistence."""
        with self._lock:
            if self.state == ElevatorState.LOCKED_FAULT:
                self._fault_refresh_time = time.time()

    def shutdown(self):
        self._alive = False

    def run(self):
        log(f"  ELV-{self.eid} | PLC ONLINE | start_floor={self.floor} | "
            f"buffer_size={MAX_CMD_QUEUE}", self._color,
            source=f"ELV-{self.eid}", event_type="startup")
        while self._alive:
            self._scan_cycle += 1
            with self._lock:
                self.registers.cycle_count = self._scan_cycle
            self._execute_state()
            time.sleep(POLL_RATE)

    def _execute_state(self):
        if self.state == ElevatorState.IDLE:
            self._state_idle()
        elif self.state == ElevatorState.MOVING_UP:
            self._state_move(1)
        elif self.state == ElevatorState.MOVING_DOWN:
            self._state_move(-1)
        elif self.state == ElevatorState.DOOR_OPEN:
            self._state_door_open()
        elif self.state == ElevatorState.DOOR_CLOSING:
            self._state_door_close()
        elif self.state == ElevatorState.FAULT:
            self._state_fault()
        elif self.state == ElevatorState.LOCKED_FAULT:
            self._state_locked_fault()

    def _state_idle(self):
        try:
            target = self.cmd_queue.get_nowait()
        except queue.Empty:
            return
        with self._lock:
            self.registers.target_floor = target
        if target == self.floor:
            self._open_doors()
            return
        direction = 1 if target > self.floor else -1
        with self._lock:
            self.registers.direction = direction
            self.state = (ElevatorState.MOVING_UP if direction == 1
                          else ElevatorState.MOVING_DOWN)
        dir_str = "UP" if direction == 1 else "DOWN"
        log(f"  ELV-{self.eid} | DISPATCH \u2192 floor {target} | "
            f"direction={dir_str} | from={self.floor}", self._color,
            source=f"ELV-{self.eid}", event_type="dispatch")

    def _is_faulted(self):
        """Check if a fault was injected during a sleep — don't overwrite it."""
        return self.state in (ElevatorState.FAULT, ElevatorState.LOCKED_FAULT)

    def _state_move(self, direction: int):
        target = self.registers.target_floor
        time.sleep(TRAVEL_TIME)
        if self._is_faulted():
            return
        self.floor += direction
        with self._lock:
            self.registers.current_floor = self.floor
        if self.floor == target:
            log(f"  ELV-{self.eid} | ARRIVED floor {self.floor}", self._color,
                source=f"ELV-{self.eid}", event_type="arrived")
            self._trip_log.append(self.floor)
            self._open_doors()

    def _open_doors(self):
        if self._is_faulted():
            return
        with self._lock:
            self.registers.door_status = 1
            self.state = ElevatorState.DOOR_OPEN
        log(f"  ELV-{self.eid} | DOORS OPEN  \u2190 floor {self.floor}",
            self._color, source=f"ELV-{self.eid}", event_type="doors")
        time.sleep(DOOR_TIME)
        if self._is_faulted():
            return
        with self._lock:
            self.state = ElevatorState.DOOR_CLOSING

    def _state_door_open(self):
        pass  # Door timing handled in _open_doors

    def _state_door_close(self):
        with self._lock:
            self.registers.door_status = 2
        log(f"  ELV-{self.eid} | DOORS CLOSING \u2014 floor {self.floor}",
            self._color, source=f"ELV-{self.eid}", event_type="doors")
        time.sleep(0.4)
        if self._is_faulted():
            return
        with self._lock:
            self.registers.door_status = 0
            self.registers.direction = 0
            self.state = ElevatorState.IDLE

    def _state_fault(self):
        log(f"  {C.YELLOW}ELV-{self.eid} | FAULT STATE \u2014 attempting "
            f"auto-recovery (fault_code=0x{self.registers.fault_code:02X})"
            f"{C.RESET}", source=f"ELV-{self.eid}", event_type="fault")
        time.sleep(3)
        with self._lock:
            self.registers.fault_code = 0x00
            self.state = ElevatorState.IDLE
        log(f"  ELV-{self.eid} | FAULT CLEARED \u2014 back online", self._color,
            source=f"ELV-{self.eid}", event_type="recovery")

    def _state_locked_fault(self):
        global attack_phase
        if self._no_recovery:
            return  # Original behavior — permanent lock
        if (self._fault_refresh_time is not None and
                time.time() - self._fault_refresh_time > self._fault_ttl):
            with self._lock:
                self.registers.fault_code = 0x00
                self.state = ElevatorState.IDLE
                self._fault_refresh_time = None
            attack_phase = 0
            log(f"  {C.GREEN}{C.BOLD}ELV-{self.eid} | FAULT TTL EXPIRED \u2014 "
                f"AUTO-RECOVERY \u2014 PLC back online{C.RESET}",
                source=f"ELV-{self.eid}", event_type="recovery")


# ── SCADA Dispatcher ─────────────────────────────────────────────────────────
class DispatcherSCADA(threading.Thread):
    def __init__(self, elevators: list):
        super().__init__(daemon=True, name="DispatcherSCADA")
        self.elevators = elevators
        self._alive    = True
        self._call_log = deque(maxlen=50)

    def shutdown(self):
        self._alive = False

    def run(self):
        log("  SCADA DISPATCHER ONLINE | algo=nearest-car | "
            f"elevators={len(self.elevators)}", C.CYAN,
            source="SCADA", event_type="startup")
        while self._alive:
            time.sleep(random.uniform(2.0, 4.5))
            floor = random.randint(1, FLOORS)
            self._assign_call(floor)

    def _assign_call(self, floor: int):
        best_elv = None
        best_dist = float('inf')
        for elv in self.elevators:
            regs = elv.get_registers()
            if regs.fault_code != 0x00:
                continue
            if regs.state_id == ElevatorState.LOCKED_FAULT.value:
                continue
            dist = abs(regs.current_floor - floor)
            if dist < best_dist:
                best_dist = dist
                best_elv  = elv
        if best_elv is None:
            log(f"  SCADA | CALL floor {floor} \u2014 NO AVAILABLE ELEVATOR",
                C.RED, source="SCADA", event_type="no_elevator")
            return
        success = best_elv.dispatch(floor)
        tag = "OK" if success else "REJECTED"
        log(f"  SCADA | CALL floor {floor} \u2192 assigned ELV-{best_elv.eid} "
            f"[dist={best_dist}] [{tag}]", C.CYAN,
            source="SCADA", event_type="dispatch")
        self._call_log.append((floor, best_elv.eid, success))
        network_packets.append({
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "elapsed": _elapsed(),
            "source": "SCADA",
            "target": f"ELV-{best_elv.eid}",
            "fc": FC_WRITE_MULTIPLE,
            "type": "normal",
        })


# ── Status Display ───────────────────────────────────────────────────────────
class StatusDisplay(threading.Thread):
    def __init__(self, elevators: list, interval: float = 5.0):
        super().__init__(daemon=True, name="StatusDisplay")
        self.elevators = elevators
        self.interval  = interval
        self._alive    = True

    def shutdown(self):
        self._alive = False

    def run(self):
        while self._alive:
            time.sleep(self.interval)
            self._render()

    def _render(self):
        state_icons = {
            ElevatorState.IDLE:         f"{C.DIM}\u25cf{C.RESET}",
            ElevatorState.MOVING_UP:    f"{C.GREEN}\u25b2{C.RESET}",
            ElevatorState.MOVING_DOWN:  f"{C.BLUE}\u25bc{C.RESET}",
            ElevatorState.DOOR_OPEN:    f"{C.YELLOW}\u2261{C.RESET}",
            ElevatorState.DOOR_CLOSING: f"{C.YELLOW}]{C.RESET}",
            ElevatorState.FAULT:        f"{C.RED}!{C.RESET}",
            ElevatorState.LOCKED_FAULT: f"{C.BG_RED}\u2717{C.RESET}",
        }
        sep = "\u2500" * 62
        lines = [f"\n  {sep}",
                 f"  {'HMI STATUS BOARD':^62}",
                 f"  {sep}",
                 f"  {'ELV':<6} {'FLOOR':<8} {'STATE':<18} {'QUEUE':<8} {'FAULT':<8} {'CYCLES':<8}"]
        for elv in self.elevators:
            r    = elv.get_registers()
            s    = ElevatorState(r.state_id)
            icon = state_icons.get(s, "?")
            fault_str = f"0x{r.fault_code:02X}" if r.fault_code else "  OK"
            fault_col = C.RED if r.fault_code else C.GREEN
            lines.append(
                f"  {C.BOLD}ELV-{elv.eid}{C.RESET}  "
                f"FL:{r.current_floor:<4}  "
                f"{icon} {s.name:<15} "
                f"Q:{r.cmd_queue_depth:<5} "
                f"{fault_col}{fault_str:<8}{C.RESET}"
                f"{r.cycle_count:<8}"
            )
        lines.append(f"  {sep}\n")
        with _print_lock:
            print("\n".join(lines))


# ── Modbus TCP Server ────────────────────────────────────────────────────────
class ModbusTCPServer(threading.Thread):
    def __init__(self, elevators: list, host: str = HOST, port: int = PORT):
        super().__init__(daemon=True, name="ModbusTCPServer")
        self.elevators = {elv.eid: elv for elv in elevators}
        self.host = host
        self.port = port
        self._alive = True

    def shutdown(self):
        self._alive = False

    def run(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(5)
        srv.settimeout(1.0)
        log(f"  MODBUS TCP SERVER listening on {self.host}:{self.port}", C.CYAN,
            source="MODBUS", event_type="startup")
        while self._alive:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            log(f"  MODBUS | Connection from {addr[0]}:{addr[1]}", C.YELLOW,
                source="MODBUS", event_type="connection")
            t = threading.Thread(target=self._handle_client, args=(conn, addr),
                                 daemon=True)
            t.start()
        srv.close()

    def _handle_client(self, conn, addr):
        global attack_phase
        conn.settimeout(30.0)
        try:
            while self._alive:
                msg = recv_message(conn)
                if msg is None:
                    break
                fc = msg.get("fc")
                unit = msg.get("unit", 1)
                resp = {"fc": fc, "unit": unit}

                if fc == FC_LIST_UNITS:
                    resp["units"] = list(self.elevators.keys())
                    network_packets.append({
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "elapsed": _elapsed(),
                        "source": f"{addr[0]}",
                        "target": "SERVER",
                        "fc": fc,
                        "type": "recon",
                    })

                elif fc == FC_READ_REGISTERS:
                    elv = self.elevators.get(unit)
                    if elv:
                        regs = elv.get_registers()
                        resp["registers"] = regs.to_dict()
                        resp["state_name"] = ElevatorState(regs.state_id).name
                    else:
                        resp["error"] = f"Unknown unit {unit}"
                    network_packets.append({
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "elapsed": _elapsed(),
                        "source": f"{addr[0]}",
                        "target": f"ELV-{unit}",
                        "fc": fc,
                        "type": "recon",
                    })

                elif fc == FC_WRITE_REGISTER:
                    address = msg.get("address", 0)
                    value = msg.get("value", 0)
                    elv = self.elevators.get(unit)
                    if elv and address == HR_FAULT_CODE:
                        if value != 0:
                            if elv.state == ElevatorState.LOCKED_FAULT:
                                elv.refresh_fault()
                                resp["status"] = "REFRESHED"
                            else:
                                elv.inject_fault(value)
                                resp["status"] = "FAULT_INJECTED"
                        else:
                            resp["status"] = "IGNORED"
                        network_packets.append({
                            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                            "elapsed": _elapsed(),
                            "source": f"{addr[0]}",
                            "target": f"ELV-{unit}",
                            "fc": fc,
                            "type": "attack",
                            "detail": f"HR4=0x{value:02X}",
                        })
                    else:
                        resp["error"] = f"Write not supported for address {address}"

                elif fc == FC_SET_PHASE:
                    phase_val = msg.get("phase", 0)
                    if 0 <= phase_val <= 4:
                        attack_phase = phase_val
                        resp["status"] = "OK"
                        phase_names = ["NORMAL", "RECON", "FLOOD", "EXPLOIT", "IMPACT"]
                        log(f"  MODBUS | Attack phase set to {phase_val} ({phase_names[phase_val]})",
                            C.YELLOW if phase_val > 0 else C.GREEN,
                            source="MODBUS", event_type="phase")
                    else:
                        resp["error"] = f"Invalid phase {phase_val}"

                elif fc == FC_WRITE_MULTIPLE:
                    floor_val = msg.get("floor", 1)
                    elv = self.elevators.get(unit)
                    if elv:
                        accepted = elv.dispatch(floor_val)
                        resp["status"] = "ACCEPTED" if accepted else "REJECTED"
                    else:
                        resp["error"] = f"Unknown unit {unit}"
                    pkt_type = "attack" if attack_phase >= 2 else "normal"
                    network_packets.append({
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "elapsed": _elapsed(),
                        "source": f"{addr[0]}",
                        "target": f"ELV-{unit}",
                        "fc": fc,
                        "type": pkt_type,
                    })

                else:
                    resp["error"] = f"Unknown function code {fc}"

                send_message(conn, resp)

        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            conn.close()
            log(f"  MODBUS | Disconnected {addr[0]}:{addr[1]}", C.DIM,
                source="MODBUS", event_type="disconnect")


# ── aiohttp WebSocket + HTTP server ─────────────────────────────────────────
class WebDashboardServer:
    def __init__(self, elevators: list, host: str = "0.0.0.0", port: int = 8080):
        self.elevators = elevators
        self.host = host
        self.port = port
        self._ws_clients = set()
        self._loop = None

    def start_in_thread(self):
        t = threading.Thread(target=self._run, daemon=True, name="WebDashboard")
        t.start()

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_server())

    async def _start_server(self):
        app = web.Application()
        app.router.add_get("/", self._handle_index)
        app.router.add_get("/ws", self._handle_ws)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        log(f"  WEB DASHBOARD at http://localhost:{self.port}", C.CYAN,
            source="WEB", event_type="startup")

        # Broadcast loop
        while True:
            await asyncio.sleep(0.2)
            if self._ws_clients:
                snapshot = self._build_snapshot()
                dead = set()
                for ws in self._ws_clients:
                    try:
                        await ws.send_json(snapshot)
                    except (ConnectionResetError, Exception):
                        dead.add(ws)
                self._ws_clients -= dead

    def _build_snapshot(self):
        elev_data = []
        for elv in self.elevators:
            r = elv.get_registers()
            s = ElevatorState(r.state_id)
            elev_data.append({
                "id": elv.eid,
                "floor": r.current_floor,
                "target": r.target_floor,
                "door": r.door_status,
                "direction": r.direction,
                "fault": r.fault_code,
                "queue_depth": r.cmd_queue_depth,
                "queue_max": MAX_CMD_QUEUE,
                "state": s.name,
            })
        recent_events = list(event_log)[-30:]
        recent_packets = list(network_packets)[-20:]
        return {
            "type": "state",
            "elapsed": _elapsed(),
            "attack_phase": attack_phase,
            "elevators": elev_data,
            "events": recent_events,
            "network_packets": recent_packets,
        }

    async def _handle_index(self, request):
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "dashboard.html")
        if os.path.exists(html_path):
            return web.FileResponse(html_path)
        return web.Response(text="dashboard.html not found", status=404)

    async def _handle_ws(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._ws_clients.add(ws)
        try:
            async for msg in ws:
                pass  # We don't process incoming WS messages for now
        finally:
            self._ws_clients.discard(ws)
        return ws


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    global _start_time

    parser = argparse.ArgumentParser(
        description="Elevator OT Server \u2014 KipuCon / Sec-Llama")
    parser.add_argument("--port", type=int, default=PORT,
                        help=f"Modbus TCP port (default: {PORT})")
    parser.add_argument("--web-port", type=int, default=8080,
                        help="Web dashboard port (default: 8080)")
    parser.add_argument("--no-recovery", action="store_true",
                        help="Original terminal LOCKED_FAULT (no auto-recovery)")
    parser.add_argument("--fault-ttl", type=float, default=8.0,
                        help="Seconds before auto-recovery from LOCKED_FAULT (default: 8)")
    parser.add_argument("--duration", type=float, default=300.0,
                        help="Total demo runtime in seconds (default: 300)")
    args = parser.parse_args()

    _start_time = time.time()

    banner("BUILDING ELEVATOR CONTROL SYSTEM \u2014 OT CYBER DEMO (SERVER)\n"
           "  Sec-Llama | KipuCon Conference\n"
           f"  Floors: {FLOORS}  |  Elevators: 3  |  "
           f"Recovery: {'DISABLED' if args.no_recovery else f'{args.fault_ttl}s TTL'}\n"
           f"  Modbus TCP: port {args.port}  |  Dashboard: http://localhost:{args.web_port}",
           C.CYAN)

    elevators = [
        ElevatorPLC(eid=1, start_floor=1,
                    fault_ttl=args.fault_ttl, no_recovery=args.no_recovery),
        ElevatorPLC(eid=2, start_floor=5,
                    fault_ttl=args.fault_ttl, no_recovery=args.no_recovery),
        ElevatorPLC(eid=3, start_floor=10,
                    fault_ttl=args.fault_ttl, no_recovery=args.no_recovery),
    ]

    scada   = DispatcherSCADA(elevators)
    display = StatusDisplay(elevators, interval=6.0)
    modbus  = ModbusTCPServer(elevators, host=HOST, port=args.port)

    for elv in elevators:
        elv.start()

    time.sleep(0.5)
    scada.start()
    display.start()
    modbus.start()

    # Start web dashboard
    if HAS_AIOHTTP:
        dashboard = WebDashboardServer(elevators, port=args.web_port)
        dashboard.start_in_thread()
    else:
        log("  WARNING: aiohttp not installed \u2014 web dashboard disabled. "
            "Install with: pip install aiohttp", C.YELLOW,
            source="WEB", event_type="warning")

    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        pass

    banner("DEMO ENDED \u2014 shutting down", C.DIM)
    scada.shutdown()
    display.shutdown()
    modbus.shutdown()


if __name__ == "__main__":
    main()
