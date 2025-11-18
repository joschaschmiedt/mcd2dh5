"""
Tests for neuroshare_mcd module.

Run with: pytest test_neuroshare_mcd.py
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import os


# Try to import the module
try:
    from neuroshare_mcd import MCDFile, MCD2HDF5Converter

    NEUROSHARE_AVAILABLE = True
except ImportError:
    NEUROSHARE_AVAILABLE = False
    pytest.skip("neuroshare not available", allow_module_level=True)


# Test data path - you'll need to provide a real MCD file for actual testing
TEST_MCD_FILE = os.environ.get("TEST_MCD_FILE", None)


@pytest.mark.skipif(TEST_MCD_FILE is None, reason="No test MCD file specified")
class TestMCDFile:
    """Tests for MCDFile class."""

    def test_open_file(self):
        """Test opening a file."""
        mcd = MCDFile(TEST_MCD_FILE)
        assert mcd._file is not None
        mcd.close()

    def test_context_manager(self):
        """Test using MCDFile as context manager."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            assert mcd._file is not None

    def test_get_info(self):
        """Test getting file info."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            info = mcd.info()
            assert "entity_count" in info
            assert "time_span" in info
            assert "file_type" in info
            assert info["entity_count"] > 0

    def test_list_entities(self):
        """Test listing entities."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            entities = mcd.list_entities()
            assert len(entities) > 0

            # Check entity structure
            entity = entities[0]
            assert "id" in entity
            assert "label" in entity
            assert "type" in entity
            assert "type_name" in entity
            assert "item_count" in entity

    def test_get_entities_by_type(self):
        """Test filtering entities by type."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            # Test string filter
            analog_entities = mcd.get_entities_by_type("analog")
            for entity in analog_entities:
                assert entity["type"] == MCDFile.ENTITY_ANALOG

            # Test numeric filter
            event_entities = mcd.get_entities_by_type(MCDFile.ENTITY_EVENT)
            for entity in event_entities:
                assert entity["type"] == MCDFile.ENTITY_EVENT

    def test_get_entity_info(self):
        """Test getting entity info."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            entities = mcd.list_entities()
            if len(entities) > 0:
                entity_id = entities[0]["id"]
                info = mcd.get_entity_info(entity_id)
                assert info["id"] == entity_id
                assert "label" in info
                assert "metadata_raw" in info

    def test_get_analog_data(self):
        """Test reading analog data."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            analog_entities = mcd.get_entities_by_type("analog")

            if len(analog_entities) > 0:
                entity_id = analog_entities[0]["id"]
                data = mcd.get_analog_data(entity_id)

                assert "data" in data
                assert "timestamps" in data
                assert "sample_rate" in data
                assert "units" in data
                assert isinstance(data["data"], np.ndarray)
                assert isinstance(data["timestamps"], np.ndarray)
                assert len(data["data"]) == len(data["timestamps"])

    def test_get_analog_data_partial(self):
        """Test reading partial analog data."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            analog_entities = mcd.get_entities_by_type("analog")

            if len(analog_entities) > 0:
                entity_id = analog_entities[0]["id"]

                # Read first 100 samples
                data = mcd.get_analog_data(entity_id, start_index=0, count=100)
                assert len(data["data"]) <= 100

    def test_get_event_data(self):
        """Test reading event data."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            event_entities = mcd.get_entities_by_type("event")

            if len(event_entities) > 0:
                entity_id = event_entities[0]["id"]
                data = mcd.get_event_data(entity_id)

                assert "timestamps" in data
                assert "values" in data
                assert isinstance(data["timestamps"], np.ndarray)

    def test_get_segment_data(self):
        """Test reading segment data."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            segment_entities = mcd.get_entities_by_type("segment")

            if len(segment_entities) > 0:
                entity = segment_entities[0]
                if entity["item_count"] > 0:
                    data = mcd.get_segment_data(entity["id"], 0)

                    assert "data" in data
                    assert "timestamp" in data
                    assert "sample_count" in data
                    assert "unit_id" in data
                    assert isinstance(data["data"], np.ndarray)

    def test_get_all_segments(self):
        """Test reading all segments."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            segment_entities = mcd.get_entities_by_type("segment")

            if len(segment_entities) > 0:
                entity = segment_entities[0]
                if entity["item_count"] > 0:
                    segments = mcd.get_all_segments(entity["id"])
                    assert len(segments) == entity["item_count"]

    def test_get_neural_data(self):
        """Test reading neural data."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            neural_entities = mcd.get_entities_by_type("neural")

            if len(neural_entities) > 0:
                entity_id = neural_entities[0]["id"]
                data = mcd.get_neural_data(entity_id)

                assert "timestamps" in data
                assert isinstance(data["timestamps"], np.ndarray)

    def test_invalid_entity_type(self):
        """Test error handling for wrong entity type."""
        with MCDFile(TEST_MCD_FILE) as mcd:
            # Try to read event data from an analog entity
            analog_entities = mcd.get_entities_by_type("analog")

            if len(analog_entities) > 0:
                entity_id = analog_entities[0]["id"]
                with pytest.raises(ValueError):
                    mcd.get_event_data(entity_id)


@pytest.mark.skipif(TEST_MCD_FILE is None, reason="No test MCD file specified")
class TestMCD2HDF5Converter:
    """Tests for MCD to HDF5 conversion."""

    def test_conversion(self):
        """Test MCD to HDF5 conversion."""
        try:
            import h5py
        except ImportError:
            pytest.skip("h5py not available")

        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
            tmp_file = tmp.name

        try:
            converter = MCD2HDF5Converter(TEST_MCD_FILE, tmp_file)
            converter.convert()

            # Verify HDF5 file was created
            assert os.path.exists(tmp_file)

            # Check HDF5 structure
            with h5py.File(tmp_file, "r") as h5:
                assert "events" in h5
                assert "analog" in h5
                assert "segments" in h5
                assert "neural" in h5

        finally:
            # Clean up
            if os.path.exists(tmp_file):
                os.remove(tmp_file)


class TestUtilityFunctions:
    """Tests for utility functions that don't require a real file."""

    def test_entity_type_names(self):
        """Test entity type name mapping."""
        assert MCDFile.ENTITY_TYPE_NAMES[MCDFile.ENTITY_EVENT] == "event"
        assert MCDFile.ENTITY_TYPE_NAMES[MCDFile.ENTITY_ANALOG] == "analog"
        assert MCDFile.ENTITY_TYPE_NAMES[MCDFile.ENTITY_SEGMENT] == "segment"
        assert MCDFile.ENTITY_TYPE_NAMES[MCDFile.ENTITY_NEURAL] == "neural"


if __name__ == "__main__":
    # If TEST_MCD_FILE is set, run tests
    if TEST_MCD_FILE:
        pytest.main([__file__, "-v"])
    else:
        print("No test MCD file specified.")
        print("Set TEST_MCD_FILE environment variable to run tests:")
        print("  export TEST_MCD_FILE=/path/to/test.mcd")
        print("  pytest test_neuroshare_mcd.py")
