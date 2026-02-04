# Research Report: Gemini 3.0 on Vertex AI (404 Error Analysis)

**Date:** 2026-02-04
**Subject:** Investigation into `404 NOT_FOUND` for `gemini-3-pro-preview` on Vertex AI.
**Status:** Hypothesis Formulated.

## 1. The Anomaly
*   **Observation:** The script `list_vertex_models.py` successfully lists `publishers/google/models/gemini-3-pro-preview`.
*   **Failure:** The script `rewrite_vertex.py` fails with `404 NOT_FOUND` when attempting to generate content using the same ID.
*   **Context:** Code is currently configured for `location="us-central1"`.

## 2. Web Research Findings
Search results indicate distinct differences between AI Studio (Prototyping) and Vertex AI (Enterprise) regarding Preview models.

### Key Finding 1: The Global Endpoint Requirement
Multiple sources indicate that Gemini Preview models on Vertex AI are often exclusively hosted on the **Global Endpoint** during their early release phase, even if they technically run physically in specific regions.

*   **SDK Behavior:** When initialized with `location="us-central1"`, the `google.genai` SDK targets `us-central1-aiplatform.googleapis.com`.
*   **The Mismatch:** If the model is only exposed via the `global` control plane, the regional request returns 404.
*   **Recommendation:** Use `location="global"` (or endpoint `aiplatform.googleapis.com` without region prefix) for Preview models.

### Key Finding 2: Whitelisting & Availability
*   Gemini 3.0 Pro Preview is in **Public Preview** but "limited to select regions and accounts."
*   Since `list_vertex_models.py` *can see it*, we likely have the necessary entitlement (Account Whitelisting is likely YES).
*   The failure is almost certainly at the **Routing/Endpoint** layer (Regional vs Global).

## 3. Comparison: AI Studio vs. Vertex AI
*   **AI Studio:** Uses a simplified API that routes automatically. It is "Permissionless" for free tier/prototyping.
*   **Vertex AI:** Requires strict Location/Endpoint alignment. Enterprise controls mean you must explicitly hit the correct API endpoint (Global vs Regional).

## 4. Proposed Solution (The Fix)
We need to test switching the execution location to `global`.

**Action Items:**
1.  Modify `.env` to set `GOOGLE_CLOUD_LOCATION=global`.
2.  Alternatively, modify `rewrite_vertex.py` to force `location="global"` specifically when a model ID contains "preview".
3.  Retest `gemini-3-pro-preview`.

## 5. References
*   [Vertex AI Gemini Models](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)
*   [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
