# TEST PLAN  Satellite TCS (v1)

## 1. Scope
Verify the CLI behaviour of the Thermal Control System (TCS) module against R2R7 using requirements-based testing, boundary analysis, and invalid/robustness checks (black-box discovery  confirmation).

## 2. Assumptions & Oracles
- CLI: `tcs <temp> <prev_state> <dt>`.
- Mapping (raw  status/heater):
  - -2  SAFETY_MODE, heater=None
  - -1  INVALID_INPUT, heater=None
  -  0  OK, heater=OFF   (or UNCHANGED when `prev=0` and `0T40`)
  -  1  OK, heater=ON    (or UNCHANGED when `prev=1` and `0T40`)
- Rule precedence: **INVALID  SAFETY  Control**.
- Invalids (policy): `dt  0` or non-finite (`NaN/Inf`) or invalid sensor  INVALID_INPUT.
  *Observed deviation:* NaN alone is treated as **UNCHANGED**.

## 3. Equivalence Classes & Boundaries
- Temp classes: (,15), [15,0), [0,40], (40,45], (45,+)
- Invalids: `dt0`, invalid sensor, non-finite (`NaN/Inf`)
- Boundaries: 15, 0, 40, 45 with below / exactly / above

## 4. Test Matrix (Expected vs Observed)
> Auto-generated from `docs/cases.yaml` by `tools/gen_matrix.py`.

<!-- BEGIN:AUTO_MATRIX -->
| ID | Purpose | Input (T,prev,dt) | Expected (Spec) | Observed | Notes |
|----|---------|--------------------|------------------|----------|-------|
| TCS-004 | Edge 0 (prev=1) | 0,1,1 | OK (heater=1) | OK (heater=1) | OK |
| TCS-006 | Edge 40 (prev=0) | 40,0,1 | OK (heater=0) | OK (heater=0) | OK |
| TCS-002 | Edge -15 (not safety; below-0 control) | -15,0,1 | OK (heater=1) | OK (heater=1) | OK |
| TCS-008 | Edge 45 (not safety; above-40 control) | 45,1,1 | OK (heater=0) | OK (heater=0) | OK |
| TCS-003 | Below 0 | -0.1,0,1 | OK (heater=1) | OK (heater=1) | OK |
| TCS-007 | Above 40 | 40.1,1,1 | OK (heater=0) | OK (heater=0) | OK |
| TCS-005 | Mid band | 20,0,1 | OK (heater=0) | OK (heater=0) | OK |
| TCS-001 | Safety low | -16,0,1 | SAFETY_MODE | SAFETY_MODE | OK |
| TCS-009 | Safety high | 45.1,1,1 | SAFETY_MODE | SAFETY_MODE | OK |
| TCS-010 | Invalid dt=0 | 10,0,0 | INVALID_INPUT | INVALID_INPUT | OK |
| TCS-011 | Invalid dt<0 | 10,0,-1 | INVALID_INPUT | INVALID_INPUT | OK |
| TCS-012 | Invalid sensor (special) | 999,0,1 | INVALID_INPUT | INVALID_INPUT | OK |
| TCS-013 | Non-finite temperature (NaN) | NaN,1,1 | INVALID_INPUT | OK (heater=1) | **Diff:** expected INVALID_INPUT, observed OK (heater=1) |
| TCS-014 | Non-finite dt (NaN) | 10,1,NaN | INVALID_INPUT | OK (heater=1) | **Diff:** expected INVALID_INPUT, observed OK (heater=1) |
| TCS-015 | Precedence: invalid vs safety (low) | -20,0,0 | INVALID_INPUT | INVALID_INPUT | OK |
| TCS-016 | Precedence: NaN + dt=0 | NaN,0,0 | INVALID_INPUT | INVALID_INPUT | OK |
<!-- END:AUTO_MATRIX -->

## 5. Exit Criteria
- All R2R7 covered at boundaries (below / exactly / above).
- Precedence documented (INVALID  SAFETY  Control).
- Deviations (e.g., NaN) recorded with a CR proposal.

