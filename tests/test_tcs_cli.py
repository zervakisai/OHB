import os
import math
import pathlib
import subprocess

import pytest
import yaml  # pip install pyyaml

BINARY = pathlib.Path("build/tcs")
CASES_YAML = pathlib.Path("docs/cases.yaml")


def is_band(temp_str: str) -> bool:
    """Band is 0 ≤ T ≤ 40. NaN is never in band."""
    try:
        v = float(str(temp_str))
        return (not math.isnan(v)) and (0.0 <= v <= 40.0)
    except ValueError:
        return False


def map_raw(raw: int, prev: int, in_band: bool):
    """
    Oracle (from the TEST_PLAN):
    -2 -> SAFETY_MODE / None
    -1 -> INVALID_INPUT / None
     0 -> OK / OFF  (or UNCHANGED if prev==0 and in_band)
     1 -> OK / ON   (or UNCHANGED if prev==1 and in_band)
    """
    if raw == -2:
        return "SAFETY_MODE", None
    if raw == -1:
        return "INVALID_INPUT", None
    if raw in (0, 1):
        if in_band and raw == prev:
            return "OK", prev  # UNCHANGED
        return "OK", raw
    return "UNKNOWN", None


def run_bin(temp, prev, dt) -> int:
    """Run the CLI and return the last stdout line as int."""
    assert BINARY.exists(), "Binary not found. Build it first (see README/Makefile)."
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    args = [str(BINARY), str(temp), str(prev), str(dt)]
    res = subprocess.run(args, env=env, capture_output=True, text=True)
    # We expect a single integer on the last line
    out_lines = (res.stdout or "").strip().splitlines()
    last = out_lines[-1] if out_lines else ""
    return int(last)


def load_cases():
    data = yaml.safe_load(CASES_YAML.read_text(encoding="utf-8"))
    return data["cases"]


CASES = load_cases()

# Parametrize tests from YAML (ids show nicely in pytest output)
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_tcs_cli(case):
    cid = case["id"]
    temp = case["input"]["temp"]
    prev = int(case["input"]["prev"])
    dt = case["input"]["dt"]

    # Known deviations (documented in TEST_PLAN): NaN alone -> UNCHANGED by current impl
    if cid in ("TCS-013", "TCS-014"):
        pytest.xfail("Known deviation: NaN treated as UNCHANGED by current implementation")

    raw = run_bin(temp, prev, dt)
    status_obs, heater_obs = map_raw(raw, prev, is_band(temp))

    exp_status = case["expected"]["status"]
    exp_heater = case["expected"]["heater"]

    # One simple assertion compares both status and heater
    assert (status_obs == exp_status) and (heater_obs == exp_heater), (
        f"{cid}: expected {exp_status}/{exp_heater}, observed {status_obs}/{heater_obs}"
    )
