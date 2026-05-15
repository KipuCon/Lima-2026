"""
Shared TCP protocol and constants for the OT elevator demo.

Wire format: [4-byte big-endian length][JSON payload]
Both elevator_server.py and attacker_client.py import this module.
"""

import json
import struct

# ── Connection ────────────────────────────────────────────────────────────────
HOST = "127.0.0.1"
PORT = 5020  # Not 502 — avoids admin/root privileges

# ── Modbus function codes (mirrored for educational realism) ──────────────────
FC_READ_REGISTERS  = 3   # Read holding registers
FC_WRITE_REGISTER  = 6   # Write single register
FC_WRITE_MULTIPLE  = 15  # Write multiple registers (dispatch floor cmd)
FC_LIST_UNITS      = 17  # List connected unit IDs
FC_SET_PHASE       = 99  # Attack phase announcement (attacker → server)

# ── Register addresses (HR = holding register) ───────────────────────────────
HR_CURRENT_FLOOR   = 0
HR_TARGET_FLOOR    = 1
HR_DOOR_STATUS     = 2
HR_DIRECTION       = 3
HR_FAULT_CODE      = 4
HR_CMD_QUEUE_DEPTH = 5
HR_CYCLE_COUNT     = 6
HR_STATE_ID        = 7

REGISTER_NAMES = {
    HR_CURRENT_FLOOR:   "current_floor",
    HR_TARGET_FLOOR:    "target_floor",
    HR_DOOR_STATUS:     "door_status",
    HR_DIRECTION:       "direction",
    HR_FAULT_CODE:      "fault_code",
    HR_CMD_QUEUE_DEPTH: "cmd_queue_depth",
    HR_CYCLE_COUNT:     "cycle_count",
    HR_STATE_ID:        "state_id",
}


# ── Wire protocol helpers ────────────────────────────────────────────────────
def send_message(sock, msg: dict):
    """Serialize a dict as length-prefixed JSON and send over socket."""
    payload = json.dumps(msg).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_message(sock) -> dict | None:
    """Receive and deserialize a length-prefixed JSON message. Returns None on disconnect."""
    header = _recv_exact(sock, 4)
    if header is None:
        return None
    length = struct.unpack("!I", header)[0]
    if length > 1_000_000:  # sanity cap
        return None
    payload = _recv_exact(sock, length)
    if payload is None:
        return None
    return json.loads(payload.decode("utf-8"))


def _recv_exact(sock, n: int) -> bytes | None:
    """Read exactly n bytes from socket. Returns None on disconnect."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
