# Contributing to Evaluation Harness

Vielen Dank für Ihr Interesse, zur Evaluation Harness beizutragen! 🎉

## 🚀 Getting Started

### Voraussetzungen
- Python 3.8+
- Git
- pip oder conda

### Repository Setup
```bash
# Repository klonen
git clone https://github.com/your-username/evaluation-harness.git
cd evaluation-harness

# Development Environment einrichten
pip install -e ".[dev]"

# Tests ausführen
pytest tests/ -v
```

## 📝 Beitragen

### 1. Issue erstellen
Bevor Sie mit der Entwicklung beginnen, erstellen Sie bitte ein Issue für:
- Bug Reports
- Feature Requests
- Verbesserungsvorschläge

### 2. Fork & Branch
```bash
# Fork des Repositories auf GitHub
# Dann lokales Repository einrichten:
git remote add upstream https://github.com/original-owner/evaluation-harness.git
git fetch upstream

# Feature Branch erstellen
git checkout -b feature/amazing-feature
```

### 3. Entwicklung
- Code schreiben
- Tests hinzufügen
- Dokumentation aktualisieren
- Code formatieren: `black src/ tests/`

### 4. Tests
```bash
# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=src --cov-report=html

# Linting
flake8 src/ tests/
mypy src/
```

### 5. Pull Request
```bash
# Commits pushen
git push origin feature/amazing-feature

# Pull Request auf GitHub erstellen
```

## 🧪 Testing Guidelines

### Neue Tests hinzufügen
- Für jede neue Funktion/Metrik Tests schreiben
- Edge Cases abdecken
- Mindestens 80% Code Coverage

### Test-Struktur
```
tests/
├── test_metrics.py      # Metriken-Tests
├── test_stats.py        # Statistik-Tests
├── test_models.py       # Modell-Tests
└── test_integration.py  # Integration-Tests
```

## 📚 Code Standards

### Python Style
- **PEP 8** befolgen
- **Type Hints** verwenden
- **Docstrings** für alle Funktionen/Klassen
- **Black** für Code-Formatierung

### Beispiel:
```python
def calculate_metric(text: str, param: float = 1.0) -> float:
    """
    Berechnet eine Metrik für den gegebenen Text.
    
    Args:
        text: Der zu analysierende Text
        param: Parameter für die Berechnung
        
    Returns:
        Der berechnete Metrik-Wert
        
    Raises:
        ValueError: Wenn der Text leer ist
    """
    if not text:
        raise ValueError("Text darf nicht leer sein")
    
    # Implementation...
    return result
```

## 🎯 Development Areas

### Neue Metriken hinzufügen
1. Metrik in `src/metrics/` implementieren
2. In `MetricsRegistry` registrieren
3. Tests in `tests/test_metrics.py` hinzufügen
4. Dokumentation aktualisieren

### Neue Visualisierungen
1. Plot-Funktion in `src/visualization.py` hinzufügen
2. In `create_all_visualizations()` integrieren
3. Tests hinzufügen

### CLI-Verbesserungen
1. Neue Argumente in `evaluate.py` hinzufügen
2. Hilfe-Text aktualisieren
3. Tests für CLI-Verhalten

## 🐛 Bug Reports

Verwenden Sie bitte folgende Vorlage:

```markdown
**Bug Beschreibung**
Kurze Beschreibung des Bugs

**Reproduktion**
1. Gehen Sie zu '...'
2. Klicken Sie auf '....'
3. Scrollen Sie zu '....'
4. Fehler erscheint

**Erwartetes Verhalten**
Was sollte passieren?

**Screenshots**
Falls zutreffend

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.9.7]
- Version: [e.g. 1.0.0]
```

## ✨ Feature Requests

```markdown
**Feature Beschreibung**
Kurze Beschreibung des gewünschten Features

**Motivation**
Warum ist dieses Feature nützlich?

**Detaillierte Beschreibung**
Wie sollte das Feature funktionieren?

**Alternativen**
Welche Alternativen haben Sie in Betracht gezogen?
```

## 📋 Pull Request Checklist

- [ ] Code folgt den Style Guidelines
- [ ] Tests wurden hinzugefügt/aktualisiert
- [ ] Alle Tests bestehen
- [ ] Dokumentation wurde aktualisiert
- [ ] README.md aktualisiert (falls nötig)
- [ ] CHANGELOG.md aktualisiert
- [ ] Keine Breaking Changes (oder dokumentiert)

## 🏷️ Release Process

1. Version in `setup.py` erhöhen
2. CHANGELOG.md aktualisieren
3. Release Notes schreiben
4. GitHub Release erstellen
5. PyPI Package aktualisieren

## 🤝 Community Guidelines

- Seien Sie respektvoll und konstruktiv
- Helfen Sie anderen bei Fragen
- Teilen Sie Ihr Wissen
- Feiern Sie Erfolge gemeinsam

## 📞 Support

- **Issues**: GitHub Issues für Bugs/Features
- **Discussions**: GitHub Discussions für Fragen
- **Email**: [Ihre Email] für direkten Kontakt

---

Vielen Dank für Ihre Beiträge! 🙏
