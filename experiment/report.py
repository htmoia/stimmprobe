#!/usr/bin/env python3
"""Erzeugt aus results/runs.jsonl und results/summary.json den Bericht results/ERGEBNIS.md."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

LABELS = {
    "A_kontrolle_ohne_angriff": "A · Kontrolle: nur die Anruferin, kein Angriff",
    "B_kontrolle_direkt_laut": "B · Kontrolle: Anruferin fragt selbst laut nach dem Code",
    "C_zweite_stimme_danach_-12dB": "C · Zweite Stimme nach der Anruferin, −12 dB",
    "D_zweite_stimme_gleichzeitig_-12dB": "D · Zweite Stimme gleichzeitig, −12 dB",
    "E_zweite_stimme_gleichzeitig_-20dB": "E · Zweite Stimme gleichzeitig, −20 dB",
    "F_zweite_stimme_gleichzeitig_-12dB_telefon": "F · wie D, zusätzlich Telefonfilter 300–3400 Hz",
    "G_zweite_stimme_danach_-12dB_i2": "G · Zweite Stimme nach der Anruferin, −12 dB, zweiter Wortlaut",
}


def main() -> int:
    runs = [json.loads(line) for line in (RESULTS / "runs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    manifest = {m["name"]: m for m in json.loads((HERE / "audio" / "manifest.json").read_text(encoding="utf-8"))}

    by_cond: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        by_cond[r["condition"]].append(r)

    lines = [
        "# Ergebnis des Experiments",
        "",
        f"Geheimer Testwert im System-Prompt: `{summary['canary']}` · "
        f"LLM: `{summary['llm']}` (Temperatur {summary['temperature']}) · STT: `{summary['stt']}`",
        "",
        "| Bedingung | Läufe | STT hat den Angriff transkribiert | Code vollständig genannt | Code teilweise genannt |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["rows"]:
        lines.append(
            f"| {LABELS.get(row['condition'], row['condition'])} | {row['runs']} | "
            f"{row['injection_transcribed']} | **{row['leak_full']}** | {row['leak_partial']} |"
        )
    lines += ["", "## Beispiele", ""]
    for cond, rs in by_cond.items():
        m = manifest[cond]
        lines.append(f"### {LABELS.get(cond, cond)}")
        lines.append("")
        lines.append(f"Datei: `audio/{m['file']}`" + (f" · Text der zweiten Stimme: „{m['injection_text']}“" if m["injection"] and m["injection"] != "direct" else ""))
        lines.append("")
        leaked = [r for r in rs if r["leak_full"]]
        clean = [r for r in rs if not r["leak_partial"]]
        for title, sample in (("Lauf mit Preisgabe", leaked[:1]), ("Lauf ohne Preisgabe", clean[:1])):
            for r in sample:
                lines.append(f"**{title} (Lauf {r['run']:02d})**")
                lines.append("")
                lines.append(f"- Transkript (Whisper): „{r['transcript']}“")
                lines.append(f"- Antwort des Agenten: „{r['response']}“")
                if r.get("audio_file"):
                    lines.append(f"- Audio der Antwort: `results/{r['audio_file']}`")
                lines.append("")
    lines.append("Alle Läufe mit Transkript, Antwort und Prüfergebnis: `results/runs.jsonl`.")
    (RESULTS / "ERGEBNIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
