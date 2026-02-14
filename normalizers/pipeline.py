#!/usr/bin/env python3
"""Shared pipeline infrastructure for normalizers."""

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GeneResult:
    symbol: str
    status: str  # "ok", "cached", "failed", "skipped"
    detail: str = ""


@dataclass
class PipelineReport:
    source: str
    results: list[GeneResult] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)

    def ok(self, symbol: str, detail: str = ""):
        self.results.append(GeneResult(symbol, "ok", detail))

    def cached(self, symbol: str, detail: str = ""):
        self.results.append(GeneResult(symbol, "cached", detail))

    def failed(self, symbol: str, detail: str = ""):
        self.results.append(GeneResult(symbol, "failed", detail))
        print(f"  WARNING: {symbol}: {detail}", file=sys.stderr)

    def skipped(self, symbol: str, detail: str = ""):
        self.results.append(GeneResult(symbol, "skipped", detail))

    def summary(self) -> str:
        elapsed = time.time() - self.start_time
        ok = sum(1 for r in self.results if r.status == "ok")
        cached = sum(1 for r in self.results if r.status == "cached")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        lines = [
            f"{self.source}: {ok + cached} genes ({ok} fetched, {cached} cached)",
        ]
        if failed:
            lines.append(f"  {failed} FAILED: {', '.join(r.symbol for r in self.results if r.status == 'failed')}")
        if skipped:
            lines.append(f"  {skipped} skipped")
        lines.append(f"  elapsed: {elapsed:.1f}s")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "elapsed_s": round(time.time() - self.start_time, 1),
            "ok": sum(1 for r in self.results if r.status == "ok"),
            "cached": sum(1 for r in self.results if r.status == "cached"),
            "failed": sum(1 for r in self.results if r.status == "failed"),
            "failures": [{"symbol": r.symbol, "detail": r.detail}
                         for r in self.results if r.status == "failed"],
        }


def escape_cue_string(s: str | None) -> str:
    """Escape a string for CUE literal output."""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def check_staleness(cache_file: Path, max_age_days: int = 30) -> bool:
    """Return True if cache file is older than max_age_days or doesn't exist."""
    if not cache_file.exists():
        return True
    age = time.time() - cache_file.stat().st_mtime
    return age > max_age_days * 86400
