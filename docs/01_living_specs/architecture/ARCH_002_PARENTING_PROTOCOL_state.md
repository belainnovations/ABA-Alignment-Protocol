# State: The Parenting Protocol

| Metadata | Details |
| :--- | :--- |
| **Definition Document** | [ARCH_002_PARENTING_PROTOCOL.md](./ARCH_002_PARENTING_PROTOCOL.md) |
| **Last Updated** | 2026-02-05 |
| **Status** | ACTIVE |

---

## 1. Status Summary
The architecture is defined and agreed upon. We are currently in **Stage I: Teacher Certification**.

### Current Focus
*   **Goal:** Create **Model A** (The Teacher).
*   **Method:** DPO Fine-tuning via Unsloth on RTX 5070 Ti (16GB VRAM).
*   **Status:** Data prepared (800/100/100 splits), environment verified, ready for training script.
*   **Blockers:** None.

---

## 2. Implementation History

| Date | Agent | Event |
|---|---|---|
| 2026-02-04 | Antigravity | **Requirements Definition.** Created `ARCH-002`. Defined the Triad (Architect, Child, Teacher) and the VRAM mitigation strategy. |
| 2026-02-04 | Antigravity | **Strategy Update.** Shifted project focus from "Safety Model" to "Parenting Infrastructure" (RLAIF). |
| 2026-02-05 | Claude Opus 4.5 | **Phase 3.1 Complete.** Created train/val/test splits (800/100/100) in `data/splits/`. DPO format verified. |
| 2026-02-05 | Claude Opus 4.5 | **Phase 3.2 Complete.** Environment verified: PyTorch 2.11.0+cu128 nightly for RTX 5070 Ti Blackwell (sm_120). Unsloth + TRL operational. |

---

## 3. Pending Implementation Tasks

### Stage I (Teacher)
- [x] Generate Full ABA Dataset (1k items) via `rewrite.py`. **(DONE: 2026-02-04)**
- [x] Fine-Tune Model A (Unsloth).
- [x] Verify Model A (Protocol Adherence >95%) -> **FAILED (58% Refusal). Pivot to Phase 3b.**

### Stage Ib (Apples-to-Apples Experiment)
- [ ] Train Model A_Native (Uncensored Base).
- [ ] Compare Teachers (Repair vs Native).

### Stage II (Sandbox)
- [ ] Implement `architect.py` (Scenario Generator).
- [ ] Generate 100k Scenarios.

### Stage III (Parenting)
- [ ] Implement RLAIF Training Loop (`parenting_loop.py`).
- [ ] Implement RLAIF Training Loop (`parenting_loop.py`).
- [x] **Design Finalized:** Iterative Batching + Watchdog (ARCH-002 Stage VI).
