import pytest
import numpy as np
from src.metrics.readability_de import flesch_de, lix, wstf, basic_stats, _sentences, _words, _syllables
from src.metrics.sari import sari
from src.metrics.registry import MetricsRegistry


class TestReadabilityMetrics:
    """Tests für deutsche Lesbarkeits-Metriken"""
    
    def test_sentences(self):
        """Test Satz-Erkennung"""
        text = "Das ist ein Satz. Das ist ein weiterer Satz! Und noch einer?"
        sentences = _sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "Das ist ein Satz"
        assert sentences[1] == "Das ist ein weiterer Satz"
        assert sentences[2] == "Und noch einer"
    
    def test_words(self):
        """Test Wort-Erkennung"""
        text = "Das ist ein Test mit Wörtern."
        words = _words(text)
        assert len(words) == 6
        assert words == ["Das", "ist", "ein", "Test", "mit", "Wörtern"]
    
    def test_syllables(self):
        """Test Silben-Zählung"""
        assert _syllables("Test") == 1
        assert _syllables("Wörter") == 2
        assert _syllables("Kommunikation") == 5
        assert _syllables("") == 1  # Minimum 1
    
    def test_flesch_de(self):
        """Test Flesch-Deutsch Index"""
        # Einfacher Text
        simple_text = "Das ist ein einfacher Satz. Er hat wenige Wörter."
        score = flesch_de(simple_text)
        assert 0 <= score <= 100
        assert score > 50  # Sollte relativ einfach sein
        
        # Leerer Text
        assert flesch_de("") == 0.0
        assert flesch_de("   ") == 0.0
    
    def test_lix(self):
        """Test LIX Index"""
        text = "Das ist ein Test mit verschiedenen Wörtern unterschiedlicher Länge."
        score = lix(text)
        assert score > 0
        
        # Leerer Text
        assert lix("") == 0.0
    
    def test_wstf(self):
        """Test WSTF Index"""
        text = "Das ist ein Test für die Wiener Sachtextformel."
        score = wstf(text)
        assert score > 0
        
        # Leerer Text
        assert wstf("") == 0.0
    
    def test_basic_stats(self):
        """Test Basis-Statistiken"""
        text = "Das ist ein Test. Er hat zwei Sätze mit verschiedenen Wörtern."
        stats = basic_stats(text)
        
        assert "avg_sentence_length" in stats
        assert "avg_word_length" in stats
        assert "complex_word_ratio" in stats
        assert "sentence_count" in stats
        assert "word_count" in stats
        assert "character_count" in stats
        
        assert stats["sentence_count"] == 2
        assert stats["word_count"] > 0
        assert stats["character_count"] > 0
        assert 0 <= stats["complex_word_ratio"] <= 100
        
        # Leerer Text
        empty_stats = basic_stats("")
        assert empty_stats["sentence_count"] == 0
        assert empty_stats["word_count"] == 0


class TestSARI:
    """Tests für SARI Metrik"""
    
    def test_sari_basic(self):
        """Test grundlegende SARI-Berechnung"""
        source = "The quick brown fox jumps over the lazy dog."
        hypothesis = "The quick fox jumps over the dog."
        references = ["A quick fox jumps over the dog.", "The fox jumps over the dog."]
        
        score = sari(source, hypothesis, references)
        assert 0 <= score <= 1
    
    def test_sari_no_references(self):
        """Test SARI ohne Referenzen"""
        source = "The quick brown fox"
        hypothesis = "The quick fox"
        references = []
        
        score = sari(source, hypothesis, references)
        assert score == 0.0
    
    def test_sari_identical(self):
        """Test SARI mit identischen Texten"""
        text = "The quick brown fox"
        references = [text]
        
        score = sari(text, text, references)
        # SARI kann auch bei identischen Texten nicht perfekt 1.0 sein
        # da es verschiedene Operationen (KEEP, ADD, DELETE) bewertet
        assert score > 0.0  # Sollte positiv sein


class TestMetricsRegistry:
    """Tests für Metriken-Registry"""
    
    def test_registry_basic(self):
        """Test grundlegende Registry-Funktionalität"""
        registry = MetricsRegistry()
        
        # Metrik registrieren
        def dummy_metric(src, hyp, refs):
            return 1.0
        
        registry.register('DUMMY', dummy_metric)
        
        # Namen abrufen
        names = registry.names()
        assert 'DUMMY' in names
        
        # Metrik berechnen
        result = registry.compute_all("source", "hypothesis", ["ref1", "ref2"])
        assert 'DUMMY' in result
        assert result['DUMMY'] == 1.0
    
    def test_registry_multiple_metrics(self):
        """Test Registry mit mehreren Metriken"""
        registry = MetricsRegistry()
        
        registry.register('METRIC1', lambda s, h, r: 1.0)
        registry.register('METRIC2', lambda s, h, r: 2.0)
        
        names = registry.names()
        assert len(names) == 2
        assert 'METRIC1' in names
        assert 'METRIC2' in names
        
        result = registry.compute_all("source", "hypothesis", ["ref"])
        assert result['METRIC1'] == 1.0
        assert result['METRIC2'] == 2.0


if __name__ == "__main__":
    pytest.main([__file__])
