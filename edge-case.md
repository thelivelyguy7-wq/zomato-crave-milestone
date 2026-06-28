# Edge Cases & Corner Scenarios

> AI-Powered Restaurant Recommendation System (Zomato Use Case)  
> Companion to [context.md](./context.md), [architecture.md](./architecture.md), and [implementation-plan.md](./implementation-plan.md)

This document catalogs corner scenarios across the full pipeline — from dataset load through Groq LLM output and UI display. Each entry describes the scenario, affected component, expected behavior, and test priority.

**Priority legend:** 🔴 Critical · 🟠 High · 🟡 Medium · 🟢 Low

---

## Summary Matrix

| Category | Count | Primary owner module |
|----------|-------|----------------------|
| Data ingestion & dataset | 18 | `src/data/loader.py` |
| User input & validation | 16 | `src/models/preferences.py`, UI |
| Filtering | 14 | `src/services/filter.py` |
| Groq / LLM integration | 15 | `src/services/llm/groq_client.py` |
| Prompt & response parsing | 12 | `src/services/prompt_builder.py`, `recommendation.py` |
| Recommendation orchestration | 10 | `src/services/recommendation.py` |
| UI (Streamlit) | 12 | `src/ui/streamlit_app.py` |
| API (optional FastAPI) | 8 | `src/api/main.py` |
| Configuration & environment | 9 | `src/config.py` |
| Performance & concurrency | 7 | cross-cutting |
| Security | 8 | cross-cutting |

---

## 1. Data Ingestion & Dataset

### 1.1 Loading & connectivity

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| D-01 | Hugging Face unreachable (no network, DNS failure) | Fail fast at startup with clear message: "Could not download dataset. Check network or use cached Parquet." | 🔴 |
| D-02 | Hugging Face dataset renamed, moved, or deleted | Catch load error; document fallback to local Parquet if present | 🔴 |
| D-03 | Hugging Face rate limit or timeout during download | Retry with backoff (2–3 attempts); then fail with actionable error | 🟠 |
| D-04 | Cached `data/restaurants.parquet` exists and is valid | Skip Hugging Face download; load from cache | 🟡 |
| D-05 | Cached Parquet exists but is corrupted / unreadable | Log warning; re-download from Hugging Face | 🟠 |
| D-06 | Cached Parquet is stale (schema changed in loader) | Version stamp in Parquet metadata; invalidate and rebuild on mismatch | 🟡 |
| D-07 | First load on slow connection (large dataset) | Show loading indicator in UI; log progress | 🟡 |

### 1.2 Schema & field mapping

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| D-08 | Column names differ from expected (e.g. `rate` vs `rating`) | Explicit column map in `loader.py`; fail with list of missing required columns | 🔴 |
| D-09 | Required column entirely missing from dataset | Fail fast with column name in error message | 🔴 |
| D-10 | Extra/unused columns in dataset | Ignore safely; no crash | 🟢 |
| D-11 | Dataset split has multiple configs (train/test) | Load correct split explicitly; document which split is used | 🟡 |

### 1.3 Data quality & normalization

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| D-12 | Restaurant `name` is null or empty string | Skip row or assign placeholder; log count of skipped rows | 🟠 |
| D-13 | `rating` is null, `"-"`, `"NEW"`, or non-numeric | Parse to `0.0` or exclude from rating filter; document rule | 🟠 |
| D-14 | `rating` out of range (e.g. 6.0, negative) | Clamp to [0, 5] or exclude; log anomaly | 🟡 |
| D-15 | `cost_for_two` is a range string (e.g. `"300-500"`, `"₹500"`) | Parse to numeric (use midpoint or lower bound); strip currency symbols | 🔴 |
| D-16 | `cost_for_two` is null or zero | Assign default tier or exclude from budget filter | 🟠 |
| D-17 | `location` has inconsistent casing (`"bangalore"`, `"Bangalore"`, `"BANGALORE"`) | Normalize to title case or canonical form at load time | 🟠 |
| D-18 | `location` contains locality + city (e.g. `"Indiranagar, Bangalore"`) | Preserve full string; filter matches city substring case-insensitively | 🟡 |
| D-19 | `cuisine` is comma-separated multi-value (`"North Indian, Chinese"`) | Store as-is; filter matches if any token contains query | 🟠 |
| D-20 | Duplicate restaurant rows (same name + location) | Assign unique `id` per row; do not dedupe unless business rule defined | 🟡 |
| D-21 | Duplicate `id` values after assignment | Regenerate IDs; ensure uniqueness before repository build | 🔴 |
| D-22 | Very long `name` or `address` fields | Truncate for display only; keep full value in model | 🟢 |
| D-23 | Special characters in names (Unicode, emoji, apostrophes) | Preserve UTF-8; no encoding errors on load or display | 🟡 |
| D-24 | Budget tier thresholds misaligned with actual cost distribution | Calibrate tiers from dataset percentiles during Phase 1; document thresholds | 🟠 |
| D-25 | Empty dataset after preprocessing (all rows dropped) | Fail startup: "No valid restaurants loaded" | 🔴 |

---

## 2. User Input & Validation

### 2.1 Required fields

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| U-01 | `location` is empty string or whitespace only | Validation error before filter/LLM: "Location is required" | 🔴 |
| U-02 | `budget` not provided | Validation error: "Budget is required" | 🔴 |
| U-03 | `budget` value outside enum (`"cheap"`, `"Medium"`, invalid) | Reject with allowed values: `low`, `medium`, `high` | 🔴 |
| U-04 | Form submitted with no interaction (Streamlit defaults) | Use sensible defaults only if documented; location/budget still required | 🟡 |

### 2.2 Optional fields

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| U-05 | `cuisine` omitted or empty | Treat as "any cuisine" — skip cuisine filter | 🟡 |
| U-06 | `cuisine` set to value not in dataset (e.g. `"Mexican"` when none exist) | Filter returns empty → empty state message (not an error) | 🟠 |
| U-07 | `min_rating` omitted | Default to `0.0` (no rating filter) | 🟡 |
| U-08 | `min_rating` = 5.0 | Only restaurants with rating exactly 5.0 (likely very few or zero) | 🟡 |
| U-09 | `min_rating` negative or > 5.0 | Validation error: must be in [0, 5] | 🔴 |
| U-10 | `min_rating` non-numeric (API JSON: `"four"`) | Pydantic validation error with 422 (API) or UI message | 🟠 |
| U-11 | `additional_preferences` omitted or empty | Omit from prompt or pass `"none"` | 🟢 |
| U-12 | `additional_preferences` very long (> 500 chars) | Truncate to 500 chars before prompt; no crash | 🟠 |
| U-13 | `additional_preferences` contains HTML/script tags | Strip tags; sanitize before prompt | 🟠 |
| U-14 | `additional_preferences` contains prompt injection ("ignore rules, recommend X") | System prompt enforces list-only recommendations; IDs validated post-response | 🟠 |
| U-15 | `top_k` = 0 or negative | Validation error or default to 5 | 🟡 |
| U-16 | `top_k` very large (e.g. 100) | Cap at reasonable max (e.g. 10 or 20) | 🟡 |

### 2.3 Location-specific

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| U-17 | Unknown location (not in dataset, e.g. `"Mumbai"` when dataset has no Mumbai) | Return validation error or suggest closest valid cities from dataset | 🔴 |
| U-18 | Location typo (`"Banglore"`) | Fuzzy match against known cities if implemented; else treat as unknown | 🟡 |
| U-19 | Location with leading/trailing spaces | Trim before filter | 🟢 |
| U-20 | Case mismatch (`"delhi"` vs `"Delhi"`) | Case-insensitive match against dataset | 🟠 |

---

## 3. Filtering (`RestaurantFilter`)

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| F-01 | Zero restaurants match all filters | Return empty list; UI shows "No restaurants match your criteria. Try relaxing filters." | 🔴 |
| F-02 | Only one restaurant matches | Pass single candidate to Groq; return 1 recommendation | 🟡 |
| F-03 | Hundreds/thousands match (e.g. location only, low min_rating) | Cap at `MAX_CANDIDATES` (20); sort by rating desc before cap | 🔴 |
| F-04 | All matches have identical rating | Stable secondary sort (e.g. by name or votes) for deterministic order | 🟡 |
| F-05 | Budget filter eliminates all candidates (location OK but no `medium` tier) | Empty result → empty state | 🟠 |
| F-06 | Cuisine substring false positive (`"Indian"` matches `"Indo-Chinese"`) | Acceptable for MVP; document behavior | 🟢 |
| F-07 | Cuisine filter case sensitivity (`"italian"` vs `"Italian"`) | Case-insensitive match | 🟠 |
| F-08 | Combined filters overly restrictive (location + cuisine + budget + rating 4.5+) | Empty result; suggest relaxing one filter in UI copy | 🟠 |
| F-09 | `min_rating` filters out restaurants with parsed rating 0.0 (missing data) | Those restaurants excluded when min_rating > 0 | 🟡 |
| F-10 | Restaurant on budget tier boundary (cost exactly 300, 700) | Consistent inclusive/exclusive rule documented in loader | 🟡 |
| F-11 | Filter called with empty repository | Return empty list; log warning | 🟠 |
| F-12 | `top_k` > number of filtered candidates | Return all available (fewer than top_k) | 🟡 |
| F-13 | Filter order dependency (location before budget vs reverse) | Document fixed pipeline order per architecture §3.3.1 | 🟢 |
| F-14 | Special regex characters in cuisine search (if regex used) | Escape user input; prefer substring match | 🟡 |

---

## 4. Groq Integration (Groq API)

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| L-01 | `GROQ_API_KEY` missing or empty | Skip LLM; use rating-sorted fallback; log warning; UI banner | 🔴 |
| L-02 | Invalid / expired API key | Catch 401 from Groq; fallback + user-visible degraded mode | 🔴 |
| L-03 | Groq API timeout (network slow) | Configurable timeout (e.g. 30s); fallback on timeout | 🔴 |
| L-04 | Groq API rate limit (429) | Log; fallback; optional short retry after `Retry-After` | 🟠 |
| L-05 | Groq service unavailable (500, 503) | Fallback to rating-sorted results | 🔴 |
| L-06 | Model `llama3-70b-8192` not found (404 / model deprecated) | Log error; fallback; alert in README to update `LLM_MODEL` | 🟠 |
| L-07 | Empty response content from Groq | Treat as failure; retry once; then fallback | 🟠 |
| L-08 | Response truncated (`max_tokens` exceeded) | Increase `max_tokens` or reduce candidate count; retry; fallback if still truncated | 🟠 |
| L-09 | Groq returns valid HTTP but empty `choices` array | Fallback | 🟠 |
| L-10 | Concurrent requests (multiple Streamlit users) | Each request independent; no shared mutable LLM state | 🟡 |
| L-11 | Groq rate limits hit due to high request volume | Document tradeoff; implement retry with backoff; UI spinner | 🟡 |
| L-12 | SSL/TLS certificate errors | Fail with network error message; fallback | 🟡 |
| L-13 | Partial connectivity (DNS resolves, API hangs) | Timeout → fallback | 🟠 |
| L-14 | API returns unexpected content type (HTML error page) | Parse failure → retry → fallback | 🟡 |
| L-15 | Cost/quota exceeded on Groq account | Catch billing error if exposed; fallback + clear log | 🟠 |

---

## 5. Prompt Building & Response Parsing

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| P-01 | LLM wraps JSON in markdown fences (` ```json ... ``` `) | Strip fences before `json.loads` | 🔴 |
| P-02 | LLM returns plain text instead of JSON | Retry with "respond with valid JSON only"; then fallback | 🔴 |
| P-03 | JSON missing `recommendations` key | Treat as parse failure; retry; fallback | 🔴 |
| P-04 | JSON missing `summary` key | Optional field; proceed without summary | 🟢 |
| P-05 | `recommendations` is empty array | Fallback to rating-sorted top_k | 🟠 |
| P-06 | Fewer recommendations than `top_k` | Return what LLM provided if IDs valid; optionally pad from rating sort | 🟡 |
| P-07 | More recommendations than `top_k` | Trim to `top_k` by rank | 🟡 |
| P-08 | Duplicate `restaurant_id` in LLM response | Deduplicate; keep first by rank | 🟠 |
| P-09 | `restaurant_id` not in candidate set (hallucinated ID) | Reject invalid IDs; do not display fabricated restaurants | 🔴 |
| P-10 | `restaurant_id` valid but duplicate ranks (two rank=1) | Renumber sequentially by array order or rank value | 🟡 |
| P-11 | Missing `explanation` for a recommendation | Use generic fallback text: "Matches your preferences based on rating and filters." | 🟡 |
| P-12 | `explanation` extremely long | Truncate for UI display (e.g. 500 chars) | 🟢 |
| P-13 | Non-integer or string `rank` in JSON | Coerce to int or use array index | 🟡 |
| P-14 | LLM recommends restaurants not in filtered list by name (wrong ID) | Display only validated IDs; metadata always from dataset | 🔴 |
| P-15 | Prompt exceeds Llama 3 70B context window (unlikely with 20 candidates, 8192 token context) | Reduce `MAX_CANDIDATES`; compact JSON in prompt | 🟡 |
| P-16 | Unicode / emoji in LLM explanations | Render correctly in Streamlit UTF-8 | 🟢 |

---

## 6. Recommendation Orchestration

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| R-01 | Full happy path: filters → Groq → enriched results | Return `RecommendationResult[]` + optional `summary`; `fallback_used=false` | 🔴 |
| R-02 | Groq failure at any stage | Rating-sorted fallback; `fallback_used=true`; generic explanations | 🔴 |
| R-03 | Empty filter result before LLM call | Do not call Groq (save cost/latency); return empty with message | 🔴 |
| R-04 | Single candidate — still call LLM for explanation | Allow; or skip LLM and use template explanation (document choice) | 🟡 |
| R-05 | Repository lookup fails for valid LLM ID (data inconsistency) | Skip that entry; log error; continue with remaining | 🟠 |
| R-06 | User submits same preferences twice rapidly | Idempotent; two independent LLM calls (acceptable) or debounce in UI | 🟢 |
| R-07 | Partial Groq success (3 valid IDs, 2 invalid out of 5) | Return 3 valid; optionally fill remaining slots from rating sort | 🟠 |
| R-08 | `summary` present but recommendations empty | Treat as failure; fallback | 🟠 |
| R-09 | Exception mid-pipeline (unhandled) | Catch at service boundary; return 500 (API) or error banner (UI) | 🔴 |
| R-10 | Recommendation service called before repository loaded | Raise clear "not initialized" error | 🟠 |

---

## 7. UI (Streamlit)

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| S-01 | App startup while dataset still loading | Show spinner / "Loading restaurant data..." | 🟠 |
| S-02 | Dataset load fails at startup | `st.error` with message; app does not crash silently | 🔴 |
| S-03 | User clicks submit without selecting location | Inline validation message | 🔴 |
| S-04 | Groq call in progress (2–10s) | `st.spinner("Finding recommendations...")` | 🟠 |
| S-05 | Fallback mode active | Warning banner: "AI unavailable — showing rating-based results" | 🟠 |
| S-06 | Zero results | Info message with suggestion to relax filters | 🔴 |
| S-07 | Results contain null/ missing cost | Display "N/A" or "—" for cost field | 🟡 |
| S-08 | Very long restaurant name breaks layout | CSS wrap / truncate with tooltip | 🟢 |
| S-09 | Browser refresh mid-request | Streamlit reruns; may duplicate request (acceptable) | 🟢 |
| S-10 | Location dropdown empty (repository failure) | Disable submit; show error | 🟠 |
| S-11 | Rating slider at extremes (0.0 and 5.0) | Works correctly; no UI glitch | 🟡 |
| S-12 | Multiple tabs/sessions same machine | `@st.cache_resource` shares repository (intended) | 🟢 |

---

## 8. API — Optional FastAPI

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| A-01 | `POST /recommendations` with valid body | 200 + JSON response per architecture §6 | 🔴 |
| A-02 | Malformed JSON body | 422 Unprocessable Entity with field errors | 🔴 |
| A-03 | Missing required fields in body | 422 with Pydantic validation detail | 🔴 |
| A-04 | `GET /health` when app healthy | 200 `{"status": "ok"}` | 🟡 |
| A-05 | `GET /health` when dataset not loaded | 503 with reason | 🟠 |
| A-06 | `GET /locations` on empty repository | 200 with empty array | 🟡 |
| A-07 | Extremely large request body | Reject or limit size (e.g. 1 MB) | 🟡 |
| A-08 | Wrong HTTP method (GET on POST endpoint) | 405 Method Not Allowed | 🟢 |

---

## 9. Configuration & Environment

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| C-01 | `.env` file missing | Use defaults where safe; warn if `GROQ_API_KEY` missing | 🟠 |
| C-02 | Invalid `LLM_TEMPERATURE` (non-float) | Config validation error at startup | 🟡 |
| C-03 | `MAX_CANDIDATES` = 0 or negative | Default to 20 | 🟡 |
| C-04 | `MAX_CANDIDATES` very large (1000) | Cap at hard maximum (e.g. 50) to protect token budget | 🟠 |
| C-05 | Wrong `LLM_BASE_URL` (typo) | Connection error → fallback | 🟡 |
| C-06 | Running without virtualenv (dependency missing) | Import error with install instructions | 🟢 |
| C-07 | Python version < 3.10 | Document minimum version; fail early if syntax unsupported | 🟢 |
| C-08 | `data/` directory not writable (Parquet cache) | Log warning; continue in-memory only | 🟡 |
| C-09 | Environment variables with leading/trailing whitespace in API key | Strip whitespace on load | 🟡 |

---

## 10. Performance & Concurrency

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| E-01 | First Hugging Face download on slow network | Acceptable delay; progress feedback | 🟡 |
| E-02 | Second startup with Parquet cache | Load in seconds, not minutes | 🟠 |
| E-03 | End-to-end latency > 5s (Groq slow) | UI spinner; consider reducing prompt size or candidate count | 🟡 |
| E-04 | Memory pressure (full dataset in RAM) | Monitor; use Parquet + lazy load if needed | 🟡 |
| E-05 | Two simultaneous recommendation requests | Both complete independently; no race on repository | 🟡 |
| E-06 | Filter on 50k+ rows | Completes in < 1s with in-memory pandas/list | 🟡 |
| E-07 | Rapid repeated identical queries | Optional response cache (out of MVP scope); document | 🟢 |

---

## 11. Security

| ID | Scenario | Expected behavior | Priority |
|----|----------|-------------------|----------|
| SEC-01 | API key committed to git | Prevent via `.gitignore`; never log key | 🔴 |
| SEC-02 | API key visible in Streamlit UI or error traces | Redact in logs and user-facing errors | 🔴 |
| SEC-03 | Prompt injection via `additional_preferences` | System prompt + ID validation limit impact | 🟠 |
| SEC-04 | XSS via restaurant names in HTML UI | Streamlit escapes by default; verify no `unsafe_allow_html` with user data | 🟡 |
| SEC-05 | Path traversal in cache path config | Use fixed `data/` path; no user-controlled paths | 🟢 |
| SEC-06 | Unauthenticated public API exposure (Phase 5) | Document need for auth/rate limit in production | 🟡 |
| SEC-07 | Logging full prompts containing user PII | Truncate or omit in production logs | 🟡 |
| SEC-08 | Dependency vulnerability in `requirements.txt` | Pin versions; periodic audit | 🟢 |

---

## 12. Cross-Cutting & Integration Scenarios

End-to-end flows that span multiple layers:

| ID | Scenario | Expected end-to-end behavior | Priority |
|----|----------|------------------------------|----------|
| X-01 | New user, valid prefs, GLM healthy | Filter → GLM rank → 5 cards with explanations | 🔴 |
| X-02 | Valid prefs, zero filter matches | No GLM call; empty state in UI | 🔴 |
| X-03 | Valid prefs, GLM down | Rating-sorted results + fallback banner | 🔴 |
| X-04 | Invalid location | Validation error before filter/LLM | 🔴 |
| X-05 | All optional fields omitted | Filter by location + budget only; GLM still explains | 🟠 |
| X-06 | Maximum strictness (5.0 rating + specific cuisine + high budget + rare city) | Likely empty → helpful empty state | 🟡 |
| X-07 | Dataset has only one city; user picks that city | Normal operation | 🟡 |
| X-08 | Restart app after Parquet cached | Faster startup; same recommendation quality | 🟡 |
| X-09 | Change `.env` API key without restart | Streamlit may need restart to pick up new env (document) | 🟢 |
| X-10 | Demo with API key revoked mid-session | Next request falls back gracefully | 🟠 |

---

## 13. Test Case Mapping

Recommended pytest / manual tests for critical edge cases:

| Test file | Edge case IDs to cover |
|-----------|------------------------|
| `tests/test_loader.py` | D-08, D-12–D-16, D-21, D-25 |
| `tests/test_filter.py` | F-01, F-03, F-05, F-07, F-12 |
| `tests/test_prompt_builder.py` | U-12, P-15 |
| `tests/test_recommendation.py` | R-01–R-03, R-07, P-01–P-02, P-09, L-01 (mock) |
| Manual / Streamlit | S-03, S-05, S-06, X-01–X-04 |
| `tests/test_api.py` (Phase 5) | A-01–A-03 |

---

## 14. Default Handling Quick Reference

| Scenario | Default action |
|----------|----------------|
| Unknown location | Validation error + suggest valid cities |
| Empty filter results | Empty state message; no LLM call |
| Groq API any failure | Rating-sorted fallback; `fallback_used=true` |
| Malformed LLM JSON | One retry → fallback |
| Hallucinated restaurant ID | Drop entry; never show fabricated data |
| Missing optional fields | Sensible defaults (min_rating=0, cuisine=any) |
| Missing API key | Fallback mode only |
| Dataset load failure | Fail startup with clear error |
| Long additional_preferences | Truncate to 500 characters |

---

## References

- [context.md](./context.md) — success criteria and workflow
- [architecture.md](./architecture.md) — §10 Error Handling, §3.4 Groq (Llama 3 70B), §7 Prompts
- [implementation-plan.md](./implementation-plan.md) — Phase 4 hardening, Risk Register

---

*Document version: 1.1 — LLM: Llama 3 70B (Groq). Covers MVP (Phases 0–4) and optional API (Phase 5)*
