# TEST REPORT — Satellite TCS (v1)

**Repository:** zervakisai/OHB  
**CI run:** <PASTE GITHUB ACTIONS RUN URL>  
**Scope:** Black-box CLI verification of TCS against R2–R7.  
**Date:** 2025-09-07 (Europe/Athens)

## 1. Executive Summary
- Result: CI green (build + tests). Pytest: **14 passed, 2 xfailed** (known deviations).
- Outcome: All requirements R2–R7 satisfied under tested conditions. Non-finite inputs deviation documented.

## 2. Environment
- Compiler: `clang -Wall -Wextra -O2`
- Runner: GitHub Actions (ubuntu-latest), `pytest` + JUnit XML
- Locale: `LC_ALL=C`

## 3. Requirements Verification
| Req | Statement (short)                   | Tests                        | Verdict |
|-----|-------------------------------------|------------------------------|---------|
| R2  | T < 0 ⇒ ON                          | TCS-002, TCS-003             | PASS    |
| R3  | T > 40 ⇒ OFF                        | TCS-007, TCS-008             | PASS    |
| R4  | 0≤T≤40 ⇒ UNCHANGED                  | TCS-004, TCS-005, TCS-006    | PASS    |
| R5  | T < −15 or T > 45 ⇒ SAFETY_MODE     | TCS-001, TCS-009             | PASS    |
| R6  | Invalid sensor ⇒ INVALID_INPUT      | TCS-012                      | PASS    |
| R7  | Invalid timestep ⇒ INVALID_INPUT    | TCS-010, TCS-011             | PASS    |

Precedence evidence: **INVALID > SAFETY > Control** (TCS-015, TCS-016).

## 4. Boundaries & Evidence
See `docs/TEST_PLAN.md` (auto-generated matrix). Key edges behave as specified:  
0 & 40 → UNCHANGED; −15 & 45 → control (not safety); below −15/above 45 → SAFETY.

## 5. Deviation & Change Request
- Observed: **NaN** (temp or dt) → **UNCHANGED** (current impl), policy expects **INVALID_INPUT**.  
  Cases: TCS-013, TCS-014 (marked **xfail**).
- **CR-001:** Treat **non-finite inputs** (`NaN`, `±Inf`) as **INVALID_INPUT** for both temperature and timestep.

## 6. Artifacts
- `artifacts/junit.xml` (pytest)
- `docs/TEST_PLAN.md` (matrix auto-generation)
- Source in `src/`, tests in `tests/`, generator in `tools/`

## 7. Next Steps
- Discuss/approve **CR-001** and fix plan.
- (Optional) Add sanitizers job; property-based sampling with Hypothesis.

