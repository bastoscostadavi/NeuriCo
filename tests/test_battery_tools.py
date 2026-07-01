"""Tests for Battery Lab manager tools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from interactive.research_state import ResearchState  # noqa: E402
from interactive.session_state import SessionState  # noqa: E402
from interactive.tools import ToolExecutor  # noqa: E402


class DummyChannel:
    def __init__(self):
        self.messages = []

    def send(self, text, kind="manager", meta=None):
        self.messages.append((kind, text, meta or {}))

    def prompt(self, message=None, options=None):
        return "results are ready"

    def poll_input(self, timeout=0.0):
        return None


def _executor(tmp_path):
    session = SessionState(tmp_path, "battery-idea", "Battery idea", "claude")
    research = ResearchState(tmp_path)
    return ToolExecutor(
        work_dir=tmp_path,
        session=session,
        idea_file=tmp_path / "idea.yaml",
        provider="claude",
        project_root=tmp_path,
        channel=DummyChannel(),
        research=research,
    )


def test_ingest_results_records_structured_summary_and_raw_files(tmp_path):
    results = tmp_path / "BL-results" / "round-1"
    results.mkdir(parents=True)
    (results / "summary.json").write_text(json.dumps({
        "recipe_name": "wa_ladder_cell_01",
        "measurement_type": "ionic_conductivity",
        "ionic_conductivity_mS_cm": 12.4,
        "bulk_resistance_ohm": 18.7,
        "temperature_C": 25,
        "source_files": ["eis.csv", "nyquist.png"],
        "fit_model": "Rb + CPE",
        "quality_flag": "ok",
        "notes": "single clean high-frequency intercept",
    }))
    (results / "nyquist.png").write_bytes(b"fake png")

    ex = _executor(tmp_path)
    out = ex.execute("ingest_results", {"path": "BL-results"})

    assert "Ingested structured wet-lab result records" in out
    assert "Raw files found: 1" in out
    findings = ex.research.state["findings"]
    assert any("wa_ladder_cell_01" in f["text"] and f["kind"] == "result" for f in findings)
    assert any("raw files available" in f["text"] and f["kind"] == "note" for f in findings)
    assert ex.research.state["current_best"].startswith("1 wet-lab result record")
    assert ex.session.state["phase"] == "wet_lab_results_ingested"


def test_ingest_results_reports_malformed_summary(tmp_path):
    results = tmp_path / "BL-results"
    results.mkdir()
    (results / "summary.json").write_text("{not json")

    ex = _executor(tmp_path)
    out = ex.execute("ingest_results", {"path": "BL-results"})

    assert "No structured JSON/JSONL result records were ingested." in out
    assert "invalid JSON" in out
    assert ex.research.state["findings"] == []
