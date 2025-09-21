import pytest
import os
import tempfile
import shutil
from src.caching import make_key, get, put


class TestCaching:
    """Tests für das Caching-System"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup nach jedem Test"""
        shutil.rmtree(self.temp_dir)

    def test_make_key_consistency(self):
        """Test dass gleiche Inputs gleiche Keys erzeugen"""
        key1 = make_key("model1", {"temp": 0.7}, "prompt", "id1")
        key2 = make_key("model1", {"temp": 0.7}, "prompt", "id1")

        assert key1 == key2
        assert len(key1) == 40  # SHA1 Hash Länge

    def test_make_key_different_inputs(self):
        """Test dass verschiedene Inputs verschiedene Keys erzeugen"""
        key1 = make_key("model1", {"temp": 0.7}, "prompt", "id1")
        key2 = make_key("model2", {"temp": 0.7}, "prompt", "id1")
        key3 = make_key("model1", {"temp": 0.8}, "prompt", "id1")
        key4 = make_key("model1", {"temp": 0.7}, "different prompt", "id1")
        key5 = make_key("model1", {"temp": 0.7}, "prompt", "id2")

        keys = [key1, key2, key3, key4, key5]
        assert len(set(keys)) == len(keys)  # Alle Keys sollten unterschiedlich sein

    def test_put_get_basic(self):
        """Test grundlegende Put/Get-Funktionalität"""
        test_data = {"id": "test1", "result": "test_result", "score": 0.85}

        # Daten speichern
        put(self.temp_dir, "test_key", test_data)

        # Daten abrufen
        retrieved_data = get(self.temp_dir, "test_key")

        assert retrieved_data == test_data

    def test_get_nonexistent(self):
        """Test Abruf von nicht existierenden Daten"""
        result = get(self.temp_dir, "nonexistent_key")
        assert result is None

    def test_put_overwrite(self):
        """Test Überschreiben von existierenden Daten"""
        data1 = {"id": "test1", "value": 1}
        data2 = {"id": "test1", "value": 2}

        put(self.temp_dir, "test_key", data1)
        put(self.temp_dir, "test_key", data2)

        retrieved = get(self.temp_dir, "test_key")
        assert retrieved == data2

    def test_put_creates_directory(self):
        """Test dass Put das Verzeichnis erstellt"""
        new_dir = os.path.join(self.temp_dir, "new_cache")
        test_data = {"test": "data"}

        put(new_dir, "test_key", test_data)

        assert os.path.exists(new_dir)
        retrieved = get(new_dir, "test_key")
        assert retrieved == test_data

    def test_json_serialization(self):
        """Test JSON-Serialisierung komplexer Daten"""
        complex_data = {
            "id": "complex_test",
            "nested": {"key": "value", "number": 42},
            "list": [1, 2, 3, "string"],
            "unicode": "äöüß",
            "float": 3.14159,
            "bool": True,
            "none": None,
        }

        put(self.temp_dir, "complex_key", complex_data)
        retrieved = get(self.temp_dir, "complex_key")

        assert retrieved == complex_data

    def test_multiple_keys(self):
        """Test mehrere verschiedene Keys"""
        data1 = {"id": "test1", "value": 1}
        data2 = {"id": "test2", "value": 2}
        data3 = {"id": "test3", "value": 3}

        put(self.temp_dir, "key1", data1)
        put(self.temp_dir, "key2", data2)
        put(self.temp_dir, "key3", data3)

        assert get(self.temp_dir, "key1") == data1
        assert get(self.temp_dir, "key2") == data2
        assert get(self.temp_dir, "key3") == data3


if __name__ == "__main__":
    pytest.main([__file__])
