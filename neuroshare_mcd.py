"""
Python interface for reading Multi Channel Systems (MCS) .mcd files.

This module provides a high-level Python interface to read MCD files using
the Neuroshare API via the python-neuroshare package.

Example:
    >>> import neuroshare_mcd as ns_mcd
    >>> with ns_mcd.MCDFile('data.mcd') as mcd:
    ...     info = mcd.info()
    ...     analog_data = mcd.get_analog_data(entity_id=1)
    ...     print(f"Samples: {len(analog_data['data'])}")

Requirements:
    - neuroshare (pip install neuroshare)
    - numpy
    - nsMCDLibrary.dll (or platform equivalent)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

try:
    import neuroshare as ns
except ImportError:
    raise ImportError(
        "python-neuroshare is required. Install with: pip install neuroshare"
    )


class MCDFile:
    """
    Interface for reading Multi Channel Systems .mcd files.

    This class provides methods to access various types of neurophysiological
    data stored in MCD files, including analog signals, events, and spike data.

    Attributes:
        filename (str): Path to the MCD file
        library_path (str): Path to the Neuroshare library
        _file: Neuroshare file handle
        _lib: Neuroshare library handle
    """

    # Entity type constants
    ENTITY_UNKNOWN = 0
    ENTITY_EVENT = 1
    ENTITY_ANALOG = 2
    ENTITY_SEGMENT = 3
    ENTITY_NEURAL = 4

    # Entity type names
    ENTITY_TYPE_NAMES = {
        0: "unknown",
        1: "event",
        2: "analog",
        3: "segment",
        4: "neural",
    }

    def __init__(self, filename: str, library_path: Optional[str] = None):
        """
        Open an MCD file for reading.

        Args:
            filename: Path to the .mcd file
            library_path: Optional path to the Neuroshare library directory.
                         If not provided, will search in default locations.

        Raises:
            FileNotFoundError: If the MCD file doesn't exist
            RuntimeError: If the Neuroshare library cannot be loaded
        """
        self.filename = str(filename)

        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"MCD file not found: {self.filename}")

        # Find and set library path
        self.library_path = self._find_library_path(library_path)

        # Load the library and open file
        self._lib = None
        self._file = None
        self._open_file()

    def _find_library_path(self, library_path: Optional[str]) -> str:
        """
        Find the Neuroshare MCD library.

        Args:
            library_path: Optional user-provided library path

        Returns:
            Path to the Neuroshare library directory

        Raises:
            RuntimeError: If library cannot be found
        """
        if library_path and os.path.exists(library_path):
            return library_path

        # Default search locations
        script_dir = Path(__file__).parent.parent
        search_paths = [
            script_dir / "Matlab-Import-Filter" / "Matlab_Interface",
            Path.cwd(),
        ]

        # Platform-specific library names
        if sys.platform == "win32":
            lib_names = ["nsMCDLibrary64.dll", "nsMCDLibrary.dll"]
        elif sys.platform == "darwin":
            lib_names = ["nsMCDLibrary.dylib"]
        else:  # Linux
            lib_names = ["nsMCDLibrary.so"]

        for search_path in search_paths:
            if not search_path.exists():
                continue
            for lib_name in lib_names:
                lib_file = search_path / lib_name
                if lib_file.exists():
                    return str(lib_file)

        # If not found, return a default path and let neuroshare try to find it
        return str(search_paths[0] / lib_names[0]) if search_paths else None

    def _open_file(self):
        """
        Open the MCD file using the Neuroshare library.

        Raises:
            RuntimeError: If file cannot be opened
        """
        try:
            # Set library path if available
            if self.library_path and os.path.exists(self.library_path):
                # Extract directory from full library path
                lib_dir = os.path.dirname(self.library_path)
                lib_name = os.path.basename(self.library_path)

                # Some systems need the directory in PATH
                if sys.platform == "win32" and lib_dir:
                    os.environ["PATH"] = (
                        lib_dir + os.pathsep + os.environ.get("PATH", "")
                    )

                # Try to load with specific library
                try:
                    self._lib = ns.Library(lib_name, lib_dir)
                except:
                    # Fall back to automatic detection
                    self._file = ns.File(self.filename)
                    return

            # Open file (neuroshare will try to auto-detect library)
            self._file = ns.File(self.filename)

        except Exception as e:
            raise RuntimeError(f"Failed to open MCD file: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the MCD file."""
        if self._file is not None:
            # The neuroshare File object doesn't have explicit close,
            # but we can delete the reference
            self._file = None
        self._lib = None

    def info(self) -> Dict:
        """
        Get file metadata.

        Returns:
            Dictionary containing file information:
                - file_type: File type descriptor
                - entity_count: Number of entities
                - time_stamp_resolution: Minimum timestamp resolution
                - time_span: Time span in seconds
                - app_name: Application that created the file
                - comment: File comment
                - date: Creation date dictionary
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        # Access file metadata
        info = {
            "file_type": self._file.file_type,
            "entity_count": self._file.entity_count,
            "time_stamp_resolution": self._file.time_stamp_resolution,
            "time_span": self._file.time_span,
            "app_name": self._file.app_name,
            "comment": self._file.comment,
            "date": {
                "year": self._file.metadata_raw.get("Time_Year", 0),
                "month": self._file.metadata_raw.get("Time_Month", 0),
                "day": self._file.metadata_raw.get("Time_Day", 0),
                "hour": self._file.metadata_raw.get("Time_Hour", 0),
                "minute": self._file.metadata_raw.get("Time_Min", 0),
                "second": self._file.metadata_raw.get("Time_Sec", 0),
            },
        }

        return info

    def list_entities(self) -> List[Dict]:
        """
        List all entities in the file.

        Returns:
            List of dictionaries, each containing:
                - id: Entity ID
                - label: Entity label/name
                - type: Entity type (1=event, 2=analog, 3=segment, 4=neural)
                - type_name: Human-readable type name
                - item_count: Number of data items
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entities = []
        for i in range(self._file.entity_count):
            entity = self._file.get_entity(i)
            entities.append(
                {
                    "id": i,
                    "label": entity.label,
                    "type": entity.entity_type,
                    "type_name": self.ENTITY_TYPE_NAMES.get(
                        entity.entity_type, "unknown"
                    ),
                    "item_count": entity.item_count,
                }
            )

        return entities

    def get_entities_by_type(self, entity_type: Union[str, int]) -> List[Dict]:
        """
        Get entities filtered by type.

        Args:
            entity_type: Type filter - either numeric (1-4) or string
                        ('event', 'analog', 'segment', 'neural')

        Returns:
            List of entity dictionaries matching the type
        """
        if isinstance(entity_type, str):
            entity_type = entity_type.lower()
            type_map = {v: k for k, v in self.ENTITY_TYPE_NAMES.items()}
            if entity_type not in type_map:
                raise ValueError(f"Invalid entity type: {entity_type}")
            type_num = type_map[entity_type]
        else:
            type_num = entity_type

        all_entities = self.list_entities()
        return [e for e in all_entities if e["type"] == type_num]

    def get_entity_info(self, entity_id: int) -> Dict:
        """
        Get detailed information about a specific entity.

        Args:
            entity_id: Entity ID

        Returns:
            Dictionary with entity-specific metadata
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entity = self._file.get_entity(entity_id)

        info = {
            "id": entity_id,
            "label": entity.label,
            "type": entity.entity_type,
            "type_name": self.ENTITY_TYPE_NAMES.get(entity.entity_type, "unknown"),
            "item_count": entity.item_count,
            "metadata_raw": entity.metadata_raw,
        }

        # Add type-specific metadata
        if entity.entity_type == self.ENTITY_ANALOG:
            info.update(
                {
                    "sample_rate": entity.sample_rate,
                    "min_value": entity.min_value,
                    "max_value": entity.max_value,
                    "units": entity.units,
                    "resolution": entity.resolution,
                }
            )
        elif entity.entity_type == self.ENTITY_SEGMENT:
            info.update(
                {
                    "source_count": entity.source_count,
                    "max_sample_count": entity.max_sample_count,
                    "sample_rate": entity.sample_rate,
                }
            )

        return info

    def get_analog_data(
        self, entity_id: int, start_index: int = 0, count: int = -1
    ) -> Dict:
        """
        Read analog signal data (continuous electrode recordings).

        Args:
            entity_id: ID of the analog entity
            start_index: Starting index (default: 0)
            count: Number of samples to read (default: -1 = all)

        Returns:
            Dictionary containing:
                - data: numpy array of signal values
                - timestamps: numpy array of timestamps (seconds)
                - continuous_count: Number of continuous samples
                - sample_rate: Sampling rate in Hz
                - units: Physical units
                - metadata: Additional metadata

        Raises:
            ValueError: If entity is not an analog entity
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entity = self._file.get_entity(entity_id)

        if entity.entity_type != self.ENTITY_ANALOG:
            raise ValueError(f"Entity {entity_id} is not an analog entity")

        # Get data
        data, timestamps, cont_count = entity.get_data(start_index, count)

        return {
            "data": data,
            "timestamps": timestamps,
            "continuous_count": cont_count,
            "sample_rate": entity.sample_rate,
            "units": entity.units,
            "label": entity.label,
            "metadata": {
                "min_value": entity.min_value,
                "max_value": entity.max_value,
                "resolution": entity.resolution,
                "location_x": entity.location_x,
                "location_y": entity.location_y,
                "location_z": entity.location_z,
            },
        }

    def get_event_data(self, entity_id: int) -> Dict:
        """
        Read event data (e.g., triggers, digital markers).

        Args:
            entity_id: ID of the event entity

        Returns:
            Dictionary containing:
                - timestamps: numpy array of event timestamps (seconds)
                - values: numpy array or list of event values
                - event_type: Type of event data
                - label: Entity label

        Raises:
            ValueError: If entity is not an event entity
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entity = self._file.get_entity(entity_id)

        if entity.entity_type != self.ENTITY_EVENT:
            raise ValueError(f"Entity {entity_id} is not an event entity")

        # Read all events
        n_events = entity.item_count
        timestamps = np.zeros(n_events)
        values = []

        for i in range(n_events):
            timestamp, value = entity.get_data(i)
            timestamps[i] = timestamp
            values.append(value)

        # Convert values to numpy array if possible
        try:
            values = np.array(values)
        except:
            pass  # Keep as list if values are heterogeneous

        return {
            "timestamps": timestamps,
            "values": values,
            "event_type": entity.event_type,
            "label": entity.label,
        }

    def get_segment_data(self, entity_id: int, index: int) -> Dict:
        """
        Read segment data (spike waveforms).

        Args:
            entity_id: ID of the segment entity
            index: Index of the segment to read

        Returns:
            Dictionary containing:
                - data: numpy array of waveform data (samples x sources)
                - timestamp: Timestamp of the segment (seconds)
                - sample_count: Number of samples
                - unit_id: Unit classification ID
                - source_count: Number of sources
                - sample_rate: Sampling rate in Hz
                - label: Entity label

        Raises:
            ValueError: If entity is not a segment entity
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entity = self._file.get_entity(entity_id)

        if entity.entity_type != self.ENTITY_SEGMENT:
            raise ValueError(f"Entity {entity_id} is not a segment entity")

        # Get segment data
        data, timestamp, sample_count, unit_id = entity.get_data(index)

        return {
            "data": data,
            "timestamp": timestamp,
            "sample_count": sample_count,
            "unit_id": unit_id,
            "source_count": entity.source_count,
            "sample_rate": entity.sample_rate,
            "label": entity.label,
        }

    def get_all_segments(self, entity_id: int) -> List[Dict]:
        """
        Read all segments from a segment entity.

        Args:
            entity_id: ID of the segment entity

        Returns:
            List of segment data dictionaries
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entity = self._file.get_entity(entity_id)

        if entity.entity_type != self.ENTITY_SEGMENT:
            raise ValueError(f"Entity {entity_id} is not a segment entity")

        segments = []
        for i in range(entity.item_count):
            segments.append(self.get_segment_data(entity_id, i))

        return segments

    def get_neural_data(
        self, entity_id: int, start_index: int = 0, count: int = -1
    ) -> Dict:
        """
        Read neural event data (spike times).

        Args:
            entity_id: ID of the neural entity
            start_index: Starting index (default: 0)
            count: Number of events to read (default: -1 = all)

        Returns:
            Dictionary containing:
                - timestamps: numpy array of spike timestamps (seconds)
                - label: Entity label

        Raises:
            ValueError: If entity is not a neural entity
        """
        if self._file is None:
            raise RuntimeError("File is not open")

        entity = self._file.get_entity(entity_id)

        if entity.entity_type != self.ENTITY_NEURAL:
            raise ValueError(f"Entity {entity_id} is not a neural entity")

        # Get data
        if count < 0:
            count = entity.item_count

        data = entity.get_data(start_index, count)

        return {
            "timestamps": data,
            "label": entity.label,
        }


class MCD2HDF5Converter:
    """
    Convert MCD files to HDF5 format.

    This converter creates an HDF5 file with groups for each entity type
    and datasets for the data.
    """

    def __init__(self, mcd_filename: str, hdf5_filename: str):
        """
        Initialize converter.

        Args:
            mcd_filename: Path to input MCD file
            hdf5_filename: Path to output HDF5 file
        """
        self.mcd_filename = mcd_filename
        self.hdf5_filename = hdf5_filename

    def convert(self, progress_callback=None):
        """
        Convert MCD file to HDF5.

        Args:
            progress_callback: Optional callback function(current, total, message)
        """
        try:
            import h5py
        except ImportError:
            raise ImportError(
                "h5py is required for conversion. Install with: pip install h5py"
            )

        with MCDFile(self.mcd_filename) as mcd:
            with h5py.File(self.hdf5_filename, "w") as h5:
                # Write file info as attributes
                info = mcd.info()
                for key, value in info.items():
                    if key != "date":
                        h5.attrs[key] = value

                # Create groups for each entity type
                event_grp = h5.create_group("events")
                analog_grp = h5.create_group("analog")
                segment_grp = h5.create_group("segments")
                neural_grp = h5.create_group("neural")

                entities = mcd.list_entities()
                total = len(entities)

                for i, entity_info in enumerate(entities):
                    if progress_callback:
                        progress_callback(
                            i, total, f"Converting {entity_info['label']}"
                        )

                    entity_id = entity_info["id"]
                    entity_type = entity_info["type"]
                    label = entity_info["label"].replace(
                        "/", "_"
                    )  # HDF5 doesn't like /

                    try:
                        if entity_type == MCDFile.ENTITY_EVENT:
                            data = mcd.get_event_data(entity_id)
                            grp = event_grp.create_group(label)
                            grp.create_dataset("timestamps", data=data["timestamps"])
                            if isinstance(data["values"], np.ndarray):
                                grp.create_dataset("values", data=data["values"])

                        elif entity_type == MCDFile.ENTITY_ANALOG:
                            data = mcd.get_analog_data(entity_id)
                            grp = analog_grp.create_group(label)
                            grp.create_dataset("data", data=data["data"])
                            grp.create_dataset("timestamps", data=data["timestamps"])
                            grp.attrs["sample_rate"] = data["sample_rate"]
                            grp.attrs["units"] = data["units"]

                        elif entity_type == MCDFile.ENTITY_SEGMENT:
                            segments = mcd.get_all_segments(entity_id)
                            grp = segment_grp.create_group(label)
                            for seg_idx, seg in enumerate(segments):
                                seg_grp = grp.create_group(f"segment_{seg_idx:04d}")
                                seg_grp.create_dataset("data", data=seg["data"])
                                seg_grp.attrs["timestamp"] = seg["timestamp"]
                                seg_grp.attrs["unit_id"] = seg["unit_id"]

                        elif entity_type == MCDFile.ENTITY_NEURAL:
                            data = mcd.get_neural_data(entity_id)
                            grp = neural_grp.create_group(label)
                            grp.create_dataset("timestamps", data=data["timestamps"])

                    except Exception as e:
                        print(f"Warning: Failed to convert entity {label}: {e}")

                if progress_callback:
                    progress_callback(total, total, "Conversion complete")


def print_mcd_info(filename: str):
    """
    Utility function to print MCD file information.

    Args:
        filename: Path to MCD file
    """
    with MCDFile(filename) as mcd:
        info = mcd.info()
        print(f"\nFile: {filename}")
        print(f"Type: {info['file_type']}")
        print(f"Application: {info['app_name']}")
        print(f"Comment: {info['comment']}")
        print(f"Entities: {info['entity_count']}")
        print(f"Time span: {info['time_span']:.2f} seconds")
        print(f"Timestamp resolution: {info['time_stamp_resolution']:.6f} seconds")
        print(f"\nEntities:")
        print(f"{'ID':<5} {'Type':<10} {'Label':<40} {'Items':<10}")
        print("-" * 70)

        for entity in mcd.list_entities():
            print(
                f"{entity['id']:<5} {entity['type_name']:<10} "
                f"{entity['label']:<40} {entity['item_count']:<10}"
            )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python neuroshare_mcd.py <mcd_file> [output.h5]")
        print("  Without output.h5: prints file information")
        print("  With output.h5: converts to HDF5 format")
        sys.exit(1)

    mcd_file = sys.argv[1]

    if len(sys.argv) >= 3:
        # Convert to HDF5
        output_file = sys.argv[2]
        print(f"Converting {mcd_file} to {output_file}...")

        def progress(current, total, msg):
            percent = (current / total) * 100 if total > 0 else 0
            print(f"\r[{percent:5.1f}%] {msg}", end="", flush=True)

        converter = MCD2HDF5Converter(mcd_file, output_file)
        converter.convert(progress)
        print("\nDone!")
    else:
        # Print info
        print_mcd_info(mcd_file)
