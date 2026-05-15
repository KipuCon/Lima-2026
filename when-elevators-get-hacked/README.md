# When Elevators Get Hacked

**One packet. One register. One elevator locked. Passengers trapped.**

An end-to-end simulation of a targeted OT/ICS attack against a building's elevator control system — PLCs, a SCADA dispatcher, a Modbus-style TCP protocol, and a live web dashboard you can project on stage. Built for the [KipuCon](https://kipucon.pe/) talk *"When Elevators Get Hacked"* by **Sec-Llama**.

No real elevators were harmed. Every vulnerability shown is publicly documented and applies to legacy Modbus/TCP deployments in real buildings, hospitals, and industrial plants today.

---

## Why this exists

Most of the security world looks at web apps and APIs. Meanwhile, the systems that physically move the world — elevators, HVAC, access control, factory floors — sit on 1979-era protocols that were never designed for adversarial networks.

This repo lets you **watch that gap exploited in real time**, on your laptop, in about 30 seconds.

---

## Quick start

```bash
pip install aiohttp

# Terminal 1 — start the building
python elevator_server.py

# Terminal 2 — run the attack
python attacker_client.py --persist --delay 3
```

Open <http://localhost:8080> in your browser. Watch ELV-1 get locked. Press `Ctrl+C` on the attacker to release it.

Full command reference and every attack variant (recon only, flood only, cascade all elevators, etc.) is in **[USAGE_GUIDE.md](USAGE_GUIDE.md)**.

---

## What's in this repo

| Path | What it is |
|---|---|
| `elevator_server.py` | 3 PLCs + SCADA dispatcher + Modbus TCP server + web dashboard |
| `attacker_client.py` | Red-team client: recon → flood → exploit → persist |
| `ot_protocol.py` | Shared Modbus-style protocol (function codes, register map) |
| `dashboard.html` | The live dashboard the server hosts at :8080 |
| `USAGE_GUIDE.md` | Full command reference and CLI flags |
| `kipucon_talking_points.md` | Presenter notes, slide-by-slide script, Q&A cheat sheet |
| `Presentation/*.pdf` | Slide decks (English + Spanish) |

---

## The attack, in four phases

| Phase | What the attacker does | What the audience sees |
|---|---|---|
| **RECON** | Reads registers on every unit. No auth required. | Scan-line sweeps across the building |
| **FLOOD** | Sends 24 rapid floor commands per second to overflow the 8-slot queue | Amber overlay, queue bars fill, legitimate calls rejected |
| **EXPLOIT** | Writes `0x10` to fault register `HR4` — six bytes, one packet | Car turns red, sparks, LED flickers |
| **IMPACT** | `LOCKED_FAULT` state. No recovery path in the state machine. | Emergency overlay, passengers trapped |

The full walkthrough (with the narration used on stage) is in [`kipucon_talking_points.md`](kipucon_talking_points.md).

---

## The defense section

Four controls, none of which require replacing the PLC:

1. **Network segmentation** — PLCs on their own VLAN. Firewall rule: only the SCADA server reaches port 502.
2. **Modbus-aware firewall** — Claroty, Nozomi, etc. inspect at the Function Code level. Allow FC=3 (read) from SCADA; block FC=6 (write) from everything except the engineering workstation.
3. **Write-protect fault registers** — a checkbox in Siemens TIA Portal and Allen-Bradley Studio 5000. Just not checked by default.
4. **Anomaly detection** — real floor calls average 1–3 per minute. 24 per second is a threshold rule, not ML.

---

## Slides & video

- **Slides:** [`Presentation/KipuCon_OT_Talk_v5.pdf`](Presentation/KipuCon_OT_Talk_v5.pdf) · [Español](<Presentation/KipuCon_OT_Talk_v5 - ES.pdf>)
- **Demo videos:** [YouTube playlist](#) *(link pending — upload to YouTube and paste URL here)*

The raw `.pptx` and `.mp4` source files are kept out of Git (GitHub's 100 MB file limit) — ask Sec-Llama if you need them.

---

## Disclaimer

This is a **simulated** OT stack. It does not talk to real PLCs, does not implement the full Modbus spec, and is not a pentesting tool. The weaknesses demonstrated — unauthenticated register writes, command-queue DoS, writable fault registers — are architectural properties of legacy ICS deployments and are covered in public ICS security curricula (SANS ICS515, ICS-CERT advisories, the Triton/TRISIS case studies).

Use it to teach. Use it to convince a CISO that OT is on fire. Don't point it at anything you don't own.

---

## About Sec-Llama

Sec-Llama does OT penetration testing for mining and industrial clients in LATAM. If your building, plant, or mine runs Modbus/TCP, BACnet, or proprietary fieldbus on a network anyone can reach — we should talk.
