# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-09-20

### Hinzugefügt
- **Erste Veröffentlichung** der Evaluation Harness
- **Umfassende Metriken**:
  - SARI (System for Automatic Readability Index)
  - Flesch-Deutsch (Deutsche Version des Flesch-Index)
  - LIX (Lesbarkeitsindex)
  - WSTF (Wiener Sachtextformel)
  - Basisstatistiken (Wortlänge, Satzlänge, Komplexität)
- **Statistische Analyse**:
  - Paired t-Tests und Wilcoxon-Tests
  - Cohen's d Effektgrößen
  - Bootstrap-Konfidenzintervalle
  - Holm-Korrektur für multiple Vergleiche
- **Professionelle Visualisierung**:
  - Metriken-Vergleichsdiagramme
  - Korrelations-Heatmaps
  - Verteilungsplots
  - Effektgrößen-Visualisierung
- **Robuste CLI**:
  - Progress Bars mit tqdm
  - Verbose/Quiet Modi
  - Dry-Run Funktionalität
  - Flexible Konfiguration
- **Caching-System** für reproduzierbare Ergebnisse
- **Umfassende Dokumentation**:
  - README.md mit Installation und Verwendung
  - API-Dokumentation
  - Troubleshooting Guide
- **Vollständige Test-Suite**:
  - 34 Unit Tests mit 100% Erfolgsrate
  - Test-Coverage für alle Module
  - Edge Case Testing
- **Setup.py** für einfache Installation
- **Requirements.txt** mit allen Abhängigkeiten
- **Logging-System** mit verschiedenen Levels
- **Error Handling** für Modell-Loading und Generation
- **Memory Management** für GPU/CPU

### Technische Details
- **Python 3.8+** Kompatibilität
- **Modulare Architektur** für einfache Erweiterung
- **YAML-basierte Konfiguration**
- **JSON + Markdown** Ausgabe-Formate
- **Transformers Library** Integration
- **PyTorch** Support für GPU/CPU

## [Unreleased]

### Geplant
- Mehrsprachige Unterstützung (Englisch, Französisch)
- Zusätzliche Metriken (BLEU, ROUGE, BERTScore)
- Batch-Verarbeitung für große Datensätze
- Web-Interface für interaktive Evaluation
- Docker-Container für einfache Deployment
- CI/CD Pipeline mit GitHub Actions
- Automatische Modell-Downloads
- Experiment-Tracking Integration

### Mögliche Verbesserungen
- Parallele Modell-Inferenz
- Streaming für große Datensätze
- Real-time Monitoring Dashboard
- Export zu verschiedenen Formaten (CSV, Excel)
- Plugin-System für benutzerdefinierte Metriken
- Cloud-Integration (AWS, GCP, Azure)

---

## Versionierung

Wir verwenden [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking Changes
- **MINOR** (0.X.0): Neue Features, rückwärtskompatibel
- **PATCH** (0.0.X): Bug Fixes, rückwärtskompatibel

## Migration Guide

### Von 0.x zu 1.0
- Keine Breaking Changes - vollständig rückwärtskompatibel
- Neue CLI-Optionen sind optional
- Alle bestehenden Konfigurationsdateien funktionieren weiterhin
