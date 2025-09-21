import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from .logging_config import get_logger

logger = get_logger("visualization")

# Setze Style für bessere Plots
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def create_metrics_comparison_plot(comparison_results: Dict, output_dir: str) -> str:
    """Erstellt Vergleichsdiagramme für alle Metriken"""

    # Ausgabeverzeichnis erstellen
    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Daten für Plot vorbereiten
    metrics = []
    model_a_scores = []
    model_b_scores = []
    differences = []
    p_values = []

    for metric_name, stats in comparison_results.items():
        metrics.append(metric_name)
        model_a_scores.append(stats["model_a_mean"])
        model_b_scores.append(stats["model_b_mean"])
        differences.append(stats["model_b_mean"] - stats["model_a_mean"])

        p_val = stats["paired_t_test"]["tp"]
        if np.isnan(p_val):
            p_val = 1.0  # Nicht signifikant wenn NaN
        p_values.append(p_val)

    # Farben basierend auf Signifikanz
    colors = ["red" if p < 0.05 else "lightgray" for p in p_values]

    # Plot erstellen
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Subplot 1: Balkendiagramm der Mittelwerte
    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax1.bar(
        x - width / 2,
        model_a_scores,
        width,
        label="Modell A",
        alpha=0.8,
        color="skyblue",
    )
    bars2 = ax1.bar(
        x + width / 2,
        model_b_scores,
        width,
        label="Modell B",
        alpha=0.8,
        color="lightcoral",
    )

    ax1.set_xlabel("Metriken")
    ax1.set_ylabel("Wert")
    ax1.set_title("Metriken-Vergleich: Modell A vs. Modell B")
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45, ha="right")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Werte auf Balken anzeigen
    for bar in bars1:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    for bar in bars2:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # Subplot 2: Differenzen mit Signifikanz
    bars = ax2.bar(metrics, differences, color=colors, alpha=0.7)
    ax2.axhline(y=0, color="black", linestyle="-", alpha=0.3)
    ax2.set_xlabel("Metriken")
    ax2.set_ylabel("Differenz (Modell B - Modell A)")
    ax2.set_title("Differenzen mit Signifikanz-Tests\n(Rot = p < 0.05)")
    ax2.set_xticklabels(metrics, rotation=45, ha="right")
    ax2.grid(True, alpha=0.3)

    # p-Werte als Text anzeigen
    for i, (bar, p_val) in enumerate(zip(bars, p_values)):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + (0.01 if height >= 0 else -0.01),
            f"p={p_val:.3f}",
            ha="center",
            va="bottom" if height >= 0 else "top",
            fontsize=8,
            fontweight="bold" if p_val < 0.05 else "normal",
        )

    plt.tight_layout()

    # Speichern
    plot_path = plots_dir / "metrics_comparison.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    logger.info(f"Metriken-Vergleichsplot gespeichert: {plot_path}")
    return str(plot_path)


def create_correlation_heatmap(all_metrics: Dict, output_dir: str) -> str:
    """Erstellt Korrelations-Heatmap zwischen Metriken"""

    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Daten für beide Modelle sammeln
    model_a_data = {}
    model_b_data = {}

    for model_id, metrics in all_metrics.items():
        if "phi-4-mini-instruct" in model_id:  # Modell A
            model_a_data = metrics
        else:  # Modell B
            model_b_data = metrics

    # DataFrames erstellen
    df_a = pd.DataFrame(model_a_data)
    df_b = pd.DataFrame(model_b_data)

    # Korrelationsmatrizen berechnen
    corr_a = df_a.corr()
    corr_b = df_b.corr()

    # Plots erstellen
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Modell A Korrelation
    sns.heatmap(
        corr_a,
        annot=True,
        cmap="coolwarm",
        center=0,
        square=True,
        ax=ax1,
        fmt=".2f",
        cbar_kws={"shrink": 0.8},
    )
    ax1.set_title("Korrelations-Matrix: Modell A")

    # Modell B Korrelation
    sns.heatmap(
        corr_b,
        annot=True,
        cmap="coolwarm",
        center=0,
        square=True,
        ax=ax2,
        fmt=".2f",
        cbar_kws={"shrink": 0.8},
    )
    ax2.set_title("Korrelations-Matrix: Modell B")

    plt.tight_layout()

    # Speichern
    plot_path = plots_dir / "correlation_heatmap.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    logger.info(f"Korrelations-Heatmap gespeichert: {plot_path}")
    return str(plot_path)


def create_distribution_plots(all_metrics: Dict, output_dir: str) -> str:
    """Erstellt Verteilungsplots für wichtige Metriken"""

    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Wichtige Metriken für Verteilungsplots
    key_metrics = ["FLESCH_DE", "LIX", "SARI", "avg_sentence_length", "word_count"]

    # Verfügbare Metriken filtern
    available_metrics = [
        m for m in key_metrics if any(m in metrics for metrics in all_metrics.values())
    ]

    if not available_metrics:
        logger.warning("Keine passenden Metriken für Verteilungsplots gefunden")
        return ""

    # Plots erstellen
    n_metrics = len(available_metrics)
    cols = min(3, n_metrics)
    rows = (n_metrics + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    if rows == 1:
        axes = [axes] if cols == 1 else axes
    else:
        axes = axes.flatten()

    for i, metric in enumerate(available_metrics):
        ax = axes[i]

        # Daten sammeln
        model_a_data = []
        model_b_data = []

        for model_id, metrics in all_metrics.items():
            if metric in metrics:
                if "phi-4-mini-instruct" in model_id:
                    model_a_data = metrics[metric]
                else:
                    model_b_data = metrics[metric]

        # Plots erstellen
        if model_a_data and model_b_data:
            ax.hist(model_a_data, alpha=0.7, label="Modell A", bins=10, color="skyblue")
            ax.hist(
                model_b_data, alpha=0.7, label="Modell B", bins=10, color="lightcoral"
            )
            ax.set_title(f"Verteilung: {metric}")
            ax.set_xlabel(metric)
            ax.set_ylabel("Häufigkeit")
            ax.legend()
            ax.grid(True, alpha=0.3)

    # Leere Subplots verstecken
    for i in range(len(available_metrics), len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()

    # Speichern
    plot_path = plots_dir / "distributions.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    logger.info(f"Verteilungsplots gespeichert: {plot_path}")
    return str(plot_path)


def create_effect_size_plot(comparison_results: Dict, output_dir: str) -> str:
    """Erstellt Effektgrößen-Plot"""

    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Daten sammeln
    metrics = []
    effect_sizes = []
    p_values = []

    for metric_name, stats in comparison_results.items():
        cohens_d = stats["cohens_d"]
        p_val = stats["paired_t_test"]["tp"]

        if not np.isnan(cohens_d) and not np.isnan(p_val):
            metrics.append(metric_name)
            effect_sizes.append(cohens_d)
            p_values.append(p_val)

    if not metrics:
        logger.warning("Keine gültigen Effektgrößen für Plot gefunden")
        return ""

    # Plot erstellen
    fig, ax = plt.subplots(figsize=(12, 8))

    # Farben basierend auf Signifikanz und Effektgröße
    colors = []
    for p_val, effect in zip(p_values, effect_sizes):
        if p_val < 0.05:
            if abs(effect) >= 0.8:
                colors.append("darkred")  # Groß und signifikant
            elif abs(effect) >= 0.5:
                colors.append("red")  # Mittel und signifikant
            else:
                colors.append("orange")  # Klein aber signifikant
        else:
            colors.append("lightgray")  # Nicht signifikant

    # Balkendiagramm
    bars = ax.barh(metrics, effect_sizes, color=colors, alpha=0.7)

    # Referenzlinien für Effektgrößen
    ax.axvline(x=0, color="black", linestyle="-", alpha=0.3)
    ax.axvline(x=0.2, color="gray", linestyle="--", alpha=0.5, label="Kleiner Effekt")
    ax.axvline(x=-0.2, color="gray", linestyle="--", alpha=0.5)
    ax.axvline(x=0.5, color="gray", linestyle=":", alpha=0.5, label="Mittlerer Effekt")
    ax.axvline(x=-0.5, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(x=0.8, color="gray", linestyle="-.", alpha=0.5, label="Großer Effekt")
    ax.axvline(x=-0.8, color="gray", linestyle="-.", alpha=0.5)

    ax.set_xlabel("Cohen's d (Effektgröße)")
    ax.set_ylabel("Metriken")
    ax.set_title(
        "Effektgrößen-Vergleich\n(Farbe = Signifikanz, Linien = Effektgrößen-Referenzen)"
    )
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Werte als Text anzeigen
    for i, (bar, effect, p_val) in enumerate(zip(bars, effect_sizes, p_values)):
        width = bar.get_width()
        ax.text(
            width + (0.01 if width >= 0 else -0.01),
            bar.get_y() + bar.get_height() / 2,
            f"d={effect:.2f}\np={p_val:.3f}",
            ha="left" if width >= 0 else "right",
            va="center",
            fontsize=8,
        )

    plt.tight_layout()

    # Speichern
    plot_path = plots_dir / "effect_sizes.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    logger.info(f"Effektgrößen-Plot gespeichert: {plot_path}")
    return str(plot_path)


def create_all_visualizations(
    comparison_results: Dict, all_metrics: Dict, output_dir: str
) -> List[str]:
    """Erstellt alle Visualisierungen"""

    logger.info("Erstelle Visualisierungen...")

    plot_paths = []

    try:
        # Metriken-Vergleich
        path = create_metrics_comparison_plot(comparison_results, output_dir)
        if path:
            plot_paths.append(path)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Metriken-Vergleichsplots: {e}")

    try:
        # Korrelations-Heatmap
        path = create_correlation_heatmap(all_metrics, output_dir)
        if path:
            plot_paths.append(path)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Korrelations-Heatmap: {e}")

    try:
        # Verteilungsplots
        path = create_distribution_plots(all_metrics, output_dir)
        if path:
            plot_paths.append(path)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Verteilungsplots: {e}")

    try:
        # Effektgrößen-Plot
        path = create_effect_size_plot(comparison_results, output_dir)
        if path:
            plot_paths.append(path)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Effektgrößen-Plots: {e}")

    logger.info(f"Visualisierungen erstellt: {len(plot_paths)} Plots")
    return plot_paths
