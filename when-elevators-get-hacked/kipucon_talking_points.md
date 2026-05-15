# KipuCon Demo Script — OT Cyber: Elevator Attack
**Sec-Llama | Presenter notes**

---

## Setup (before you go on stage)

```bash
# Terminal 1 — your demo terminal (font size 18+, dark theme)
cd /path/to/elevator_demo

# Terminal 2 (optional) — open the HTML visualization in browser
open kipucon_demo.html
```

Have both visible. Suggested split: slides left (2/3), terminal right (1/3). Or use second monitor.

---

## Slide 1 — Title (90 sec)

> *"Today I want to show you something that will change how you think about what a cyber attack can look like."*

> *"This is not a web app. This is not a database. This is an elevator. A real building. 10 floors. 3 elevators. All controlled by PLCs connected to a network."*

> *"By the end of this demo, one of those elevators will be locked. Passengers trapped. And you will have watched me do it in real time — with a single packet."*

**[Click to slide 2]**

---

## Slide 2 — What is OT? (60 sec)

> *"Most of the security world focuses on IT — servers, APIs, web applications. But there's another network almost nobody talks about: Operational Technology."*

> *"OT is the layer that physically controls your world. The HVAC in this room. The access card reader on that door. The elevator you took to get here. All of it runs on networked PLCs."*

> *"And the protocol tying it all together — Modbus/TCP — was designed in 1979. Before the internet. Before anyone imagined putting these systems on a network with adversaries on it."*

**[Click to slide 3]**

---

## Slide 3 — Architecture (90 sec)

> *"Here's our building's control system. Three layers."*

> *"At the top: the SCADA dispatcher. Think of this as the brain — it polls every elevator every 100 milliseconds, reads their position, and assigns floor calls using a nearest-car algorithm. Exactly like a real building automation system."*

> *"Middle layer: three independent PLC controllers. Each elevator has its own thread, its own state machine, its own command queue with 8 slots."*

> *"Bottom: the physical I/O. Floor sensors, door actuators, and — here's the important one — the fault register. HR4. It's the only writable register in the system. And there is no authentication required to write to it."*

> *"Notice ELV-1 is highlighted in red. That's our target."*

**[Click to slide 4]**

---

## Slide 4 — The Vulnerability (60 sec)

> *"This is the register map. Every field in a PLC controller's memory that SCADA can read."*

> *"Seven read-only registers. One read-write register: HR4, the fault code."*

> *"In a real Siemens or Allen-Bradley deployment, this exact pattern is common. The fault register needs to be writable so maintenance software can clear faults. But it's exposed on the network with no authentication."*

> *"Modbus RFC 6833 — the IETF document that describes the protocol — explicitly says it was never designed for adversarial environments. That's not me criticizing it. That's the protocol's own specification saying: this is not secure. Deploy accordingly."*

> *"Nobody deployed accordingly."*

**[Click to slide 5]**

---

## Slide 5 — Phase 1: Recon  ← START THE DEMO HERE

> *"Okay. Let's run the attack."*

**[Run in terminal:]**
```bash
python elevator_ot_demo.py --attack --attack-delay 15 --duration 90
```

> *"Watch the terminal. You can see the system coming online. Three PLCs, the SCADA dispatcher, the HMI board. Everything is healthy."*

> *"Now — the first thing the attacker does is nothing. Just listen. SCADA is polling every 100ms, broadcasting register values on the network in plaintext. The attacker reads: ELV-1 is on floor 1, queue is empty, fault code is 0x00 — meaning healthy."*

> *"No credentials. No exploit. Just a network tap and a Wireshark window."*

**[Point to terminal output showing the recon phase]**

**[Click to slide 6]**

---

## Slide 6 — Phase 2: Buffer Flood

> *"Phase two: denial of service. Watch ELV-1's command queue on the right."*

**[Watch terminal — buffer flood phase begins ~15s into demo]**

> *"The attacker is sending random floor commands as fast as possible. Floor 7, floor 3, floor 9... the queue fills up."*

> *"Once it's full, you'll see 'CMD BUFFER OVERFLOW — command dropped'. Now watch what happens when SCADA tries to send a real floor call. Rejected. The building's real passengers can't get an elevator."*

> *"But — and this is the important point — no alarm has been raised. The elevator is behaving strangely, but it hasn't faulted. An operator looking at the HMI might think it's just busy."*

**[Click to slide 7]**

---

## Slide 7 — Phase 3: The Kill Shot

> *"Now comes the kill shot."*

**[Watch terminal — attack phase 3]**

> *"One packet. Modbus Function Code 6. Write Single Register. Address: HR4. Value: 0x0010."*

> *"That's it. Six bytes of payload. No session. No authentication. The PLC receives this, sets its internal fault code to 0x10, and transitions to LOCKED_FAULT state."*

> *"There is no recovery path from LOCKED_FAULT. The state machine has no exit transition. The only way to clear this is to physically open the controller cabinet and reset the PLC by hand."*

> *"The elevator is frozen. Doors closed. Wherever it is — between floors, mid-travel — that's where it stays."*

**[Click to slide 8]**

---

## Slide 8 — Impact

> *"Look at the HMI board now."*

> *"ELV-1: LOCKED_FAULT, fault code 0x10. ELV-2 and ELV-3: still running, still serving calls. That's intentional — this is a targeted attack, not a shotgun."*

> *"One elevator down: 33% capacity reduction. Zero log entries from the attack. One packet to do it."*

> *"In a real building — a hospital, an office tower, a shopping mall — this means people stuck. Emergency services potentially delayed. Liability. Panic."*

> *"And the attacker is already gone."*

**[Click to slide 9]**

---

## Slide 9 — Defense (60 sec)

> *"So how do you fix this?"*

> *"Four controls, none of which require replacing the PLC hardware."*

> *"First and most important: network segmentation. Put the PLCs on their own VLAN. A firewall rule that only allows the SCADA server to reach port 502. The attacker on the corporate network can't even see the PLC."*

> *"Second: a Modbus-aware firewall. Products like Claroty or Nozomi Networks inspect packets at the Function Code level. You can say: FC=3 (read registers) is allowed from SCADA. FC=6 (write register) is blocked from everything except the engineering workstation."*

> *"Third: write-protect HR4 at the PLC config level. This is a checkbox in Siemens TIA Portal and Allen-Bradley Studio 5000. It's just not checked by default."*

> *"Fourth: anomaly detection. Real floor calls average 1–3 per minute. 24 per second is detectable without machine learning — it's a threshold rule."*

**[Click to slide 10]**

---

## Slide 10 — Takeaways (45 sec)

> *"Five things I want you to remember."*

> *"OT networks are everywhere and mostly undefended. Your clients have them whether they know it or not."*

> *"Modbus was never designed for security. This isn't a vulnerability you can patch — it's architectural."*

> *"One packet can lock a controller. The escalation from 'weird behavior' to 'full lockout' is a single frame."*

> *"Physical impact is real. This is not a data breach. This is a physical action in the world."*

> *"Defenders need OT-specific tooling. A Palo Alto firewall does not inspect Modbus. Your SIEM does not have Modbus signatures. The tools are different."*

> *"The code for this demo is on my GitHub. Happy to talk more — I do OT penetration testing for mining and industrial clients in LATAM through Sec-Llama."*

---

## Q&A Cheat Sheet

**"Is this a real attack vector?"**
Yes. ICS-CERT has published multiple advisories on unauthenticated Modbus write attacks. The 2021 Oldsmar Water Treatment attack (Florida) used a similar pattern — remote write to a SCADA control register. The Triton/TRISIS malware targeted Schneider Electric safety PLCs with direct register manipulation.

**"Do real elevators use Modbus?"**
Many do, particularly in older buildings. Newer installations may use BACnet/IP or proprietary protocols — but BACnet also lacks authentication by default. The attack surface is the same.

**"What's the hardest part of this attack in practice?"**
Getting initial network access to the OT segment. If the building is properly segmented, you can't reach port 502. Most buildings are not properly segmented. Lateral movement from corporate WiFi or a vendor laptop is the common initial vector.

**"Can the elevator company sue you for showing this?"**
This demo uses a completely simulated system. No real elevators, no real PLCs. It demonstrates publicly documented, well-known weaknesses in a legacy industrial protocol — the same content covered in ICS security courses like SANS ICS515.

**"Does this affect mines and industrial plants?"**
Yes — that's exactly why Sec-Llama focuses on LATAM industrial clients. Mining operations in Peru, Chile, and Colombia run Modbus/TCP on process control networks for crushers, conveyors, and ventilation systems. Same attack surface, much higher physical stakes.

---

## Timing guide (total: ~12 min)

| Section | Time |
|---|---|
| Title + intro | 1.5 min |
| What is OT | 1 min |
| Architecture | 1.5 min |
| Vulnerability | 1 min |
| Live demo (all 3 phases) | 3 min |
| Impact | 1 min |
| Defense | 1 min |
| Takeaways | 1 min |
| Buffer | 1 min |

---

*Sec-Llama — KipuCon — Lima, Peru*
