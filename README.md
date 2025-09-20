# 🚀 Evaluation Harness für Text-Vereinfachung

Eine professionelle, modulare Evaluation-Pipeline für die Bewertung von Modellen zur deutschen Text-Vereinfachung.

## ✨ Features

- 🎯 **Umfassende Metriken**: SARI, Flesch-Deutsch, LIX, WSTF, Basisstatistiken
- 📊 **Statistische Analyse**: Signifikanz-Tests, Effektgrößen, Bootstrap-Konfidenzintervalle
- 🔄 **Caching**: Reproduzierbare Ergebnisse durch intelligentes Caching
- ⚙️ **Flexible Konfiguration**: YAML-basierte Konfiguration für Tasks und Modelle
- 📈 **Detaillierte Reports**: Markdown + JSON Ausgabe mit Visualisierungen
- 🧪 **Unit Tests**: Vollständige Test-Abdeckung
- 📦 **Einfache Installation**: Ein-Klick Setup

## 🛠️ Installation

### Voraussetzungen
- Python 3.8+
- CUDA-fähige GPU (empfohlen)
- 8GB+ RAM

### Schnellstart
```bash
# Repository klonen
git clone <repository-url>
cd evaluation_harness

# Abhängigkeiten installieren
pip install -r requirements.txt

# Evaluation ausführen
python evaluate.py --help
```

### Manuelle Installation
```bash
pip install torch transformers numpy scipy pyyaml matplotlib seaborn tqdm
```

## 🚀 Verwendung

### Grundlegende Evaluation
```bash
python evaluate.py --task configs/tasks/simplify_de.yaml \
                   --models configs/models/base_phi4.yaml \
                           configs/models/finetuned_klexikon.yaml \
                   --config configs/default.yaml
```

### Erweiterte Optionen
```bash
python evaluate.py \
    --task configs/tasks/simplify_de.yaml \
    --models configs/models/base_phi4.yaml configs/models/finetuned_klexikon.yaml \
    --config configs/default.yaml \
    --verbose \
    --output outputs/custom_eval \
    --max-samples 50
```

### CLI-Optionen
- `--task`: Task-Konfigurationsdatei
- `--models`: Liste der Modell-Konfigurationsdateien
- `--config`: Haupt-Konfigurationsdatei
- `--verbose`: Detaillierte Ausgabe
- `--quiet`: Minimale Ausgabe
- `--output`: Ausgabeverzeichnis
- `--max-samples`: Maximale Anzahl Testbeispiele
- `--dry-run`: Simulation ohne echte Evaluation

## 📁 Projektstruktur

```
evaluation_harness/
├── src/                    # Haupt-Code
│   ├── models.py          # Modell-Adapter
│   ├── tasks.py           # Task-Management
│   ├── metrics/           # Metriken
│   │   ├── registry.py    # Metriken-Registry
│   │   ├── sari.py        # SARI-Metrik
│   │   └── readability_de.py # Deutsche Lesbarkeits-Metriken
│   ├── stats.py           # Statistische Tests
│   ├── report.py          # Report-Generierung
│   ├── caching.py         # Caching-System
│   └── decoding.py        # Decoding-Strategien
├── configs/               # Konfigurationsdateien
│   ├── default.yaml       # Standard-Konfiguration
│   ├── models/            # Modell-Konfigurationen
│   └── tasks/             # Task-Konfigurationen
├── data/                  # Test-Daten
├── outputs/               # Ausgabe-Ordner
├── tests/                 # Unit Tests
├── evaluate.py           # Haupt-Script
├── requirements.txt      # Abhängigkeiten
└── README.md            # Diese Datei
```

## 📊 Metriken

### Text-Vereinfachung
- **SARI**: System for Automatic Readability Index
- **Flesch-Deutsch**: Deutsche Version des Flesch-Index
- **LIX**: Lesbarkeitsindex
- **WSTF**: Wiener Sachtextformel

### Basisstatistiken
- Durchschnittliche Satzlänge
- Durchschnittliche Wortlänge
- Komplexitäts-Verhältnis
- Wort-/Satz-/Zeichenanzahl

## 📈 Ausgabe

### Markdown-Report (`outputs/report.md`)
- Zusammenfassung der Ergebnisse
- Detaillierte Metriken-Vergleiche
- Statistische Signifikanz-Tests
- Interpretation der Ergebnisse

### JSON-Daten (`outputs/detailed_results.json`)
- Vollständige Rohdaten
- Metriken pro Modell
- Statistische Tests
- Konfidenzintervalle

### Visualisierungen (`outputs/plots/`)
- Vergleichsdiagramme
- Metriken-Distributionen
- Signifikanz-Plots

## ⚙️ Konfiguration

### Task-Konfiguration
```yaml
task_name: simplify_de
data:
  test_file: data/test.jsonl
  dev_file: data/dev.jsonl
prompt:
  template: |
    Vereinfache den folgenden deutschen Text in einfacher Sprache (A2-B1).
    Verwende kurze Sätze und vermeide Fremdwörter.

    Text: {source}

    Vereinfachter Text:
```

### Modell-Konfiguration
```yaml
model_id: microsoft/phi-4-mini-instruct
adapter: null
```

### Haupt-Konfiguration
```yaml
seed: 42
max_new_tokens: 160
batch_size: 1
output_dir: outputs
cache_dir: .cache

decoding:
  name: greedy
  do_sample: false
  temperature: 0.0
  top_p: 1.0
```

## 🧪 Tests

```bash
# Alle Tests ausführen
python -m pytest tests/ -v

# Mit Coverage
python -m pytest tests/ --cov=src --cov-report=html

# Spezifische Tests
python -m pytest tests/test_metrics.py -v
```

## 🔧 Entwicklung

### Neue Metriken hinzufügen
```python
# In src/metrics/registry.py
reg.register('NEUE_METRIK', lambda src, hyp, refs: neue_metrik_funktion(hyp))
```

### Neue Tasks hinzufügen
1. Task-Konfiguration in `configs/tasks/` erstellen
2. Datenformat in `data/` bereitstellen
3. Prompt-Template definieren

### Neue Modelle hinzufügen
1. Modell-Konfiguration in `configs/models/` erstellen
2. Bei Bedarf `ModelAdapter` erweitern

## 📊 Beispiel-Ergebnisse

```
============================================================
EVALUATION ZUSAMMENFASSUNG
============================================================
Task: simplify_de
Modelle: microsoft/phi-4-mini-instruct vs /path/to/finetuned-model
Beispiele: 50
Metriken: 10

SIGNIFIKANTE VERBESSERUNGEN:
  FLESCH_DE: +5.234 (p=0.0234)
  LIX: -3.456 (p=0.0123)

SIGNIFIKANTE VERSCHLECHTERUNGEN:
  SARI: -0.123 (p=0.0456)
```

## 🐛 Troubleshooting

### Häufige Probleme

**CUDA Out of Memory**
```bash
# Batch-Size reduzieren oder CPU verwenden
# In configs/default.yaml:
batch_size: 1
```

**Model Loading Fehler**
```bash
# Modell-Pfad überprüfen
# In configs/models/:
model_id: /korrekter/pfad/zum/modell
```

**YAML Syntax Fehler**
```bash
# YAML-Validierung verwenden
python -c "import yaml; yaml.safe_load(open('configs/default.yaml'))"
```

## 🤝 Beitragen

1. Fork des Repositories
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` für Details.

## 🙏 Danksagungen

- Transformers Library von Hugging Face
- SciPy für statistische Tests
- NumPy für numerische Berechnungen

## 📞 Support

Bei Fragen oder Problemen:
- Issue im Repository erstellen
- Dokumentation durchsuchen
- Code-Beispiele in `examples/` ansehen

---

**Version**: 1.0.0  
**Letztes Update**: 2024-09-20  
**Python**: 3.8+
