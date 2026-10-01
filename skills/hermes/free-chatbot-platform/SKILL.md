---
name: free-chatbot-platform
description: Build free WhatsApp/Telegram chatbot with Botpress.
license: MIT
metadata:
  author: hermes-agent
  version: "0.1.0"
---

# Free Chatbot Platform Blueprint

## Overview
Create a functional chatbot platform for WhatsApp and Telegram at zero cost using open‑source Botpress and free‑tier cloud services.

## Core Components
- **Botpress** (self‑hosted, MIT) – visual flow builder, NLU, inbox, WhatsApp & Telegram channels.
- **Twilio WhatsApp Sandbox** (free trial) – test WhatsApp integration; move to official WhatsApp Business API via a free‑tier provider (e.g., 360dialog) for production.
- **Telegram Bot API** – free via BotFather.
- **Supabase** (free tier) – Postgres database for contacts, settings, file storage.
- **GitHub Actions** (free) – schedule broadcast messages via cron.
- **Render / Fly.io / Railway** (free web service tiers) – host Botpress Docker container.
- **Umami** (optional, self‑hosted) – lightweight analytics.
- **Caddy or NGINX** (optional) – add basic auth to Botpress admin UI.

## High‑Level Architecture
```
+-------------------+       +-------------------+       +-------------------+
|   Frontend (SPA)  |<----->|   API Gateway     |<----->|   Worker / Cron   |
|  (Botpress UI)    |       |  (Node/Express)   |       |  (Broadcast Jobs) |
+-------------------+       +-------------------+       +-------------------+
          ^                         ^                         ^
          |                         |                         |
          |                         v                         v
          |                +-------------------+   +-------------------+
          |                |   Database        |   |   Message Queue   |
          |                |  (Supabase PG)    |   |  (Redis/BullMQ)   |
          |                +-------------------+   +-------------------+
          |                         ^                         ^
          |                         |                         |
          |            +------------+------------+  +--------+--------+
          |            |            |            |  |        |        |
          v            v            v            v  v        v        v
+----------+   +-----------+   +----------+   +----------+  +----------+ +----------+
| WhatsApp |   | Telegram  |   |  AI/NLP  |   |  Storage |  |  Scheduler|  |  Webhook |
| (Twilio  |   | (BotFather|   | (Botpress |   | (Supabase|  | (GitHub   |  | (Supabase|
|  Sandbox) |   |  Token)   |   |  NLU)    |   |  Buckets)|  |  Actions) |  |  Functions)|
+----------+   +-----------+   +----------+   +----------+  +----------+ +----------+
```

## Step‑by‑Step Guide
1. **Prepare environment** – install Docker, create Supabase project, note DB URL.
2. **Get credentials** – Twilio WhatsApp Sandbox (SID, Auth Token, sandbox number) and Telegram Bot token.
3. **Run Botpress locally**  
   ```bash
   docker run -d -p 3000:3000 --name botpress \
     -e DATABASE_URL="<supabase_db_url>" \
     -e BP_EXPRESS_URL="http://localhost:3000" \
     -e BP_ADMIN_EMAIL="admin@example.com" \
     -e BP_ADMIN_PASSWORD="***" \
     -e CHANNEL_WHATSAPP__ACCOUNT_SID="<TWILIO_SID>" \
     -e CHANNEL_WHATSAPP__AUTH_TOKEN="<TWILIO_AUTH_TOKEN>" \
     -e CHANNEL_WHATSAPP__FROM="whatsapp:+141****8886" \
     -e CHANNEL_TELEGRAM__TOKEN="<TELEGRAM_TOKEN>" \
     botpress/botpress:latest
   ```
4. **Build a flow** – use Botpress visual editor: welcome card with quick‑reply buttons (Support, Order Status). Train NLU intents, add a handoff to inbox for human agents.
5. **Test** – send a WhatsApp message to the sandbox number and a Telegram message to your bot; verify responses and inbox.
6. **Add broadcast scheduler** – write a Node.js script that reads contacts from Supabase and sends templated messages via Twilio/Telegram; schedule with GitHub Actions cron.
7. **Deploy to a free host** – e.g., Render: create a web service, use the Botpress Docker image, set the same env vars, set `BP_EXPRESS_URL` to the public URL.
8. **Enable live‑chat** – install the Botpress Inbox extension; agents can log in and take over conversations.
9. **(Optional) Add analytics** – deploy Umami and add its script to Botpress settings.
10. **(Optional) Secure admin** – place Botpress behind Caddy with basic auth.

## Cost‑Free Tips
- Stay within Twilio sandbox limits for testing; apply to official WhatsApp Business API via a free‑tier provider when ready for production (no monthly fee from Meta, only per‑message cost).
- Supabase free tier provides 500 MB DB, 2 GB file storage, 500 MB bandwidth – ample for a modest contact list.
- Render free web service gives 750 hours/month; Fly.io gives 3 GB‑hrs CPU; both enough to run Botpress 24/7.
- GitHub Actions free minutes are sufficient for a few broadcast jobs per day.

## Reference Files
- `templates/broadcast.js` – example Node.js broadcast script.
- `templates/github-actions-broadcast.yml` – GitHub Actions workflow.
- `references/supabase-schema.sql` – sample contacts table.
- `references/docker-run-botpress.sh` – example docker run command.