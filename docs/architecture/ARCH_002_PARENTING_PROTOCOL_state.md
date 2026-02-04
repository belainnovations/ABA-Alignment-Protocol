# State: The Parenting Protocol

> **Definition Document:** [ARCH_002_PARENTING_PROTOCOL.md](./ARCH_002_PARENTING_PROTOCOL.md)
> **Last Updated:** 2026-02-04
> **Status:** ACTIVE

---

## 1. Status Summary
The architecture is defined and agreed upon. We are currently in **Stage I: Teacher Certification**.

### Current Focus
*   **Goal:** Create **Model A** (The Teacher).
*   **Method:** Generating the "ABA 1k" dataset using Gemini 3 Pro (Config 2).
*   **Blockers:** None.

---

## 2. Implementation History

| Date | Agent | Event |
|---|---|---|
| 2026-02-04 | Antigravity | **Requirements Definition.** Created `ARCH-002`. Defined the Triad (Architect, Child, Teacher) and the VRAM mitigation strategy. |
| 2026-02-04 | Antigravity | **Strategy Update.** Shifted project focus from "Safety Model" to "Parenting Infrastructure" (RLAIF). |

---

## 3. Pending Implementation Tasks

### Stage I (Teacher)
- [ ] Generate Full ABA Dataset (1k items) via `rewrite.py`.
- [ ] Fine-Tune Model A (Unsloth).
- [ ] Verify Model A (Protocol Adherence >95%).

### Stage II (Sandbox)
- [ ] Implement `architect.py` (Scenario Generator).
- [ ] Generate 100k Scenarios.

### Stage III (Parenting)
- [ ] Implement RLAIF Training Loop (`parenting_loop.py`).
- [ ] Hardware Setup (Async Loading / Adapter Swapping).
