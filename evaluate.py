import argparse, os, yaml, json, sys
import numpy as np
from pathlib import Path
from tqdm import tqdm
import time

from src.models import ModelAdapter
from src.tasks import load_jsonl
from src.decoding import get_decoding
from src.caching import make_key, get as cache_get, put as cache_put
from src.metrics.registry import MetricsRegistry
from src.metrics.readability_de import flesch_de, lix, wstf, basic_stats
from src.metrics.sari import sari
from src.stats import paired_tests, cohens_d, bootstrap_ci, holm_correction
from src.report import write_markdown
from src.visualization import create_all_visualizations
from src.logging_config import setup_logging, get_logger

# Argument Parser mit erweiterten Optionen
parser = argparse.ArgumentParser(
    description='Evaluation Harness für Text-Vereinfachung',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Beispiele:
  python evaluate.py --task configs/tasks/simplify_de.yaml
  python evaluate.py --verbose --max-samples 100 --output results/
  python evaluate.py --dry-run --quiet
    """
)

parser.add_argument('--task', 
                   default='configs/tasks/simplify_de.yaml',
                   help='Task-Konfigurationsdatei (default: configs/tasks/simplify_de.yaml)')
parser.add_argument('--models', 
                   nargs='+', 
                   default=['configs/models/base_phi4.yaml','configs/models/finetuned_klexikon.yaml'],
                   help='Liste der Modell-Konfigurationsdateien')
parser.add_argument('--config', 
                   default='configs/default.yaml',
                   help='Haupt-Konfigurationsdatei (default: configs/default.yaml)')
parser.add_argument('--verbose', '-v',
                   action='store_true',
                   help='Detaillierte Ausgabe')
parser.add_argument('--quiet', '-q',
                   action='store_true',
                   help='Minimale Ausgabe')
parser.add_argument('--output', '-o',
                   help='Ausgabeverzeichnis (überschreibt config)')
parser.add_argument('--max-samples',
                   type=int,
                   help='Maximale Anzahl Testbeispiele')
parser.add_argument('--dry-run',
                   action='store_true',
                   help='Simulation ohne echte Evaluation')
parser.add_argument('--no-cache',
                   action='store_true',
                   help='Cache ignorieren')
parser.add_argument('--no-plots',
                   action='store_true',
                   help='Keine Plots erstellen')
parser.add_argument('--log-file',
                   help='Log-Datei spezifizieren')

args = parser.parse_args()

# Logging einrichten
logger = setup_logging(
    level=20,  # INFO level
    log_file=args.log_file,
    verbose=args.verbose,
    quiet=args.quiet
)

logger.info("="*60)
logger.info("🚀 EVALUATION HARNESS STARTET")
logger.info("="*60)


# Konfiguration laden mit Fehlerbehandlung
try:
    logger.info(f"Lade Konfiguration aus: {args.config}")
    cfg = yaml.safe_load(open(args.config))
    
    logger.info(f"Lade Task aus: {args.task}")
    task = yaml.safe_load(open(args.task))
    
    logger.info(f"Lade Modell-Konfigurationen: {args.models}")
    model_cfgs = [yaml.safe_load(open(p)) for p in args.models]
    
    # CLI-Argumente überschreiben Konfiguration
    if args.output:
        cfg['output_dir'] = args.output
    if args.max_samples:
        cfg['max_samples'] = args.max_samples
    
    logger.info(f"Konfiguration geladen: {len(model_cfgs)} Modelle, Task: {task.get('task_name', 'unknown')}")
    
except Exception as e:
    logger.error(f"Fehler beim Laden der Konfiguration: {e}")
    sys.exit(1)

# Ausgabeverzeichnis erstellen
output_dir = cfg['output_dir']
os.makedirs(output_dir, exist_ok=True)
logger.info(f"Ausgabeverzeichnis: {output_dir}")

# Dry-Run Modus
if args.dry_run:
    logger.info("🔍 DRY-RUN MODUS - Keine echte Evaluation")
    logger.info(f"Würde {len(model_cfgs)} Modelle evaluieren")
    logger.info(f"Task: {task.get('task_name', 'unknown')}")
    logger.info(f"Konfiguration: {cfg}")
    sys.exit(0)


# Registry aufsetzen
reg = MetricsRegistry()
reg.register('SARI', lambda src, hyp, refs: sari(src, hyp, refs))
reg.register('FLESCH_DE', lambda src, hyp, refs: flesch_de(hyp))
reg.register('LIX', lambda src, hyp, refs: lix(hyp))
reg.register('WSTF', lambda src, hyp, refs: wstf(hyp))

# Basisstatistiken werden separat behandelt


# Basisstatistiken werden separat geloggt


def build_prompt(template: str, source: str) -> str:
    return template.format(source=source)


# Daten laden
logger.info(f"Lade Test-Daten aus: {task['data']['test_file']}")
try:
    examples = load_jsonl(task['data']['test_file'])
    logger.info(f"{len(examples)} Testbeispiele geladen")
    
    # Maximale Anzahl Samples begrenzen
    if 'max_samples' in cfg and cfg['max_samples'] < len(examples):
        examples = examples[:cfg['max_samples']]
        logger.info(f"Begrenzt auf {len(examples)} Beispiele")
        
except Exception as e:
    logger.error(f"Fehler beim Laden der Daten: {e}")
    sys.exit(1)

# Modelle laden
logger.info("Lade Modelle...")
adapters = []
for i, mc in enumerate(model_cfgs):
    try:
        logger.info(f"Lade Modell {i+1}/{len(model_cfgs)}: {mc['model_id']}")
        adapter = ModelAdapter(mc['model_id'])
        adapters.append((mc['model_id'], adapter))
    except Exception as e:
        logger.error(f"Fehler beim Laden von Modell {mc['model_id']}: {e}")
        sys.exit(1)

logger.info(f"Alle {len(adapters)} Modelle erfolgreich geladen")

# Generierung & Caching
results = {model_id: [] for model_id, _ in adapters}

logger.info("Starte Evaluation...")
total_examples = len(examples)
total_models = len(adapters)
total_tasks = total_examples * total_models

# Progress Bar für gesamte Evaluation
with tqdm(total=total_tasks, desc="Evaluation", unit="Beispiel") as pbar:
    for ex_idx, ex in enumerate(examples):
        for model_id, adapter in adapters:
            try:
                prompt = build_prompt(task['prompt']['template'], ex['source'])
                decoding = get_decoding(cfg['decoding'], seed=cfg['seed'])
                key = make_key(model_id, decoding, prompt, ex['id'])
                
                # Cache prüfen (außer wenn --no-cache gesetzt)
                cached = None
                if not args.no_cache:
                    cached = cache_get(cfg['cache_dir'], key)
                
                if cached is None:
                    logger.debug(f"Generiere für {model_id}, Beispiel {ex['id']}")
                    hyp = adapter.generate(prompt, cfg['max_new_tokens'], decoding)
                    cached = {"id": ex['id'], "source": ex['source'], "hyp": hyp, "refs": ex.get('refs', [])}
                    
                    # Cache speichern (außer wenn --no-cache gesetzt)
                    if not args.no_cache:
                        cache_put(cfg['cache_dir'], key, cached)
                else:
                    logger.debug(f"Cache-Hit für {model_id}, Beispiel {ex['id']}")
                
                results[model_id].append(cached)
                
            except Exception as e:
                logger.error(f"Fehler bei Beispiel {ex['id']}, Modell {model_id}: {e}")
                # Dummy-Eintrag für fehlgeschlagene Generation
                results[model_id].append({
                    "id": ex['id'], 
                    "source": ex['source'], 
                    "hyp": "", 
                    "refs": ex.get('refs', [])
                })
            
            pbar.update(1)

logger.info("Evaluation abgeschlossen")


# Metriken berechnen
metrics_per_model = {mid: {name: [] for name in reg.names()} for mid, _ in adapters}
statlog_per_model = {mid: [] for mid, _ in adapters}

# Basisstatistiken separat sammeln
basic_stats_per_model = {mid: {name: [] for name in ['avg_sentence_length', 'avg_word_length', 'complex_word_ratio', 'sentence_count', 'word_count', 'character_count']} for mid, _ in adapters}

for mid, rows in results.items():
    for r in rows:
        # Registry-Metriken
        ms = reg.compute_all(r['source'], r['hyp'], r['refs'])
        for name, value in ms.items():
            if name in metrics_per_model[mid]:
                metrics_per_model[mid][name].append(value)
        
        # Basisstatistiken
        bs = basic_stats(r['hyp'])
        for name, value in bs.items():
            if name in basic_stats_per_model[mid]:
                basic_stats_per_model[mid][name].append(value)
        
        # Für Statlog alle Metriken zusammenfassen
        all_metrics = {**ms, **bs}
        statlog_per_model[mid].append({"id": r['id'], **all_metrics})


# Vergleich: Modell 0 vs. 1
mid_a, mid_b = adapters[0][0], adapters[1][0]

# Statistische Vergleiche durchführen
comparison_results = {}
summary_stats = {}

# Alle Metriken (Registry + Basisstatistiken) vergleichen
all_metrics = {}
for mid, _ in adapters:
    all_metrics[mid] = {**metrics_per_model[mid], **basic_stats_per_model[mid]}

# Vergleiche für alle Metriken
all_metric_names = set()
for mid, _ in adapters:
    all_metric_names.update(all_metrics[mid].keys())

for metric_name in all_metric_names:
    if metric_name in all_metrics[mid_a] and metric_name in all_metrics[mid_b]:
        values_a = [v for v in all_metrics[mid_a][metric_name] if v is not None]
        values_b = [v for v in all_metrics[mid_b][metric_name] if v is not None]
        
        if len(values_a) > 0 and len(values_b) > 0:
            # Paired Tests
            paired_result = paired_tests(values_a, values_b)
            
            # Cohen's d
            effect_size = cohens_d(values_a, values_b)
            
            # Bootstrap CI für Differenzen
            diffs = [b - a for a, b in zip(values_a, values_b)]
            ci_lo, ci_hi = bootstrap_ci(diffs)
            
            comparison_results[metric_name] = {
                'model_a_mean': sum(values_a) / len(values_a),
                'model_b_mean': sum(values_b) / len(values_b),
                'paired_t_test': paired_result,
                'cohens_d': effect_size,
                'bootstrap_ci': [ci_lo, ci_hi],
                'n_samples': len(values_a)
            }
            
            summary_stats[metric_name] = {
                'model_a': mid_a,
                'model_b': mid_b,
                'mean_difference': comparison_results[metric_name]['model_b_mean'] - comparison_results[metric_name]['model_a_mean'],
                'p_value': paired_result['tp'],
                'significant': paired_result['tp'] < 0.05 if not np.isnan(paired_result['tp']) else False,
                'effect_size': effect_size
            }

# Zusammenfassung erstellen
summary = {
    'task': task['task_name'],
    'models_compared': [mid_a, mid_b],
    'n_examples': len(examples),
    'metrics_evaluated': list(comparison_results.keys()),
    'significant_improvements': [m for m, stats in summary_stats.items() if stats['significant'] and stats['mean_difference'] > 0],
    'significant_degradations': [m for m, stats in summary_stats.items() if stats['significant'] and stats['mean_difference'] < 0]
}

# Visualisierungen erstellen
plot_paths = []
if not args.no_plots:
    logger.info("Erstelle Visualisierungen...")
    try:
        plot_paths = create_all_visualizations(comparison_results, all_metrics, output_dir)
        logger.info(f"Visualisierungen erstellt: {len(plot_paths)} Plots")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Visualisierungen: {e}")

# Report generieren
logger.info("Generiere Reports...")
try:
    rep_path = write_markdown(output_dir, summary, comparison_results)
    logger.info(f"Markdown-Report erstellt: {rep_path}")
except Exception as e:
    logger.error(f"Fehler beim Erstellen des Markdown-Reports: {e}")
    rep_path = None

# Ergebnisse als JSON speichern
results_path = os.path.join(output_dir, 'detailed_results.json')
try:
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': summary,
            'detailed_comparisons': comparison_results,
            'per_model_metrics': all_metrics,
            'statlog_data': statlog_per_model,
            'plot_paths': plot_paths,
            'evaluation_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'args': vars(args)
        }, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Detaillierte Ergebnisse gespeichert: {results_path}")
except Exception as e:
    logger.error(f"Fehler beim Speichern der JSON-Ergebnisse: {e}")

# Zusammenfassung ausgeben
logger.info("="*60)
logger.info("📊 EVALUATION ZUSAMMENFASSUNG")
logger.info("="*60)
logger.info(f"Task: {task['task_name']}")
logger.info(f"Modelle: {mid_a} vs {mid_b}")
logger.info(f"Beispiele: {len(examples)}")
logger.info(f"Metriken: {len(comparison_results)}")

if summary['significant_improvements']:
    logger.info("\n✅ SIGNIFIKANTE VERBESSERUNGEN:")
    for metric in summary['significant_improvements']:
        diff = summary_stats[metric]['mean_difference']
        p_val = summary_stats[metric]['p_value']
        logger.info(f"  {metric}: +{diff:.3f} (p={p_val:.4f})")
else:
    logger.info("\n✅ Keine signifikanten Verbesserungen")

if summary['significant_degradations']:
    logger.info("\n❌ SIGNIFIKANTE VERSCHLECHTERUNGEN:")
    for metric in summary['significant_degradations']:
        diff = summary_stats[metric]['mean_difference']
        p_val = summary_stats[metric]['p_value']
        logger.info(f"  {metric}: {diff:.3f} (p={p_val:.4f})")
else:
    logger.info("\n❌ Keine signifikanten Verschlechterungen")

logger.info(f"\n📄 Vollständiger Report: {rep_path}")
logger.info(f"📊 Detaillierte Ergebnisse: {results_path}")
if plot_paths:
    logger.info(f"📈 Visualisierungen: {len(plot_paths)} Plots erstellt")

logger.info("="*60)
logger.info("🎉 EVALUATION ERFOLGREICH ABGESCHLOSSEN")
logger.info("="*60)