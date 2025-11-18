# Python MCD Reader - Quick Start Guide

## Overview

This Python package provides an interface to read Multi Channel Systems (MCS) `.mcd` files using the python-neuroshare library. It offers a simpler, more Pythonic API compared to the low-level Neuroshare C API.

## Installation

### 1. Install Python Dependencies

```bash
cd mcd/python
pip install -r requirements.txt
```

Or manually:
```bash
pip install neuroshare numpy matplotlib h5py
```

### 2. Verify Neuroshare Library

The MCS Neuroshare library should already be present in:
```
mcd/Matlab-Import-Filter/Matlab_Interface/nsMCDLibrary64.dll
```

If not, download from: https://www.multichannelsystems.com/downloads

## Quick Start

### Basic Usage

```python
from neuroshare_mcd import MCDFile

# Open and read file
with MCDFile('data.mcd') as mcd:
    # Get file info
    info = mcd.info()
    print(f"File contains {info['entity_count']} entities")
    
    # List all channels/entities
    for entity in mcd.list_entities():
        print(f"{entity['id']}: {entity['label']} ({entity['type_name']})")
    
    # Read analog data (electrode recording)
    analog_data = mcd.get_analog_data(entity_id=1)
    print(f"Data shape: {analog_data['data'].shape}")
    print(f"Sample rate: {analog_data['sample_rate']} Hz")
```

### Command Line Usage

Print file information:
```bash
python neuroshare_mcd.py path/to/file.mcd
```

Convert to HDF5:
```bash
python neuroshare_mcd.py input.mcd output.h5
```

### Run Examples

```bash
python examples.py path/to/file.mcd
```

This will:
- Print file information
- Read and plot analog signals
- Extract event data (triggers)
- Read spike waveforms
- Export data to numpy format

## Data Types

The MCD format supports 4 entity types:

1. **Event** - Timestamps with values (e.g., triggers, digital markers)
2. **Analog** - Continuous signals (e.g., electrode recordings, LFP)
3. **Segment** - Short waveform cutouts (e.g., spike waveforms)
4. **Neural** - Spike timestamps (sorted units)

## API Overview

### MCDFile Class

**Opening Files:**
```python
mcd = MCDFile('file.mcd')                    # Manual open
with MCDFile('file.mcd') as mcd:             # Context manager (recommended)
    ...
```

**File Information:**
```python
info = mcd.info()                            # Get metadata
entities = mcd.list_entities()               # List all entities
analog_entities = mcd.get_entities_by_type('analog')  # Filter by type
entity_info = mcd.get_entity_info(entity_id) # Get entity details
```

**Reading Data:**
```python
# Analog signals (continuous recordings)
data = mcd.get_analog_data(entity_id)
# Returns: {'data': ndarray, 'timestamps': ndarray, 'sample_rate': float, ...}

# Events (triggers)
events = mcd.get_event_data(entity_id)
# Returns: {'timestamps': ndarray, 'values': ndarray/list, ...}

# Segments (spike waveforms)
segment = mcd.get_segment_data(entity_id, index)
# Returns: {'data': ndarray, 'timestamp': float, 'unit_id': int, ...}

# Neural events (spike times)
spikes = mcd.get_neural_data(entity_id)
# Returns: {'timestamps': ndarray, 'label': str}
```

## Conversion to HDF5

```python
from neuroshare_mcd import MCD2HDF5Converter

converter = MCD2HDF5Converter('input.mcd', 'output.h5')
converter.convert()
```

The HDF5 file will have this structure:
```
output.h5
├── events/
│   ├── trigger_1/
│   │   ├── timestamps
│   │   └── values
│   └── ...
├── analog/
│   ├── electrode_1/
│   │   ├── data
│   │   └── timestamps
│   └── ...
├── segments/
│   └── ...
└── neural/
    └── ...
```

## Integration with Existing MATLAB Code

This Python interface provides similar functionality to the MATLAB MEX interface:

| MATLAB | Python |
|--------|--------|
| `ns_OpenFile('file.mcd')` | `MCDFile('file.mcd')` |
| `ns_GetFileInfo(hFile)` | `mcd.info()` |
| `ns_GetEntityInfo(hFile, id)` | `mcd.get_entity_info(id)` |
| `ns_GetAnalogData(...)` | `mcd.get_analog_data(id)` |
| `ns_GetEventData(...)` | `mcd.get_event_data(id)` |
| `ns_GetSegmentData(...)` | `mcd.get_segment_data(id, idx)` |
| `ns_CloseFile(hFile)` | `mcd.close()` or use context manager |

## Common Workflows

### Extract All Analog Channels

```python
with MCDFile('recording.mcd') as mcd:
    for entity in mcd.get_entities_by_type('analog'):
        data = mcd.get_analog_data(entity['id'])
        # Process data['data'] and data['timestamps']
        ...
```

### Extract Triggers and Align Data

```python
with MCDFile('recording.mcd') as mcd:
    # Get trigger times
    triggers = mcd.get_event_data(trigger_entity_id)
    trigger_times = triggers['timestamps']
    
    # Get continuous signal
    signal = mcd.get_analog_data(signal_entity_id)
    
    # Extract epochs around triggers
    for t in trigger_times:
        # Extract ±0.5s around each trigger
        ...
```

### Export Spike Data

```python
with MCDFile('recording.mcd') as mcd:
    for entity in mcd.get_entities_by_type('segment'):
        segments = mcd.get_all_segments(entity['id'])
        
        # Extract waveforms and timestamps
        waveforms = [s['data'] for s in segments]
        timestamps = [s['timestamp'] for s in segments]
        
        # Save or analyze
        ...
```

## Testing

Run tests with pytest:
```bash
# Set test file path
export TEST_MCD_FILE=/path/to/test.mcd

# Run tests
pytest test_neuroshare_mcd.py -v
```

## Troubleshooting

**Library not found:**
- Ensure `nsMCDLibrary64.dll` (Windows) or equivalent is in the correct location
- Try specifying library path explicitly:
  ```python
  mcd = MCDFile('file.mcd', library_path='/path/to/nsMCDLibrary64.dll')
  ```

**Import errors:**
- Install neuroshare: `pip install neuroshare`
- Make sure numpy is installed: `pip install numpy`

**Platform-specific issues:**
- Windows: Use 64-bit library (`nsMCDLibrary64.dll`) with 64-bit Python
- Linux: Use `.so` library
- macOS: Use `.dylib` library

## Further Documentation

- python-neuroshare documentation: http://pythonhosted.org/neuroshare/
- Neuroshare API specification: http://neuroshare.sourceforge.net/
- Multi Channel Systems: https://www.multichannelsystems.com/

## Advantages over MATLAB MEX Interface

1. **No compilation needed** - Pure Python, no MEX compilation
2. **Cross-platform** - Works on Windows, Linux, macOS
3. **Modern API** - Pythonic interface with context managers
4. **Better data handling** - Native numpy arrays
5. **Easy integration** - Works with scikit-learn, pandas, matplotlib, etc.
6. **Open source** - Both neuroshare and this wrapper are open source

## Next Steps

1. Try the examples: `python examples.py your_file.mcd`
2. Integrate into your analysis pipeline
3. Convert existing MATLAB code to Python using the mapping table above
4. Combine with other Python neuroscience tools (Neo, Elephant, MNE, etc.)
