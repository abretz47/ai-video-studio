"""Live sample runner for production quality regression."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from scripts.harness._common import ensure_run_dir
from scripts.harness.production_quality_api_checks import (
    lint_script_via_api,
    score_script_via_api,
)
from scripts.harness.production_quality_report import (
    aggregate_quality_report,
    evaluate_provider_chain_sample,
    extract_clip_frames,
    load_provider_chain,
    make_contact_sheet,
    write_quality_outputs,
)

DEFAULT_PREMISES = [
    "Night-shift cartoon robot discovers the bonus has been zeroed out and must find who changed the timeline before the countdown ends.",
    "Cartoon mech editor goes live with wrong assets; the client is about to review and the teammate says it's the only evidence.",
    "Blue cartoon robot receives deleted dialogue and discovers it is the real contract terms.",
    "Cartoon character director refuses to use live-action footage but is required to deliver a safe sample in ten minutes.",
    "A cartoon character in the asset library suddenly has a different face; the protagonist must prove it's a supplier callback issue.",
    "Robot production assistant discovers the second video has no characters and must stop the full release.",
    "A cartoon studio's voice file is misaligned; the protagonist identifies the insider through a single line of dialogue.",
    "One character reference image is reused across all shots but reveals a hidden marker in the final frame.",
    "The robot project manager must fix the timeline backfill before the client closes the ticket, or the whole team's work is wasted.",
    "The cartoon reviewer discovers the final cut has no story hook and re-orders a real reversal within three seconds.",
]


def run_live_samples(args: argparse.Namespace, run_dir: Path) -> dict[str, Any]:
    if not args.episode_id or not args.script_id:
        raise SystemExit("live-10 requires --episode-id and --script-id")
    samples: list[dict[str, Any]] = []
    report = _base_live_report(args, samples)
    write_quality_outputs(run_dir, report)
    for sample_index in range(1, args.sample_count + 1):
        sample_id = f"sample-{sample_index:02d}"
        premise = DEFAULT_PREMISES[(sample_index - 1) % len(DEFAULT_PREMISES)]
        for attempt in range(1, args.max_retries + 2):
            sample = run_live_sample(
                args,
                run_dir=run_dir,
                child_run_id=f"{args.run_id}-{sample_id}-attempt-{attempt}",
                sample_id=sample_id,
                premise=premise,
                attempt=attempt,
            )
            samples.append(sample)
            write_quality_outputs(run_dir, _base_live_report(args, samples))
            if sample.get("passed"):
                break
    return _base_live_report(args, samples)


def run_live_sample(
    args: argparse.Namespace,
    *,
    run_dir: Path,
    child_run_id: str,
    sample_id: str,
    premise: str,
    attempt: int,
) -> dict[str, Any]:
    provider_artifact = ensure_run_dir(child_run_id) / "provider_chain.json"
    started = time.monotonic()
    command = _provider_chain_command(args, child_run_id, premise)
    completed = subprocess.run(
        command,
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        timeout=max(args.timeout_seconds * 5, 1800),
        check=False,
    )
    log_path = _write_provider_log(run_dir, sample_id, attempt, command, completed)
    if not provider_artifact.exists():
        return failed_sample(
            sample_id,
            attempt,
            str(provider_artifact),
            "provider_chain_artifact_missing",
            str(log_path),
            round(time.monotonic() - started, 3),
        )
    payload = load_provider_chain(str(provider_artifact))
    frames, sheet, frame_error = _collect_frames(payload, run_dir, sample_id, attempt)
    sample = evaluate_provider_chain_sample(
        payload,
        provider_chain_artifact=str(provider_artifact),
        script_lint=lint_script_via_api(args, payload, f"{sample_id}-{attempt}"),
        script_score=score_script_via_api(args, payload, f"{sample_id}-{attempt}"),
        frame_artifacts=frames,
        contact_sheet=sheet,
        sample_id=sample_id,
        attempt=attempt,
    )
    sample["subprocess"] = _subprocess_summary(completed, log_path, started)
    sample["script_premise"] = premise
    if frame_error:
        sample["hard_failures"].append("frame_extraction")
        sample["passed"] = False
        sample["frame_extraction_error"] = frame_error
    return sample


def failed_sample(
    sample_id: str,
    attempt: int,
    provider_artifact: str,
    reason: str,
    log_path: str,
    elapsed_seconds: float,
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "attempt": attempt,
        "provider_chain_artifact": provider_artifact,
        "provider_chain_ok": False,
        "passed": False,
        "hard_failures": ["provider_chain"],
        "script_failures": [],
        "failure_categories": [reason],
        "subprocess": {"log_path": log_path, "elapsed_seconds": elapsed_seconds},
        "timeline_order": {"passed": False, "missing_labels": []},
        "render_structure": {"passed": False},
        "character_consistency": {"passed": False},
        "script_lint": {"status": "skipped", "passed": False},
        "script_score": {"status": "skipped", "passed": False},
        "structured_script_score": {"status": "skipped", "passed": False},
    }


def _provider_chain_command(
    args: argparse.Namespace, child_run_id: str, premise: str
) -> list[str]:
    command = [
        sys.executable,
        "scripts/harness/provider_chain_regression.py",
        "--mode",
        "full-30s",
        "--run-id",
        child_run_id,
        "--api-url",
        args.api_url,
        "--username",
        args.username,
        "--password",
        args.password,
        "--episode-id",
        str(args.episode_id),
        "--script-id",
        str(args.script_id),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--poll-interval-seconds",
        str(args.poll_interval_seconds),
        "--video-concurrency",
        str(args.video_concurrency),
        "--script-premise",
        premise,
    ]
    if args.keep_temp_ip:
        command.append("--keep-temp-ip")
    return command


def _collect_frames(
    payload: dict[str, Any],
    run_dir: Path,
    sample_id: str,
    attempt: int,
) -> tuple[list[str], str | None, str | None]:
    try:
        videos = (payload.get("key_artifacts") or {}).get("videos") or []
        frames = extract_clip_frames(
            videos,
            frame_dir=run_dir / "frames" / f"{sample_id}-attempt-{attempt}",
        )
        sheet = make_contact_sheet(
            frames,
            run_dir / "frames" / f"{sample_id}-attempt-{attempt}-contact-sheet.jpg",
        )
        return frames, sheet, None
    except Exception as exc:  # noqa: BLE001 - evidence records failure
        return [], None, f"{type(exc).__name__}: {exc}"


def _base_live_report(args: argparse.Namespace, samples: list[dict[str, Any]]) -> dict:
    return {
        "contract_version": 1,
        "mode": "live-10",
        "run_id": args.run_id,
        "api_url": args.api_url,
        "episode_id": args.episode_id,
        "script_id": args.script_id,
        "sample_count": args.sample_count,
        "duration_plan": args.duration_plan,
        "video_concurrency": args.video_concurrency,
        "samples": samples,
        "aggregate": aggregate_quality_report(
            samples,
            expected_sample_count=args.sample_count,
        ),
    }


def _write_provider_log(
    run_dir: Path,
    sample_id: str,
    attempt: int,
    command: list[str],
    completed: subprocess.CompletedProcess[str],
) -> Path:
    log_path = run_dir / f"{sample_id}-attempt-{attempt}-provider-chain.log"
    log_path.write_text(
        f"$ {' '.join(command)}\n\nSTDOUT:\n{completed.stdout}\n\n"
        f"STDERR:\n{completed.stderr}\n",
        encoding="utf-8",
    )
    return log_path


def _subprocess_summary(
    completed: subprocess.CompletedProcess[str], log_path: Path, started: float
) -> dict[str, Any]:
    return {
        "returncode": completed.returncode,
        "log_path": str(log_path),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
