#!/usr/bin/env python3
"""
Delivery DEV Phase - Slice 1: State-only orchestration

Implements minimal CLI without AI or code generation:
- dev-structure <name>
- dev-describe [<prompt...>]
- dev-proceed
- dev-feedback [<prompt...>]
- dev-reset
- dev-status

State model (.deployment-state.json):
{
  "feature_name": "my-feature",
  "phase": "DELIVERY",
  "current_step": "dev.describe",
  "substate": "awaiting_ai",  # awaiting_ai | awaiting_human
  "prompt": "optional prompt",
  "red_count_config": 1,
  "history": [
    { "step": "dev.describe", "substate": "awaiting_ai",
      "prompt": "optional", "ts": "2025-01-01T00:00:00" }
  ]
}
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime


DEV_STEPS_ORDER = [
    "dev.structure",
    "dev.describe",
    "dev.red.1",
    "dev.green",
    "dev.refactor",
]


def safe_print(message: str) -> None:
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        import re
        clean = re.sub(r'[\U0001F300-\U0001F9FF]', '', message)
        try:
            print(clean, flush=True)
        except Exception:
            print(message.encode('ascii', errors='ignore').decode('ascii'), flush=True)


def normalize_feature_name(raw: str) -> str:
    import re
    s = re.sub(r'[^a-zA-Z0-9\s_-]', '', raw)  # strip specials
    s = s.lower().replace(' ', '-').replace('_', '-')
    return s


def state_path_for(feature_path: Path) -> Path:
    return feature_path / ".deployment-state.json"


def load_state(feature_path: Path) -> dict | None:
    sp = state_path_for(feature_path)
    if not sp.exists():
        return None
    try:
        return json.loads(sp.read_text(encoding="utf-8"))
    except Exception:
            return None
    

def save_state(feature_path: Path, state: dict) -> None:
    sp = state_path_for(feature_path)
    sp.parent.mkdir(parents=True, exist_ok=True)
    # minimal validation
    state.setdefault("history", [])
    sp.write_text(json.dumps(state, indent=2), encoding="utf-8")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def next_step_id(current_step: str) -> str | None:
    try:
        idx = DEV_STEPS_ORDER.index(current_step)
    except ValueError:
        return None
    if idx + 1 < len(DEV_STEPS_ORDER):
        return DEV_STEPS_ORDER[idx + 1]
    return None


def print_status(state: dict, feature_path: Path) -> None:
    step = state.get("current_step")
    sub = state.get("substate")
    prompt = state.get("prompt")
    nxt = next_step_id(step) if sub == "awaiting_human" else step  # after human, next changes
    safe_print("\n[STATUS]")
    safe_print(f"  Feature: {state.get('feature_name')}")
    safe_print(f"  Phase: {state.get('phase')}")
    safe_print(f"  Step: {step}")
    safe_print(f"  Substate: {sub}  (awaiting_ai -> awaiting_human -> next step)")
    safe_print(f"  Prompt: {repr(prompt) if prompt else None}")
    if sub == "awaiting_human":
        ns = next_step_id(step)
        safe_print(f"  Next: {ns if ns else 'END'}")
    else:
        safe_print(f"  Next: (proceed to awaiting_human for {step})")
    safe_print(f"  State: {state_path_for(feature_path)}")


def head_lines(s: str | None, n: int) -> str:
    if not s:
        return ""
    lines = s.strip().splitlines()
    if len(lines) <= n:
        return s.strip()
    return "\n".join(lines[:n]) + f"\n... (+{len(lines)-n} more lines)"


def build_summary(feature: str, step: str, substate: str, prompt: str | None,
                  next_step: str | None, state_file: Path,
                  prompt_head: str = "", output_head: str = "") -> str:
    return (
f"""# Delivery Update\n- Feature: {feature}\n- Step: {step}\n- Substate: {substate}\n- Prompt: {repr(prompt) if prompt else None}\n- Next: {next_step if next_step else 'END'}\n- State: {state_file}\n\n## Prompt (head)\n```text\n{prompt_head}\n```\n\n## Output (head)\n```text\n{output_head}\n```\n"""
    )


def post_to_cursor(summary_text: str, model: str, session: str, cwd: str | None = None) -> bool:
    import shutil
    exe = shutil.which("cursor-agent")
    
    # If not in PATH, try via WSL on Windows
    if not exe:
        import platform
        if platform.system() == "Windows":
            # Try cursor-agent in WSL Ubuntu
            wsl_cmd = ["wsl", "-d", "Ubuntu", "bash", "-c", "~/.local/bin/cursor-agent"]
            res = subprocess.run([*wsl_cmd, "--version"], cwd=cwd, capture_output=True, text=True)
            if res.returncode == 0:
                exe = wsl_cmd
    
    if not exe:
        safe_print("[WARN] cursor-agent not found on PATH or in WSL")
        return False
        
    # First try: pass prompt with -p (fast path)
    if isinstance(exe, list):
        cmd = exe + ["-p", summary_text, "--model", model, "--output-format", "text", "--session", session]
    else:
        cmd = [exe, "-p", summary_text, "--model", model, "--output-format", "text", "--session", session]
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode == 0:
        return True
    
    # Fallback: feed summary via STDIN (more reliable for multi-line content)
    if isinstance(exe, list):
        cmd = exe + ["--model", model, "--output-format", "text", "--session", session]
    else:
        cmd = [exe, "--model", model, "--output-format", "text", "--session", session]
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, input=summary_text)
    if res.returncode != 0:
        msg = (res.stderr or res.stdout or "").strip()
        if msg:
            safe_print(f"[WARN] cursor-agent failed: {msg}")
    return res.returncode == 0


def report_if_enabled(args: argparse.Namespace, state: dict, feature_path: Path) -> None:
    if not getattr(args, "report_to_cursor", False):
        return
    feature = state.get("feature_name", "")
    step = state.get("current_step", "")
    sub = state.get("substate", "")
    prompt = state.get("prompt")
    nxt = next_step_id(step) if sub == "awaiting_human" else step
    summary = build_summary(
        feature=feature,
        step=step,
        substate=sub,
        prompt=prompt,
        next_step=nxt,
        state_file=state_path_for(feature_path),
        prompt_head=head_lines(prompt, 12),
        output_head=""
    )
    session = getattr(args, "cursor_session", None) or f"dev:{feature}"
    model = getattr(args, "cursor_model", "auto")
    ok = post_to_cursor(summary, model=model, session=session, cwd=str(Path.cwd()))
    if not ok:
        safe_print("[WARN] Failed to post summary to Cursor (cursor-agent).")


def ensure_base_state(feature_name: str, feature_path: Path) -> dict:
    feature_path.mkdir(parents=True, exist_ok=True)
    st = {
        "feature_name": feature_name,
        "phase": "DELIVERY",
        "current_step": "dev.structure",
        "substate": "awaiting_ai",
        "prompt": None,
        "red_count_config": 1,
        "history": [],
    }
    st["history"].append({
        "step": st["current_step"],
        "substate": st["substate"],
        "prompt": st["prompt"],
        "ts": now_iso()
    })
    save_state(feature_path, st)
    return st


def cmd_dev_structure(args: argparse.Namespace) -> int:
    feature = normalize_feature_name(" ".join(args.name))
    feature_path = Path("features") / feature
    st = load_state(feature_path)
    if st is None:
        st = ensure_base_state(feature, feature_path)
    else:
        # reset to structure step/substate only (do not delete history)
        st["feature_name"] = feature
        st["phase"] = "DELIVERY"
        st["current_step"] = "dev.structure"
        st["substate"] = "awaiting_ai"
        st["prompt"] = None
        st["history"].append({
            "step": st["current_step"],
            "substate": st["substate"],
            "prompt": st["prompt"],
            "ts": now_iso()
        })
        save_state(feature_path, st)
    safe_print(f"[OK] dev.structure initialized for {feature}")
    print_status(st, feature_path)
    report_if_enabled(args, st, feature_path)
    return 0


def cmd_dev_describe(args: argparse.Namespace) -> int:
    feature = normalize_feature_name(args.feature)
    feature_path = Path("features") / feature
    st = load_state(feature_path)
    if st is None:
        st = ensure_base_state(feature, feature_path)
    st["current_step"] = "dev.describe"
    st["substate"] = "awaiting_ai"
    if args.prompt:
        st["prompt"] = " ".join(args.prompt)
    st["history"].append({
        "step": st["current_step"],
        "substate": st["substate"],
        "prompt": st.get("prompt"),
        "ts": now_iso()
    })
    save_state(feature_path, st)
    safe_print(f"[OK] dev.describe set for {feature}")
    print_status(st, feature_path)
    report_if_enabled(args, st, feature_path)
    return 0


def cmd_dev_proceed(args: argparse.Namespace) -> int:
    feature = normalize_feature_name(args.feature)
    feature_path = Path("features") / feature
    st = load_state(feature_path)
    if st is None:
        safe_print("[ERROR] No state found. Run dev-structure first.")
        return 1

    step = st.get("current_step")
    sub = st.get("substate")

    if sub == "awaiting_ai":
        # Move within the same step to awaiting_human
        st["substate"] = "awaiting_human"
        st["history"].append({
            "step": step, "substate": st["substate"],
            "prompt": st.get("prompt"), "ts": now_iso()
        })
        save_state(feature_path, st)
        safe_print(f"[OK] {step}: awaiting_ai -> awaiting_human")
        print_status(st, feature_path)
        report_if_enabled(args, st, feature_path)
        return 0

    if sub == "awaiting_human":
        # Advance to next step
        ns = next_step_id(step)
        if ns is None:
            # end of pipeline
            st["history"].append({
                "step": step, "substate": "completed",
                "prompt": st.get("prompt"), "ts": now_iso()
            })
            save_state(feature_path, st)
            safe_print("[DONE] End of DEV steps")
            print_status(st, feature_path)
            report_if_enabled(args, st, feature_path)
            return 0
        st["history"].append({
            "step": step, "substate": "completed",
            "prompt": st.get("prompt"), "ts": now_iso()
        })
        st["current_step"] = ns
        st["substate"] = "awaiting_ai"
        st["prompt"] = st.get("prompt")  # keep or clear; we keep for traceability
        st["history"].append({
            "step": st["current_step"], "substate": st["substate"],
            "prompt": st.get("prompt"), "ts": now_iso()
        })
        save_state(feature_path, st)
        safe_print(f"[OK] advanced to {ns}/awaiting_ai")
        print_status(st, feature_path)
        report_if_enabled(args, st, feature_path)
        return 0

    safe_print("[ERROR] Invalid substate in state file")
    return 1


def cmd_dev_feedback(args: argparse.Namespace) -> int:
    feature = normalize_feature_name(args.feature)
    feature_path = Path("features") / feature
    st = load_state(feature_path)
    if st is None:
        safe_print("[ERROR] No state found. Run dev-structure first.")
        return 1

    # Reset current step back to awaiting_ai and optionally update prompt
    st["substate"] = "awaiting_ai"
    if args.prompt:
        st["prompt"] = " ".join(args.prompt)
    st["history"].append({
        "step": st.get("current_step"), "substate": st["substate"],
        "prompt": st.get("prompt"), "ts": now_iso()
    })
    save_state(feature_path, st)
    safe_print("[OK] feedback recorded; current step reset to awaiting_ai")
    print_status(st, feature_path)
    report_if_enabled(args, st, feature_path)
    return 0


def cmd_dev_reset(args: argparse.Namespace) -> int:
    feature = normalize_feature_name(args.feature)
    feature_path = Path("features") / feature
    st = load_state(feature_path)
    if st is None:
        st = ensure_base_state(feature, feature_path)
    else:
        st["current_step"] = "dev.structure"
        st["substate"] = "awaiting_ai"
        st["prompt"] = None
        st["history"].append({
            "step": st["current_step"], "substate": st["substate"],
            "prompt": st.get("prompt"), "ts": now_iso()
        })
        save_state(feature_path, st)
    safe_print("[OK] reset to dev.structure/awaiting_ai")
    print_status(st, feature_path)
    report_if_enabled(args, st, feature_path)
    return 0


def cmd_dev_status(args: argparse.Namespace) -> int:
    feature = normalize_feature_name(args.feature)
    feature_path = Path("features") / feature
    st = load_state(feature_path)
    if st is None:
        safe_print("[ERROR] No state found.")
        return 1
    print_status(st, feature_path)
    report_if_enabled(args, st, feature_path)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="DEV Phase Slice 1 - State-only orchestration")
    # Reporting to Cursor chat: default ON; disable with --no-report-to-cursor
    parser.add_argument("--report-to-cursor", dest="report_to_cursor", action="store_true", default=True,
                        help="Post short summary to Cursor via cursor-agent (default: on)")
    parser.add_argument("--no-report-to-cursor", dest="report_to_cursor", action="store_false",
                        help="Disable posting summary to Cursor via cursor-agent")
    parser.add_argument("--cursor-model", default="auto",
                        help="Model for cursor-agent (default: auto)")
    parser.add_argument("--cursor-session", default=None,
                        help="Session name for cursor-agent (default: dev:<feature>)")
    sub = parser.add_subparsers(dest="action", required=True)

    p_structure = sub.add_parser("dev-structure", help="Initialize feature and set dev.structure")
    p_structure.add_argument("name", nargs="+", help="Feature name parts")
    p_structure.set_defaults(func=cmd_dev_structure)

    p_describe = sub.add_parser("dev-describe", help="Set dev.describe (optional prompt)")
    p_describe.add_argument("--feature", required=True, help="Feature name")
    p_describe.add_argument("prompt", nargs="*", help="Optional prompt text")
    p_describe.set_defaults(func=cmd_dev_describe)

    p_proceed = sub.add_parser("dev-proceed", help="Advance substate/step deterministically")
    p_proceed.add_argument("--feature", required=True, help="Feature name")
    p_proceed.set_defaults(func=cmd_dev_proceed)

    p_feedback = sub.add_parser("dev-feedback", help="Repeat current AI subaction with new prompt (no AI call)")
    p_feedback.add_argument("--feature", required=True, help="Feature name")
    p_feedback.add_argument("prompt", nargs="*", help="Optional prompt text")
    p_feedback.set_defaults(func=cmd_dev_feedback)

    p_reset = sub.add_parser("dev-reset", help="Reset to dev.structure/awaiting_ai")
    p_reset.add_argument("--feature", required=True, help="Feature name")
    p_reset.set_defaults(func=cmd_dev_reset)

    p_status = sub.add_parser("dev-status", help="Show current state")
    p_status.add_argument("--feature", required=True, help="Feature name")
    p_status.set_defaults(func=cmd_dev_status)

    args = parser.parse_args()
    rc = args.func(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
