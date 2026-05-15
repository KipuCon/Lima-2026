"""
=============================================================================
 BUILDING ELEVATOR CONTROL SYSTEM — OT CYBER SECURITY DEMO
 KipuCon Conference Demo | Sec-Llama
=============================================================================
 Simulates 3 elevator PLCs in a 10-floor building using a realistic OT
 state-machine model (Modbus-inspired register map + command queue).

 DEMO ATTACK: CyberAttackDemo floods Elevator 1's command buffer, causing
 its PLC controller to lock up mid-movement — simulating a real-world
 OT DoS attack on industrial control systems.

 Architecture:
   DispatcherSCADA  →  [ElevatorPLC x3]  ←  CyberAttackDemo
                              ↓
                      Building I/O (floors, doors, sensors)

 Usage:
   python elevator_ot_demo.py              # Normal operation
   python elevator_ot_demo.py --attack     # Trigger attack after 10s
   python elevator_ot_demo.py --attack --attack-delay 5
=============================================================================
"""

import threading
import time
import random
import argparse
import queue
import sys
from collections import deque
from datetime import datetime
from enum import Enum, auto


# ── Terminal colors ──────────────────────────────────────────────────────────
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


# ── OT Constants (mirrors real Modbus register layout) ───────────────────────
FLOORS         = 10
TRAVEL_TIME    = 0.6   # seconds per floor (simulated)
DOOR_TIME      = 1.2   # seconds doors stay open
MAX_CMD_QUEUE  = 8     # PLC command buffer size (realistic hardware limit)
POLL_RATE      = 0.1   # SCADA polling interval (seconds)
LOG_WIDTH      = 78


# ── Elevator states (PLC state machine) ─────────────────────────────────────
class ElevatorState(Enum):
    IDLE          = auto()
    MOVING_UP     = auto()
    MOVING_DOWN   = auto()
    DOOR_OPEN     = auto()
    DOOR_CLOSING  = auto()
    FAULT         = auto()   # Triggered by attack / sensor error
    LOCKED_FAULT  = auto()   # Cannot recover without manual reset


# ── Shared print lock ─────────────────────────────────────────────────────────
_print_lock = threading.Lock()

def log(msg, color=""):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    with _print_lock:
        print(f"{C.DIM}[{ts}]{C.RESET} {color}{msg}{C.RESET}")

def banner(msg, color=C.CYAN):
    bar = "─" * LOG_WIDTH
    with _print_lock:
        print(f"\n{color}{bar}")
        print(f"  {msg}")
        print(f"{bar}{C.RESET}\n")


# ── Modbus-style register block (read-only snapshot for SCADA) ───────────────
class PLCRegisters:
    """Mirrors real-world Holding Register map used in elevator PLCs."""
    def __init__(self):
        self.current_floor   = 1     # HR0
        self.target_floor    = 1     # HR1
        self.door_status     = 0     # HR2: 0=closed, 1=open, 2=closing
        self.direction       = 0     # HR3: 0=idle, 1=up, -1=down
        self.fault_code      = 0x00  # HR4: 0=ok, 0x01=overload, 0x10=dos
        self.cmd_queue_depth = 0     # HR5: current buffer utilisation
        self.cycle_count     = 0     # HR6: PLC scan cycles (heartbeat)
        self.state_id        = 0     # HR7: state machine enum value


# ── Elevator PLC ─────────────────────────────────────────────────────────────
class ElevatorPLC(threading.Thread):
    """
    Simulates a real elevator Programmable Logic Controller.

    Each PLC runs its own thread (mimicking independent embedded hardware).
    Commands arrive via a bounded queue — overflow causes FAULT state,
    exactly as it would on a real Allen-Bradley or Siemens S7 controller.
    """

    def __init__(self, eid: int, start_floor: int = 1):
        super().__init__(daemon=True, name=f"ElevatorPLC-{eid}")
        self.eid          = eid
        self.state        = ElevatorState.IDLE
        self.floor        = start_floor
        self.cmd_queue    = queue.Queue(maxsize=MAX_CMD_QUEUE)
        self.registers    = PLCRegisters()
        self.registers.current_floor = start_floor
        self._alive       = True
        self._lock        = threading.Lock()
        self._trip_log    = deque(maxlen=20)   # recent floor trips
        self._scan_cycle  = 0
        self._color       = [C.GREEN, C.BLUE, C.MAGENTA][eid - 1]

    # ── Public API (called by SCADA dispatcher) ──────────────────────────────
    def dispatch(self, floor: int):
        """Send a floor command to the PLC command buffer."""
        if self.state in (ElevatorState.FAULT, ElevatorState.LOCKED_FAULT):
            return False
        try:
            self.cmd_queue.put_nowait(floor)
            return True
        except queue.Full:
            log(f"  ELV-{self.eid} | CMD BUFFER OVERFLOW — command dropped",
                C.YELLOW)
            return False

    def get_registers(self) -> PLCRegisters:
        """SCADA reads the register block (non-destructive poll)."""
        with self._lock:
            r = self.registers
            r.cmd_queue_depth = self.cmd_queue.qsize()
            r.state_id        = self.state.value
            return r

    def inject_fault(self, fault_code: int):
        """
        Simulate a malicious write to the fault register.
        On a real Modbus/TCP system, an attacker with network access
        could write directly to holding registers without authentication.
        """
        with self._lock:
            self.registers.fault_code = fault_code
            self.state = ElevatorState.LOCKED_FAULT
        log(f"  {C.BG_RED}[ATTACK]{C.RESET}{C.RED} ELV-{self.eid} | "
            f"FAULT REGISTER WRITTEN — fault_code=0x{fault_code:02X} | "
            f"Controller LOCKED{C.RESET}")

    def shutdown(self):
        self._alive = False

    # ── PLC scan loop (runs at simulated cycle time) ─────────────────────────
    def run(self):
        log(f"  ELV-{self.eid} | PLC ONLINE | start_floor={self.floor} | "
            f"buffer_size={MAX_CMD_QUEUE}", self._color)
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
            pass  # Cannot recover — needs physical intervention

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
        log(f"  ELV-{self.eid} | DISPATCH → floor {target} | "
            f"direction={dir_str} | from={self.floor}", self._color)

    def _state_move(self, direction: int):
        target = self.registers.target_floor
        time.sleep(TRAVEL_TIME)
        self.floor += direction
        with self._lock:
            self.registers.current_floor = self.floor

        if self.floor == target:
            log(f"  ELV-{self.eid} | ARRIVED floor {self.floor}", self._color)
            self._trip_log.append(self.floor)
            self._open_doors()
        else:
            pass  # Still moving — next scan cycle continues

    def _open_doors(self):
        with self._lock:
            self.registers.door_status = 1
            self.state = ElevatorState.DOOR_OPEN
        log(f"  ELV-{self.eid} | DOORS OPEN  ← floor {self.floor}",
            self._color)
        time.sleep(DOOR_TIME)
        with self._lock:
            self.state = ElevatorState.DOOR_CLOSING

    def _state_door_close(self):
        with self._lock:
            self.registers.door_status = 2
        log(f"  ELV-{self.eid} | DOORS CLOSING — floor {self.floor}",
            self._color)
        time.sleep(0.4)
        with self._lock:
            self.registers.door_status = 0
            self.registers.direction = 0
            self.state = ElevatorState.IDLE

    def _state_fault(self):
        log(f"  {C.YELLOW}ELV-{self.eid} | FAULT STATE — attempting "
            f"auto-recovery (fault_code=0x{self.registers.fault_code:02X})"
            f"{C.RESET}")
        time.sleep(3)
        with self._lock:
            self.registers.fault_code = 0x00
            self.state = ElevatorState.IDLE
        log(f"  ELV-{self.eid} | FAULT CLEARED — back online", self._color)


# ── SCADA Dispatcher ──────────────────────────────────────────────────────────
class DispatcherSCADA(threading.Thread):
    """
    Simulates the building SCADA / elevator group controller.
    Polls each PLC's register block and dispatches floor calls
    using nearest-car algorithm (standard in real systems).
    """

    def __init__(self, elevators: list):
        super().__init__(daemon=True, name="DispatcherSCADA")
        self.elevators = elevators
        self._alive    = True
        self._call_log = deque(maxlen=50)

    def shutdown(self):
        self._alive = False

    def run(self):
        log("  SCADA DISPATCHER ONLINE | algo=nearest-car | "
            f"elevators={len(self.elevators)}", C.CYAN)
        while self._alive:
            # Simulate random floor calls arriving
            time.sleep(random.uniform(2.0, 4.5))
            floor = random.randint(1, FLOORS)
            self._assign_call(floor)

    def _assign_call(self, floor: int):
        best_elv = None
        best_dist = float('inf')

        for elv in self.elevators:
            regs = elv.get_registers()
            if regs.fault_code != 0x00:
                continue   # Skip faulted controllers
            if regs.state_id == ElevatorState.LOCKED_FAULT.value:
                continue
            dist = abs(regs.current_floor - floor)
            if dist < best_dist:
                best_dist = dist
                best_elv  = elv

        if best_elv is None:
            log(f"  SCADA | CALL floor {floor} — NO AVAILABLE ELEVATOR",
                C.RED)
            return

        success = best_elv.dispatch(floor)
        tag = "OK" if success else "REJECTED"
        log(f"  SCADA | CALL floor {floor} → assigned ELV-{best_elv.eid} "
            f"[dist={best_dist}] [{tag}]", C.CYAN)
        self._call_log.append((floor, best_elv.eid, success))


# ── Status Display ────────────────────────────────────────────────────────────
class StatusDisplay(threading.Thread):
    """Periodic status board — mimics an HMI dashboard."""

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
            ElevatorState.IDLE:         f"{C.DIM}●{C.RESET}",
            ElevatorState.MOVING_UP:    f"{C.GREEN}▲{C.RESET}",
            ElevatorState.MOVING_DOWN:  f"{C.BLUE}▼{C.RESET}",
            ElevatorState.DOOR_OPEN:    f"{C.YELLOW}≡{C.RESET}",
            ElevatorState.DOOR_CLOSING: f"{C.YELLOW}]{C.RESET}",
            ElevatorState.FAULT:        f"{C.RED}!{C.RESET}",
            ElevatorState.LOCKED_FAULT: f"{C.BG_RED}✗{C.RESET}",
        }

        lines = [f"\n  {'─'*62}",
                 f"  {'HMI STATUS BOARD':^62}",
                 f"  {'─'*62}",
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

        lines.append(f"  {'─'*62}\n")
        with _print_lock:
            print("\n".join(lines))


# ── Cyber Attack Demo ─────────────────────────────────────────────────────────
class CyberAttackDemo:
    """
    Demonstrates a realistic OT attack against Elevator 1's PLC.

    Phase 1 — Recon:    SCADA poll traffic observed (passive)
    Phase 2 — Flood:    Command buffer saturated (queue exhaustion DoS)
    Phase 3 — Exploit:  Direct fault register write (auth bypass)
    Phase 4 — Impact:   Elevator locked in place, doors frozen closed

    In a real building system this attack vector exists because:
      • Many elevator Modbus/TCP implementations have no authentication
      • BACnet (common in building automation) broadcasts on UDP 47808
      • OT networks are often flat — no segmentation between SCADA and PLCs
    """

    def __init__(self, target: ElevatorPLC, delay: float = 10.0):
        self.target = target
        self.delay  = delay

    def run(self):
        time.sleep(self.delay)
        self._phase_recon()
        time.sleep(2)
        self._phase_flood()
        time.sleep(1)
        self._phase_exploit()

    def _phase_recon(self):
        banner("ATTACK PHASE 1 — PASSIVE RECON  (Modbus/TCP sniffing)",
               C.YELLOW)
        regs = self.target.get_registers()
        log(f"  [ATTACKER] Sniffed Modbus poll response from ELV-{self.target.eid}",
            C.YELLOW)
        log(f"  [ATTACKER] HR0=current_floor:{regs.current_floor}  "
            f"HR1=target:{regs.target_floor}  HR4=fault:0x{regs.fault_code:02X}",
            C.YELLOW)
        log(f"  [ATTACKER] No authentication required — writable registers exposed",
            C.YELLOW)

    def _phase_flood(self):
        banner("ATTACK PHASE 2 — COMMAND BUFFER FLOOD  (OT DoS)", C.RED)
        log(f"  [ATTACKER] Flooding ELV-{self.target.eid} command queue "
            f"(buffer_max={MAX_CMD_QUEUE})...", C.RED)
        # Saturate the PLC command queue with junk floor commands
        for i in range(MAX_CMD_QUEUE * 3):
            fake_floor = random.randint(1, FLOORS)
            accepted = self.target.dispatch(fake_floor)
            tag = "ACCEPTED" if accepted else f"{C.BG_YEL}DROPPED{C.RESET}"
            log(f"  [ATTACKER] WRITE FC=15 → floor={fake_floor:02d}  [{tag}]",
                C.RED)
            time.sleep(0.05)

    def _phase_exploit(self):
        banner("ATTACK PHASE 3 — FAULT REGISTER WRITE  (Impact)", C.RED)
        log(f"  [ATTACKER] Writing fault_code=0x10 to ELV-{self.target.eid} "
            f"HR4 (no auth required on Modbus/TCP)", C.RED)
        # Direct register manipulation — simulates unauthenticated Modbus write
        self.target.inject_fault(0x10)
        log(f"  {C.BG_RED}[IMPACT]{C.RESET}{C.RED} ELV-{self.target.eid} "
            f"LOCKED. Passengers trapped. Manual reset required.", C.RED)
        log(f"  [ATTACKER] Attack complete. 2 elevators still operational.",
            C.RED)
        banner("ATTACK COMPLETE — This is why OT network segmentation matters",
               C.RED)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Elevator OT Cyber Demo — KipuCon / Sec-Llama")
    parser.add_argument("--attack", action="store_true",
                        help="Enable the cyber attack demo")
    parser.add_argument("--attack-delay", type=float, default=10.0,
                        help="Seconds before attack starts (default: 10)")
    parser.add_argument("--duration", type=float, default=60.0,
                        help="Total demo runtime in seconds (default: 60)")
    args = parser.parse_args()

    banner("BUILDING ELEVATOR CONTROL SYSTEM — OT CYBER DEMO\n"
           "  Sec-Llama | KipuCon Conference\n"
           f"  Floors: {FLOORS}  |  Elevators: 3  |  "
           f"Attack: {'ENABLED' if args.attack else 'disabled'}",
           C.CYAN)

    # Instantiate PLCs at staggered floors
    elevators = [
        ElevatorPLC(eid=1, start_floor=1),
        ElevatorPLC(eid=2, start_floor=5),
        ElevatorPLC(eid=3, start_floor=10),
    ]

    scada   = DispatcherSCADA(elevators)
    display = StatusDisplay(elevators, interval=6.0)

    # Start all PLC threads
    for elv in elevators:
        elv.start()

    time.sleep(0.5)
    scada.start()
    display.start()

    # Launch attack in background thread if requested
    if args.attack:
        attack = CyberAttackDemo(target=elevators[0],
                                 delay=args.attack_delay)
        t = threading.Thread(target=attack.run, daemon=True,
                             name="CyberAttackDemo")
        log(f"  DEMO MODE: Attack on ELV-1 will trigger in "
            f"{args.attack_delay:.0f}s", C.YELLOW)
        t.start()

    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        pass

    banner("DEMO ENDED — shutting down", C.DIM)
    scada.shutdown()
    display.shutdown()


if __name__ == "__main__":
    main()
