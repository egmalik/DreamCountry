# Prompt: WhatsApp Personal Agent — copy everything below into a new session in Plan Mode

---

I want you to design (and later build) a **personal AI agent connected to my WhatsApp**. It is **not** a general auto-responder. It is a command-driven assistant with three hard rules:

1. **It only ever sends messages into 2 target channels** (WhatsApp chats/groups) that I configure. Nothing else, ever.
2. **It only acts when I trigger it** — it never responds to incoming messages on its own. Triggers come exclusively from a **dedicated control channel** between me and the agent.
3. **It works through skills** — named, self-contained capabilities. We launch with exactly **one skill**: "What is the studying plan until next class." More skills come later, so the skill system must be pluggable from day one.

You are in plan mode: produce a complete implementation plan first, ask me the open questions at the end, and do not write code until I approve the plan.

## 1. Core interaction model

```
Me ──(command)──► Control Channel ──► Agent ──(runs skill, grounded in KB)──► Target Channel 1 or 2
                                        │
                                        └──(confirmation / result back to me in Control Channel)
```

- **Control channel**: one dedicated WhatsApp chat between me and the agent (my self-chat, or a chat with the agent's number — recommend which, based on the integration route). Commands from **my WhatsApp ID only**; messages from anyone else in any chat are ignored and logged, never acted on.
- **Target channels**: exactly 2 chats/groups, defined by chat ID in config. The send layer must **hard-enforce** this allowlist — the check lives in the WhatsApp adapter itself, so no skill or LLM output can ever cause a send anywhere else.
- **Trigger-only operation**: the agent is idle until I issue a command. Incoming messages in target channels may be *read and stored as context* (e.g., to know when the next class is announced), but never replied to autonomously.
- Every action ends with a short report back to me in the control channel: what was sent, where, or why it failed.

## 2. Command interface (control channel)

Design a small, forgiving command grammar — I'll type these on my phone, so natural phrasing should work, e.g.:

- `study plan` → run the studying-plan skill and show me the draft
- `send to <channel-1|channel-2>` → send the last approved draft to that target channel
- `preview` / `cancel` / `status` / `pause` / `resume`
- `help` → list available skills and commands

Parse commands with the LLM (intent classification) but keep the **actions** deterministic: the LLM decides *which* command I meant, code decides *what happens*. Default flow is **draft → I confirm → send**; direct-send only if I explicitly say so in the command.

## 3. Skill system

- A skill is a self-contained module with a manifest: name, trigger phrases, which KB files it reads, which target channel(s) it may address, and its output template.
- Skills directory layout, e.g.:

```
skills/
  study-plan/
    skill.yaml        # manifest: name, triggers, allowed channels, KB inputs
    prompt.md         # the skill's own LLM instructions
```

- **Skill #1 — "What is the studying plan until next class"**: given today's date, the class schedule, and the syllabus/plan in the KB, produce a clear message listing what to study between now and the next class. We'll refine this skill's logic later — for now the plan just needs the skill scaffold, its KB inputs, and a working end-to-end pass with placeholder logic.
- Adding a future skill must mean: add a folder, restart, done. No core-code changes.

## 4. Grounding knowledge base (I author the content; you design the structure)

All skill output must be grounded in a human-editable KB. Proposed layout — refine it in your plan:

```
knowledge/
  persona.md          # my name, tone, languages, sign-off style
  channels.yaml       # control channel ID + the 2 target channel IDs and their purpose
  study/
    schedule.md       # class days/times, next-class date
    syllabus.md       # topics per class / week
    plan.md           # the studying plan source material
  policies.md         # hard rules: what never to send, when to just ask me
```

- **Strict grounding rule**: every factual claim in an outgoing message must trace to a KB file. If the KB can't answer (e.g., next class date missing), the agent tells me what's missing in the control channel instead of guessing.
- Retrieval: the KB is small — load relevant files whole into context per skill manifest. No embeddings/vector store in v1; justify if you disagree.

## 5. WhatsApp connectivity

- Evaluate the two realistic routes and recommend one, trade-offs stated plainly:
  - **WhatsApp Business Cloud API (official)** — ToS-safe, needs a separate business number; the control channel is then simply my chat with that number. Note: group messaging support is limited — verify whether the 2 target channels can be groups under this route.
  - **Device-linking libraries (Baileys / whatsapp-web.js)** — pairs with an existing number via QR, full group support, but unofficial with account-ban risk. Our design is inherently low-risk (only-when-triggered, 2 channels, low volume, human-like pacing) — state the residual risk anyway.
- If the target channels are WhatsApp **groups**, that likely decides the route — make this the first question you ask me.
- Session must survive restarts and re-authenticate without losing state.

## 6. Control & safety (non-negotiable)

- **Sender authentication**: commands accepted only from my WhatsApp ID, checked in code.
- **Channel allowlist enforced in the adapter** (defense in depth — not just in prompts).
- **Confirm-before-send** as default; `pause` as kill switch; rate cap (a handful of messages/day is the expected volume).
- **Audit log**: every command, draft, confirmation, and send logged to disk.
- Secrets in `.env`, never committed.

## 7. Architecture & code quality

- Layered structure, e.g.: `channel/` (WhatsApp adapter + allowlist), `commands/` (parsing + dispatch), `skills/` (pluggable modules), `knowledge/` (KB loader + validation), `store/` (context memory, audit log — SQLite), `config/`.
- TypeScript (Node.js) preferred unless you argue convincingly otherwise.
- Tests for: command parsing, sender authentication, channel-allowlist enforcement, KB validation, and the study-plan skill with a mocked LLM.
- Runs locally first (my machine or small VPS + Docker); no cloud complexity in v1.

## 8. Phased delivery (structure the plan this way)

1. **Phase 1 — Connection & control channel**: WhatsApp connected; agent hears my commands in the control channel, ignores everything else, replies with `status`/`help`.
2. **Phase 2 — Skill scaffold + send path**: skill system in place; study-plan skill returns a grounded draft from the KB; confirm-then-send into a target channel works; allowlist and audit log enforced.
3. **Phase 3 — Polish skill #1**: refine the studying-plan logic together (this is where "we work on this skill later" happens), better date handling, formatting, KB update workflow.
4. **Phase 4 — Later**: additional skills, scheduled triggers (e.g., auto-draft every Sunday for my confirmation), voice-command support.

Each phase ends with something I can run and test myself, with setup instructions.

## 9. What the plan must contain before any code

- Recommended WhatsApp route (driven by whether target channels are groups) with explicit risk statement.
- Final tech stack and directory tree.
- The command grammar and the exact confirm-before-send flow.
- Skill manifest format, with the study-plan skill's manifest written out as the concrete example.
- KB file formats with realistic example content for `schedule.md`, `syllabus.md`, `plan.md`.
- Sequence walkthrough of one full interaction: my command → parse → skill → draft → my confirmation → send → report.
- Test strategy and how I update the KB day to day.

## 10. Questions to ask me before finalizing the plan

1. Are the 2 target channels **groups or individual chats**? (This decides the WhatsApp route.)
2. Do I already have a second number I can dedicate to the agent, or must it run on my personal number?
3. For the study-plan skill: where does the class schedule live today (paper, calendar, chat messages)? Who updates it, and how often does it change?
4. What language(s) should the study-plan message be written in?
5. Should the agent read messages in the 2 target channels as context (e.g., teacher announces next class), or treat them as write-only?
