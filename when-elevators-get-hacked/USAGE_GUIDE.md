# OT Elevator Cyber Security Demo — Usage Guide

## Sec-Llama | KipuCon Conference

This framework simulates a building elevator control system (OT/SCADA) and demonstrates
real-world OT cyber attack techniques over a Modbus-style TCP protocol. It includes a
live web dashboard for visual demonstration.

---

## Prerequisites

- Python 3.8+
- `aiohttp` package (for the web dashboard): `pip install aiohttp`
- A modern web browser (for the dashboard)

---

## Files Overview

| File | Purpose |
|------|---------|
| `elevator_server.py` | Building elevator server — runs 3 PLCs, SCADA dispatcher, Modbus TCP server, and web dashboard |
| `attacker_client.py` | Red team attack tool — connects to the server and executes multi-phase OT attacks |
| `ot_protocol.py` | Shared protocol definitions (function codes, register addresses, message framing) |
| `dashboard.html` | Real-time web dashboard (served by the server at http://localhost:8080) |

---

## Quick Start

### Step 1: Start the Server

```bash
python elevator_server.py
```

This starts:
- 3 elevator PLCs (ELV-1, ELV-2, ELV-3) on floors 1, 5, and 10
- SCADA dispatcher sending random floor calls
- Modbus TCP server on port 5020
- Web dashboard on http://localhost:8080

Open `http://localhost:8080` in your browser to see the live dashboard.

### Step 2: Run an Attack

In a second terminal:

```bash
python attacker_client.py --persist --delay 3
```

Watch both the terminal output and the dashboard as the attack progresses through phases.

### Step 3: Recovery

- Press `Ctrl+C` to stop the attacker
- The elevator auto-recovers after ~8 seconds (fault TTL expires)
- Dashboard returns to NORMAL phase

---

## Attack Scenarios

### Full Attack on ELV-1 (Default)

```bash
python attacker_client.py
```

Runs: RECON → FLOOD → EXPLOIT → disconnects.
ELV-1 gets locked with fault code 0x10, then auto-recovers after ~8s.

### Full Attack with Persistence

```bash
python attacker_client.py --persist
```

Same as above, but after exploiting, the attacker continuously re-writes the fault register
every 2 seconds to prevent auto-recovery. Press `Ctrl+C` to release.

### Full Attack with Slower Pacing (Best for Live Demo)

```bash
python attacker_client.py --persist --delay 3
```

Adds a 3-second pause between each attack phase, giving the audience time to observe
each phase transition on the dashboard.

### Reconnaissance Only

```bash
python attacker_client.py --recon-only
```

Runs only Phase 1: discovers all PLC units, reads register values, identifies
the lack of authentication. No damage is done. Good for showing the "scanning" phase.

### Command Buffer Flood Only

```bash
python attacker_client.py --flood-only
```

Runs Phase 1 (recon) then Phase 2 (flood): sends 24 rapid floor commands to overflow
the command queue. Shows how OT DoS works — queue fills up, legitimate commands get rejected.

### Custom Flood Intensity

```bash
python attacker_client.py --flood-only --flood-count 50
```

Send 50 flood commands instead of the default 24.

### Target a Specific Elevator

```bash
python attacker_client.py --target 2
python attacker_client.py --target 3 --persist
```

Attack ELV-2 or ELV-3 instead of the default ELV-1.

### Cascade Attack — Kill ALL Elevators

```bash
python attacker_client.py --target all
```

Runs: RECON → FLOOD → CASCADE (exploits ELV-1, ELV-2, ELV-3 sequentially).
Result: complete building elevator shutdown.

### Cascade with Persistence

```bash
python attacker_client.py --target all --persist --delay 2
```

Locks all 3 elevators and maintains the fault on all of them in round-robin.
The ultimate attack scenario — full building shutdown with persistence.

---

## Server Options

```bash
python elevator_server.py [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--port PORT` | 5020 | Modbus TCP listen port |
| `--web-port PORT` | 8080 | Web dashboard port |
| `--fault-ttl SECONDS` | 8.0 | Auto-recovery time after attacker disconnects |
| `--no-recovery` | off | Disable auto-recovery (elevator stays locked permanently) |
| `--duration SECONDS` | 300 | Total demo runtime before auto-shutdown |

### Permanent Lock Mode (No Auto-Recovery)

```bash
python elevator_server.py --no-recovery
```

Elevators stay in LOCKED_FAULT state permanently after being exploited.
Requires server restart to recover. Use this for dramatic effect.

### Custom Recovery Time

```bash
python elevator_server.py --fault-ttl 15
```

Elevator takes 15 seconds to auto-recover after attacker stops refreshing the fault.

---

## Attacker Client Options

```bash
python attacker_client.py [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host HOST` | 127.0.0.1 | Target server address |
| `--port PORT` | 5020 | Target Modbus TCP port |
| `--target UNIT` | 1 | Target elevator: `1`, `2`, `3`, or `all` |
| `--delay SECONDS` | 2.0 | Pause between attack phases |
| `--persist` | off | Enable persistence (keep re-writing fault) |
| `--persist-duration SEC` | 120 | How long to persist (seconds) |
| `--persist-interval SEC` | 2.0 | Re-write interval during persistence |
| `--recon-only` | off | Run reconnaissance phase only |
| `--flood-only` | off | Run recon + flood phases only |
| `--flood-count N` | 24 | Number of flood commands to send |

---

## Dashboard Features

The web dashboard at `http://localhost:8080` shows:

- **Left Panel**: Elevator status cards (floor, state, fault code, queue depth)
- **Center Panel**: Building cross-section with animated elevator cars
- **Right Panel (top)**: Network topology diagram (SCADA → PLCs, attacker node appears during attack)
- **Right Panel (bottom)**: Real-time event log
- **Bottom Bar**: Attack phase timeline (NORMAL → RECON → FLOOD → EXPLOIT → IMPACT)

Visual effects during attack:
- **RECON**: Scan-line sweeps across the building
- **FLOOD**: Amber overlay on the target shaft, queue bars fill up
- **EXPLOIT/IMPACT**: Elevator car turns red, sparks animation, emergency overlay, LED flickers
- **Recovery**: Everything returns to normal teal theme

---

## Attack Phases Explained

| Phase | Name | What Happens |
|-------|------|-------------|
| 0 | NORMAL | System operating normally |
| 1 | RECON | Attacker scans for PLCs, reads registers (no authentication check) |
| 2 | FLOOD | Attacker floods the command queue with rapid floor requests (OT DoS) |
| 3 | EXPLOIT | Attacker writes fault code 0x10 to the fault register (the "kill shot") |
| 4 | IMPACT | Elevator is locked, passengers trapped, manual reset required |

---

## Recommended Demo Flow for Presentations

1. Start the server: `python elevator_server.py`
2. Open dashboard in browser: `http://localhost:8080`
3. Let the audience see normal elevator operations for ~15 seconds
4. In a second terminal, run: `python attacker_client.py --persist --delay 3`
5. Narrate each phase as it transitions on the dashboard
6. Show the terminal output — explain Modbus/TCP, register writes, lack of auth
7. Press `Ctrl+C` to stop the attacker
8. Watch the auto-recovery happen on the dashboard
9. (Optional) Run cascade: `python attacker_client.py --target all --persist`
10. Discuss: network segmentation, authentication, monitoring

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Make sure `elevator_server.py` is running first |
| Dashboard won't load | Install aiohttp: `pip install aiohttp` |
| No output in attacker terminal | Should be fixed — if still an issue, run with `python -u attacker_client.py` |
| Port already in use | Change ports: `--port 5021 --web-port 8081` |
| Unicode characters broken | Use a terminal with UTF-8 support (Windows Terminal, VS Code terminal) |
