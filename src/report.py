import os, json
from typing import Dict, Any


def write_markdown(out_dir: str, summary: dict, per_metric: dict):
    """Generiert einen detaillierten Markdown-Report der Evaluation"""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "report.md")

    lines = ["# Evaluation Report", ""]

    # Zusammenfassung
    lines.append("## Zusammenfassung")
    lines.append("")
    for k, v in summary.items():
        if isinstance(v, list):
            if len(v) == 0:
                lines.append(f"- **{k}**: Keine")
            else:
                lines.append(f"- **{k}**: {', '.join(map(str, v))}")
        else:
            lines.append(f"- **{k}**: {v}")

    lines.append("")
    lines.append("## Detaillierte Metriken-Vergleiche")
    lines.append("")

    # Für jede Metrik detaillierte Statistiken
    for metric_name, stats in per_metric.items():
        lines.append(f"### {metric_name}")
        lines.append("")

        # Basis-Statistiken
        lines.append(f"- **Modell A Mittelwert**: {stats['model_a_mean']:.4f}")
        lines.append(f"- **Modell B Mittelwert**: {stats['model_b_mean']:.4f}")
        lines.append(
            f"- **Differenz (B - A)**: {stats['model_b_mean'] - stats['model_a_mean']:+.4f}"
        )
        lines.append(f"- **Anzahl Samples**: {stats['n_samples']}")

        # Statistische Tests
        if "paired_t_test" in stats:
            t_test = stats["paired_t_test"]
            lines.append(f"- **t-Statistik**: {t_test['t']:.4f}")
            lines.append(f"- **p-Wert (t-Test)**: {t_test['tp']:.4f}")
            lines.append(f"- **Wilcoxon W**: {t_test['w']:.4f}")
            lines.append(f"- **p-Wert (Wilcoxon)**: {t_test['wp']:.4f}")

        # Effektgröße
        if "cohens_d" in stats and not (
            isinstance(stats["cohens_d"], float) and str(stats["cohens_d"]) == "nan"
        ):
            cohens_d_val = stats["cohens_d"]
            effect_size_desc = (
                "klein"
                if abs(cohens_d_val) < 0.2
                else "mittel" if abs(cohens_d_val) < 0.5 else "groß"
            )
            lines.append(f"- **Cohen's d**: {cohens_d_val:.4f} ({effect_size_desc})")

        # Bootstrap Konfidenzintervall
        if "bootstrap_ci" in stats:
            ci_lo, ci_hi = stats["bootstrap_ci"]
            lines.append(f"- **95% CI (Bootstrap)**: [{ci_lo:.4f}, {ci_hi:.4f}]")

        # Signifikanz-Bewertung
        if "paired_t_test" in stats and "tp" in stats["paired_t_test"]:
            p_val = stats["paired_t_test"]["tp"]
            if not (isinstance(p_val, float) and str(p_val) == "nan"):
                significance = "signifikant" if p_val < 0.05 else "nicht signifikant"
                lines.append(f"- **Signifikanz**: {significance} (α = 0.05)")

        lines.append("")

        # Raw JSON für Details
        lines.append("```json")
        lines.append(json.dumps(stats, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    # Zusätzliche Sektionen
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- **Signifikante Verbesserungen**: Metriken mit p < 0.05 und positiver Differenz"
    )
    lines.append(
        "- **Signifikante Verschlechterungen**: Metriken mit p < 0.05 und negativer Differenz"
    )
    lines.append(
        "- **Cohen's d**: 0.2 = kleiner Effekt, 0.5 = mittlerer Effekt, 0.8 = großer Effekt"
    )
    lines.append("")

    # Timestamp
    from datetime import datetime

    lines.append(f"**Generiert am**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path
