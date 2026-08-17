# Prompt: WhatsApp Personal Agent — copy everything below into a new session in Plan Mode

---

I want you to design (and later build) a **personal AI agent connected to my WhatsApp** that can read incoming messages and **send messages on my behalf**, with all its replies grounded in a **structured knowledge base that I maintain**. You are in plan mode: produce a complete implementation plan first, ask me the open questions listed at the end, and do not write code until I approve the plan.

## 1. What the system is

A single, well-structured service ("the agent") that:

1. **Connects to my personal WhatsApp account** — receives incoming messages in real time and can send outgoing messages.
2. **Acts as me (or clearly as my assistant)** — drafts and sends replies in my tone and style.
3. **Answers only from a grounding knowledge base** — a folder of structured files I write and update. If the answer is not in the knowledge base, the agent must say it doesn't know (or escalate to me), never invent facts.
4. **Keeps me in control** — configurable per-contact behavior: auto-reply, draft-for-my-approval, or ignore.

## 2. Functional requirements

### WhatsApp connectivity
- Evaluate the two realistic integration routes and recommend one, with trade-offs stated plainly:
  - **WhatsApp Business Cloud API (Meta official)** — reliable and ToS-safe, but requires a business number and message templates for outbound-initiated chats.
  - **Device-linking libraries (e.g. Baileys / whatsapp-web.js)** — works with my existing personal number via QR pairing, but is unofficial and carries a ban risk that the plan must state explicitly and mitigate (rate limits, human-like send pacing, no bulk sending).
- Support: text in/out at minimum; voice-note transcription and image understanding as a stretch phase.
- Reconnection handling: the session must survive restarts and re-authenticate without losing state.

### Agent brain
- Use the Claude API (latest model) as the reasoning engine, with an agentic loop: classify the incoming message → retrieve relevant knowledge → draft reply → apply guardrails → send or queue for approval.
- **Persona config**: a `persona.md` file defining my name, tone, languages I reply in, sign-off style, and topics I never discuss.
- **Conversation memory**: per-contact conversation history (rolling window + summary) stored locally so replies have context.

### Grounding knowledge base (I will author the content; you design the structure)
Design a clean, human-editable KB layout, for example:

```
knowledge/
  persona.md            # who I am, tone, style, boundaries
  contacts.yaml         # per-contact rules: auto / approve / ignore, language, relationship
  facts/                # topic files the agent may quote from
    business.md
    pricing.md
    availability.md
    faq.md
  policies.md           # hard rules: what never to say, when to escalate to me
```

- Retrieval: start simple (load whole KB into context if it fits; chunk + embed only if it grows). Justify the choice in the plan.
- **Strict grounding rule** in the system prompt: every factual claim must trace to a KB file; otherwise reply "I'll get back to you" and notify me.

### Control & safety (non-negotiable)
- **Approval workflow**: by default every outgoing message is a draft I approve (via a simple channel — CLI, small web dashboard, or a WhatsApp "self-chat" with approve/reject commands — recommend one). Auto-send only for contacts/topics I explicitly whitelist in `contacts.yaml`.
- **Kill switch**: one command to pause all sending instantly.
- **Rate limiting & pacing**: cap messages per hour, add human-like delays.
- **Audit log**: every received message, retrieval result, draft, decision (auto/approved/rejected), and sent message logged to disk.
- **No mass messaging**: the agent only replies to inbound messages or sends one-off messages I explicitly dictate; it must refuse bulk/broadcast behavior by design.
- Secrets (API keys, session credentials) in `.env`, never committed.

## 3. Architecture & code quality requirements

- Propose a clean layered structure, e.g.:
  - `channel/` — WhatsApp adapter (swappable, so Cloud API vs Baileys is one interface)
  - `agent/` — LLM orchestration, prompt assembly, guardrails
  - `knowledge/` — KB loader, retrieval, validation of KB file formats
  - `approval/` — draft queue + approval interface
  - `store/` — conversation history, audit log (SQLite is fine)
  - `config/` — typed config loading
- TypeScript (Node.js) preferred unless you argue convincingly for Python.
- Tests for: KB parsing/validation, guardrail decisions (auto vs approve vs ignore), and the grounding rule (mock LLM).
- Runnable locally first (my machine or a small VPS + Docker); no cloud complexity in v1.

## 4. Phased delivery (structure the plan this way)

1. **Phase 1 — Skeleton & echo**: WhatsApp connection working, incoming messages logged, manual send from CLI works.
2. **Phase 2 — Grounded drafts**: KB loading + Claude drafting + approval queue; nothing auto-sends.
3. **Phase 3 — Controlled autonomy**: per-contact auto-reply rules, rate limits, kill switch, audit log complete.
4. **Phase 4 — Stretch**: voice-note transcription, media understanding, scheduled/reminder messages, simple web dashboard.

Each phase must end with something I can run and test myself, with setup instructions.

## 5. What the plan must contain before any code

- Recommended WhatsApp integration route with explicit risk statement.
- Final tech stack and project directory tree.
- KB file formats with concrete example content for each file.
- The agent's system-prompt design (grounding rule, persona injection, escalation behavior).
- Sequence diagram (text is fine) of one message's journey: inbound → retrieval → draft → approval → send.
- Test strategy and how I do day-to-day KB updates.

## 6. Questions to ask me before finalizing the plan

1. Is this for my **personal number** or can I dedicate a separate/business number to the agent?
2. Which languages must the agent handle?
3. Default posture: approve-everything first, or auto-reply for some contacts from day one?
4. Where will it run — my computer, or a small server?
5. What are the first 3 real use cases (e.g., business FAQs, availability, appointment requests)?
