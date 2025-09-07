# Very simple generator for the Test Matrix in docs/TEST_PLAN.md
# - Reads cases from docs/cases.yaml
# - Runs build/tcs temp prev dt (LC_ALL=C)
# - Maps raw output to (status, heater) using our oracle
# - Writes a markdown table between BEGIN/END markers

import os, subprocess, math
import yaml  # pip install pyyaml

BINARY = "build/tcs"
PLAN_MD = "docs/TEST_PLAN.md"
CASES_YAML = "docs/cases.yaml"
BEGIN = "<!-- BEGIN:AUTO_MATRIX -->"
END   = "<!-- END:AUTO_MATRIX -->"

def parse_num(x):
    s = str(x).strip()
    if s.lower() == "nan":
        return float("nan")
    if s.lower() in ("inf","+inf","infinity","+infinity"):
        return float("inf")
    if s.lower() in ("-inf","-infinity"):
        return float("-inf")
    try:
        return float(s)
    except ValueError:
        return float("nan")

def is_band(temp):
    # 0  T  40; NaN is never in band
    return (not math.isnan(temp)) and (0.0 <= temp <= 40.0)

def map_raw_to_status(raw, prev, temp_in_band):
    # Oracle from the plan:
    # -2 -> SAFETY_MODE / None
    # -1 -> INVALID_INPUT / None
    #  0 -> OK / OFF  (or UNCHANGED if prev=0 and band)
    #  1 -> OK / ON   (or UNCHANGED if prev=1 and band)
    if raw == -2:
        return "SAFETY_MODE", None
    if raw == -1:
        return "INVALID_INPUT", None
    if raw in (0, 1):
        if temp_in_band and raw == prev:
            return "OK", prev  # UNCHANGED
        return "OK", raw
    return "UNKNOWN", None

def run_case(temp_str, prev, dt_str):
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    args = [BINARY, str(temp_str), str(prev), str(dt_str)]
    res = subprocess.run(args, env=env, capture_output=True, text=True)
    out = (res.stdout or "").strip().splitlines()
    last = out[-1] if out else ""
    return int(last)

def render_table(rows):
    lines = []
    lines.append("| ID | Purpose | Input (T,prev,dt) | Expected (Spec) | Observed | Notes |")
    lines.append("|----|---------|--------------------|------------------|----------|-------|")
    for r in rows:
        lines.append(f"| {r['id']} | {r['purpose']} | {r['input']} | {r['expected']} | {r['observed']} | {r['notes']} |")
    return "\n".join(lines)

def replace_in_plan(new_table):
    with open(PLAN_MD, "r", encoding="utf-8") as f:
        text = f.read()
    block = BEGIN + "\n" + new_table + "\n" + END
    i = text.find(BEGIN)
    j = text.find(END)
    if i != -1 and j != -1 and j > i:
        updated = text[:i] + block + text[j+len(END):]

def main():
    assert os.path.exists(BINARY), f"Binary not found: {BINARY}"
    with open(CASES_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    rows = []
    for c in data["cases"]:
        t_str = c["input"]["temp"]   # keep original string (e.g., "NaN")
        p     = int(c["input"]["prev"])
        dt_str= c["input"]["dt"]

        # For band check we need numeric temp
        t_num = parse_num(t_str)
        in_band = is_band(t_num)

        # Run program and map observed
        raw = run_case(t_str, p, dt_str)
        obs_status, obs_heater = map_raw_to_status(raw, p, in_band)

        # Expected (spec)
        exp_status = c["expected"]["status"]
        exp_heater = c["expected"]["heater"]

        # Render strings
        input_str = f"{t_str},{p},{dt_str}"
        expected_str = exp_status if exp_heater is None else f"{exp_status} (heater={exp_heater})"
        observed_str = obs_status if obs_heater is None else f"{obs_status} (heater={obs_heater})"

        notes = "OK"
        if (obs_status != exp_status) or (obs_heater != exp_heater):
            notes = f"**Diff:** expected {expected_str}, observed {observed_str}"

        rows.append({
            "id": c["id"],
            "purpose": c["purpose"],
            "input": input_str,
            "expected": expected_str,
            "observed": observed_str,
            "notes": notes
        })

    table_md = render_table(rows)
    replace_in_plan(table_md)
    print("Updated matrix in TEST_PLAN.md")

if __name__ == "__main__":
    main()
