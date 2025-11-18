# Python MCD Reader for BrainBox

This module provides Python bindings to read Multi Channel Systems (MCS) .mcd files using the Neuroshare API via the python-neuroshare package.

## Installation

### Prerequisites

1. **Install python-neuroshare package:**
   ```bash
   pip install neuroshare
   ```

2. **Install the MCS Neuroshare library:**
   - Download the Neuroshare library from Multi Channel Systems website
   - Place `nsMCDLibrary.dll` (Windows) or equivalent library in:
     - `mcd/Matlab-Import-Filter/Matlab_Interface/` (already present in your project)
     - Or in your system PATH

## Usage

### Basic Example

```python
import neuroshare_mcd as ns_mcd

# Open an MCD file
mcd_file = ns_mcd.MCDFile('path/to/your/file.mcd')

# Print file information
print(mcd_file.info())

# List all entities
for entity in mcd_file.list_entities():
    print(f"{entity['id']}: {entity['label']} ({entity['type']})")

# Read analog data (continuous electrode recordings)
analog_data = mcd_file.get_analog_data(entity_id=1)
print(f"Sample rate: {analog_data['sample_rate']} Hz")
print(f"Data shape: {analog_data['data'].shape}")
print(f"Timestamps shape: {analog_data['timestamps'].shape}")

# Read event data (triggers)
event_data = mcd_file.get_event_data(entity_id=0)
print(f"Event timestamps: {event_data['timestamps']}")
print(f"Event values: {event_data['values']}")

# Read segment data (spike waveforms)
segment_data = mcd_file.get_segment_data(entity_id=8, index=0)
print(f"Waveform shape: {segment_data['data'].shape}")
print(f"Timestamp: {segment_data['timestamp']}")
print(f"Unit ID: {segment_data['unit_id']}")

# Close the file
mcd_file.close()
```

### Using context manager

```python
import neuroshare_mcd as ns_mcd

with ns_mcd.MCDFile('data.mcd') as mcd:
    info = mcd.info()
    print(f"Recording contains {info['entity_count']} entities")
    
    # Get all analog channels
    analog_entities = mcd.get_entities_by_type('analog')
    for entity in analog_entities:
        data = mcd.get_analog_data(entity_id=entity['id'])
        print(f"Channel {entity['label']}: {len(data['data'])} samples")
```

### Converting to HDF5

```python
import neuroshare_mcd as ns_mcd

# Convert MCD file to HDF5 format
converter = ns_mcd.MCD2HDF5Converter('input.mcd', 'output.h5')
converter.convert()
```

## API Reference

### MCDFile

Main class for reading MCD files.

**Methods:**
- `__init__(filename, library_path=None)` - Open MCD file
- `info()` - Get file metadata
- `list_entities()` - List all entities in file
- `get_entities_by_type(entity_type)` - Filter entities by type ('event', 'analog', 'segment', 'neural')
- `get_entity_info(entity_id)` - Get metadata for specific entity
- `get_analog_data(entity_id, start_index=0, count=-1)` - Read analog signal data
- `get_event_data(entity_id)` - Read event data
- `get_segment_data(entity_id, index)` - Read segment (spike) data
- `get_neural_data(entity_id, start_index=0, count=-1)` - Read neural event data
- `close()` - Close file

## Entity Types

- **Event** (type=1): Specific timepoints with associated data (e.g., triggers)
- **Analog** (type=2): Continuously sampled analog signals (e.g., electrode recordings)
- **Segment** (type=3): Short cutouts of analog signals (e.g., spike waveforms)
- **Neural** (type=4): Spike trains (timestamps when action potentials occurred)

## Comparison with MATLAB Interface

This Python interface provides equivalent functionality to the MATLAB MEX interface:

| MATLAB Function | Python Equivalent |
|----------------|-------------------|
| `ns_OpenFile()` | `MCDFile(filename)` |
| `ns_GetFileInfo()` | `mcd.info()` |
| `ns_GetEntityInfo()` | `mcd.get_entity_info(id)` |
| `ns_GetAnalogData()` | `mcd.get_analog_data(id)` |
| `ns_GetEventData()` | `mcd.get_event_data(id)` |
| `ns_GetSegmentData()` | `mcd.get_segment_data(id, index)` |
| `ns_CloseFile()` | `mcd.close()` |

## Notes

- The python-neuroshare package handles the low-level C API calls
- Works on Windows, Linux, and macOS (with appropriate Neuroshare libraries)
- Numpy arrays are used for efficient data handling
- All timestamps are in seconds
