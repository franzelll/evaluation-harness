import pytest
import numpy as np
from src.stats import paired_tests, cohens_d, bootstrap_ci, holm_correction


class TestPairedTests:
    """Tests für gepaarte statistische Tests"""

    def test_paired_tests_basic(self):
        """Test grundlegende gepaarte Tests"""
        # Identische Daten
        x = [1, 2, 3, 4, 5]
        y = [1, 2, 3, 4, 5]

        result = paired_tests(x, y)

        assert "n" in result
        assert "t" in result
        assert "tp" in result
        assert "w" in result
        assert "wp" in result

        assert result["n"] == 5
        # Bei identischen Daten kann t-Statistik NaN sein (Varianz = 0)
        assert np.isnan(result["t"]) or np.isclose(result["t"], 0.0)
        assert np.isnan(result["tp"]) or np.isclose(result["tp"], 1.0)

    def test_paired_tests_different(self):
        """Test gepaarte Tests mit verschiedenen Daten"""
        x = [1, 2, 3, 4, 5]
        y = [2, 3, 4, 5, 6]  # Konstante Differenz von 1

        result = paired_tests(x, y)

        assert result["n"] == 5
        assert result["t"] != 0.0  # t-Statistik sollte nicht 0 sein
        assert result["tp"] < 1.0  # p-Wert sollte kleiner als 1 sein

    def test_paired_tests_insufficient_data(self):
        """Test gepaarte Tests mit zu wenigen Daten"""
        x = [1, 2]
        y = [2, 3]

        result = paired_tests(x, y)

        assert result["n"] == 2
        assert np.isnan(result["t"])
        assert np.isnan(result["tp"])
        assert np.isnan(result["w"])
        assert np.isnan(result["wp"])

    def test_paired_tests_with_nans(self):
        """Test gepaarte Tests mit NaN-Werten"""
        x = [1, 2, np.nan, 4, 5]
        y = [2, 3, 4, np.nan, 6]

        result = paired_tests(x, y)

        assert result["n"] == 3  # Nur gültige Paare
        assert not np.isnan(result["t"])
        assert not np.isnan(result["tp"])


class TestCohensD:
    """Tests für Cohen's d Effektgröße"""

    def test_cohens_d_identical(self):
        """Test Cohen's d mit identischen Daten"""
        x = [1, 2, 3, 4, 5]
        y = [1, 2, 3, 4, 5]

        d = cohens_d(x, y)
        assert np.isclose(d, 0.0)  # Kein Effekt

    def test_cohens_d_different(self):
        """Test Cohen's d mit verschiedenen Daten"""
        x = [1, 2, 3, 4, 5]
        y = [3, 4, 5, 6, 7]  # Konstante Differenz

        d = cohens_d(x, y)
        assert d > 0  # Positiver Effekt
        assert not np.isnan(d)

    def test_cohens_d_insufficient_data(self):
        """Test Cohen's d mit zu wenigen Daten"""
        x = [1, 2]
        y = [2, 3]

        d = cohens_d(x, y)
        assert np.isnan(d)

    def test_cohens_d_with_nans(self):
        """Test Cohen's d mit NaN-Werten"""
        x = [1, 2, np.nan, 4, 5]
        y = [2, 3, 4, np.nan, 6]

        d = cohens_d(x, y)
        assert not np.isnan(d)


class TestBootstrapCI:
    """Tests für Bootstrap-Konfidenzintervalle"""

    def test_bootstrap_ci_basic(self):
        """Test grundlegende Bootstrap-KI"""
        # Einfache Normalverteilung
        np.random.seed(42)
        diffs = np.random.normal(0, 1, 100)

        ci_lo, ci_hi = bootstrap_ci(diffs)

        assert ci_lo < ci_hi
        assert not np.isnan(ci_lo)
        assert not np.isnan(ci_hi)

    def test_bootstrap_ci_positive_mean(self):
        """Test Bootstrap-KI mit positivem Mittelwert"""
        np.random.seed(42)
        diffs = np.random.normal(2, 1, 100)

        ci_lo, ci_hi = bootstrap_ci(diffs)

        assert ci_lo > 0  # Sollte positiv sein
        assert ci_hi > ci_lo

    def test_bootstrap_ci_custom_params(self):
        """Test Bootstrap-KI mit benutzerdefinierten Parametern"""
        diffs = [1, 2, 3, 4, 5]

        ci_lo, ci_hi = bootstrap_ci(diffs, B=1000, alpha=0.1)

        assert ci_lo < ci_hi
        assert not np.isnan(ci_lo)
        assert not np.isnan(ci_hi)


class TestHolmCorrection:
    """Tests für Holm-Korrektur"""

    def test_holm_correction_basic(self):
        """Test grundlegende Holm-Korrektur"""
        pvals = [0.01, 0.05, 0.1, 0.2]

        adjusted = holm_correction(pvals)

        assert len(adjusted) == len(pvals)
        assert all(0 <= p <= 1 for p in adjusted)
        # Holm-Korrektur kann p-Werte erhöhen
        assert all(adj >= orig for adj, orig in zip(adjusted, pvals))

    def test_holm_correction_single(self):
        """Test Holm-Korrektur mit einem p-Wert"""
        pvals = [0.05]

        adjusted = holm_correction(pvals)

        assert len(adjusted) == 1
        assert adjusted[0] == pvals[0]  # Einzelner Wert bleibt unverändert

    def test_holm_correction_ordering(self):
        """Test dass Holm-Korrektur die Reihenfolge berücksichtigt"""
        pvals = [0.5, 0.01, 0.1, 0.05]

        adjusted = holm_correction(pvals)

        # Kleinster ursprünglicher p-Wert (0.01) sollte am stärksten korrigiert werden
        min_original_idx = pvals.index(min(pvals))
        assert adjusted[min_original_idx] <= adjusted[0]  # Index 0 hatte 0.5


if __name__ == "__main__":
    pytest.main([__file__])
