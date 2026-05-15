<div align="center">

<img src="https://kipucon.org/KipuCon.svg" alt="KipuCon" width="160"/>

# Lo que un hacker ve y tu empresa no

**KipuCon Lima 2026** &nbsp;·&nbsp; Omri Nuri, Web Red Team Lead — [Sec-Llama](https://secllama.com)

</div>

---

## About

A talk for C-level executives and decision makers about the most common web vulnerabilities affecting Latin American companies — demonstrated live with a fictional but realistic application.

The four acts are based on real publicly reported incidents:

| Act | Vulnerability | Incident |
|-----|--------------|---------|
| 1 | Unauthenticated REST API (IDOR) | ONPE 2018, MEF 2025 |
| 2 | IDOR with Base64 "encoding" | RENIEC Padrón Nominal 2018 |
| 3 | Broken Authentication | MercadoPago OAuth 2018 |
| 4 | Automated exploitation | All of the above, at scale |

---

## Slides

→ [`slides/lo-que-un-hacker-ve.pptx`](./slides/lo-que-un-hacker-ve.pptx)

---

## Demo App

A self-contained vulnerable web app that simulates all four acts. Runs locally with Docker.

```bash
cd demo
docker compose up
```

Then open [http://localhost:3333](http://localhost:3333).

### Recording the demo videos

The demo ships with Playwright tests that produce the backup videos shown during the talk:

```bash
cd demo/e2e
npm install
npx playwright install chromium
npx playwright test --reporter=html
```

Videos are saved to `demo/backup-videos/`. They are not committed to this repo due to size.

---

<div align="center">

[kipucon.org](https://kipucon.org) &nbsp;·&nbsp; Lima, Peru &nbsp;·&nbsp; 2026

</div>
