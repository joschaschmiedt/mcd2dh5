# Python MCD File Reader

Python interface for reading Multi Channel Systems (MCS) .mcd files using the Neuroshare API.

## What's Inside

This directory contains a complete Python implementation for reading MCD files:

```
python/
├── README.md                    # Comprehensive documentation
├── QUICKSTART.md               # Quick start guide
├── requirements.txt            # Python dependencies
├── neuroshare_mcd.py          # Main module
├── examples.py                 # Usage examples
├── matlab_vs_python.py        # MATLAB to Python migration guide
└── test_neuroshare_mcd.py     # Unit tests
```

## Quick Install

```bash
pip install neuroshare numpy matplotlib h5py
```

## Quick Usage

```python
from neuroshare_mcd import MCDFile

with MCDFile('data.mcd') as mcd:
    info = mcd.info()
    data = mcd.get_analog_data(entity_id=1)
    print(f"Read {len(data['data'])} samples at {data['sample_rate']} Hz")
```

## Key Features

✅ **No compilation required** - Pure Python, no MEX files  
✅ **Cross-platform** - Works on Windows, Linux, macOS  
✅ **Pythonic API** - Clean, modern interface  
✅ **NumPy integration** - Efficient array handling  
✅ **HDF5 export** - Convert MCD to HDF5 format  
✅ **Complete documentation** - Examples and tests included

## Supported Data Types

- **Event entities** - Triggers, digital markers
- **Analog entities** - Continuous electrode recordings
- **Segment entities** - Spike waveforms
- **Neural entities** - Spike timestamps

## Documentation

- **README.md** - Full API documentation and installation guide
- **QUICKSTART.md** - Step-by-step quick start guide  
- **examples.py** - Runnable code examples
- **matlab_vs_python.py** - Migration guide from MATLAB

## Running Examples

```bash
# Print file information
python neuroshare_mcd.py your_file.mcd

# Convert to HDF5
python neuroshare_mcd.py input.mcd output.h5

# Run all examples
python examples.py your_file.mcd

# Compare with MATLAB code
python matlab_vs_python.py your_file.mcd
```

## Testing

```bash
export TEST_MCD_FILE=/path/to/test.mcd
pytest test_neuroshare_mcd.py -v
```

## Requirements

- Python 3.7+
- neuroshare (python-neuroshare package)
- numpy
- matplotlib (for examples)
- h5py (for HDF5 conversion)
- nsMCDLibrary.dll (or platform equivalent)

The Neuroshare library is already included in:
```
../Matlab-Import-Filter/Matlab_Interface/nsMCDLibrary64.dll
```

## Advantages Over MATLAB MEX Interface

1. **No compilation** - Works immediately after `pip install`
2. **Cross-platform** - Same code on all operating systems
3. **Modern syntax** - Context managers, comprehensions, etc.
4. **Better error handling** - Pythonic exceptions
5. **Easy integration** - Works with pandas, scikit-learn, etc.
6. **Open source** - Free and transparent

## MATLAB to Python Quick Reference

| MATLAB Function | Python Equivalent |
|----------------|-------------------|
| `ns_OpenFile('file.mcd')` | `MCDFile('file.mcd')` |
| `ns_GetFileInfo(hFile)` | `mcd.info()` |
| `ns_GetEntityInfo(hFile, id)` | `mcd.get_entity_info(id)` |
| `ns_GetAnalogData(...)` | `mcd.get_analog_data(id)` |
| `ns_GetEventData(...)` | `mcd.get_event_data(id)` |
| `ns_GetSegmentData(...)` | `mcd.get_segment_data(id, idx)` |
| `ns_CloseFile(hFile)` | `mcd.close()` or use `with` |

## Common Use Cases

### Read All Analog Channels
```python
with MCDFile('recording.mcd') as mcd:
    for entity in mcd.get_entities_by_type('analog'):
        data = mcd.get_analog_data(entity['id'])
        # Process data['data'] and data['timestamps']
```

### Extract Triggers
```python
with MCDFile('recording.mcd') as mcd:
    events = mcd.get_event_data(trigger_entity_id)
    trigger_times = events['timestamps']
```

### Export to HDF5
```python
from neuroshare_mcd import MCD2HDF5Converter
converter = MCD2HDF5Converter('input.mcd', 'output.h5')
converter.convert()
```

## Support

For issues or questions:
1. Check the documentation files
2. Run the examples to verify installation
3. Review the test file for usage patterns
4. Consult python-neuroshare docs: http://pythonhosted.org/neuroshare/

## License

This wrapper follows the same LGPL license as python-neuroshare.

## Credits

Built on top of:
- [python-neuroshare](https://github.com/G-Node/python-neuroshare) by G-Node
- Neuroshare API specification
- Multi Channel Systems Neuroshare library
