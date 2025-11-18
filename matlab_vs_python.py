"""
Side-by-side comparison of MATLAB and Python code for reading MCD files.

This demonstrates how to translate existing MATLAB code to Python.
"""

# ==============================================================================
# MATLAB VERSION (from Neuroshare.m example)
# ==============================================================================
"""
MATLAB:

% Set library path
cd 'c:\Program Files\FIND\'
[nsresult] = ns_SetLibrary('nsMCDlibrary.dll')

% Open file
[nsresult, hfile] = ns_OpenFile('NeuroshareExample.mcd')
[nsresult,info] = ns_GetFileInfo(hfile)

% Get entity info
[nsresult,entity] = ns_GetEntityInfo(hfile,1)

% Read trigger (Event entity)
[nsresult,event] = ns_GetEventInfo(hfile,1)
[nsresult,timestamp,data,datasize] = ns_GetEventData(hfile,1,1)

% Read analog data (continuous signal)
[nsresult,entity] = ns_GetEntityInfo(hfile,27)
[nsresult,analog] = ns_GetAnalogInfo(hfile,27)
[nsresult,count,data] = ns_GetAnalogData(hfile,27,1,entity.ItemCount);
plot(data)

% Read spike data (Segment entity)
[nsresult,entity] = ns_GetEntityInfo(hfile,8)
[nsresult,segment] = ns_GetSegmentInfo(hfile,8)
[nsresult,segmentsource] = ns_GetSegmentSourceInfo(hfile,8,1)
[nsresult,timestamp,data,samplecount,unitid] = ns_GetSegmentData(hfile,8,1)
plot(data)
"""

# ==============================================================================
# PYTHON VERSION (equivalent code)
# ==============================================================================

from neuroshare_mcd import MCDFile
import matplotlib.pyplot as plt

# Open file (library path auto-detected)
with MCDFile("NeuroshareExample.mcd") as mcd:
    # Get file info
    info = mcd.info()
    print(f"File info: {info}")

    # Get entity info
    entity_info = mcd.get_entity_info(1)
    print(f"Entity 1: {entity_info}")

    # Read trigger (Event entity)
    event_data = mcd.get_event_data(1)
    print(f"Event timestamp: {event_data['timestamps'][0]}")
    print(f"Event value: {event_data['values'][0]}")

    # Read analog data (continuous signal)
    analog_data = mcd.get_analog_data(27)
    plt.figure()
    plt.plot(analog_data["data"])
    plt.title("Analog Signal")
    plt.show()

    # Read spike data (Segment entity)
    segment_info = mcd.get_entity_info(8)
    segment_data = mcd.get_segment_data(8, 0)  # First segment
    plt.figure()
    plt.plot(segment_data["data"])
    plt.title(f"Spike Waveform (Unit {segment_data['unit_id']})")
    plt.show()


# ==============================================================================
# MORE PYTHONIC EXAMPLES
# ==============================================================================


def pythonic_example_1():
    """Find and read all analog channels."""
    with MCDFile("NeuroshareExample.mcd") as mcd:
        # Get all analog channels
        for entity in mcd.get_entities_by_type("analog"):
            print(f"Reading: {entity['label']}")
            data = mcd.get_analog_data(entity["id"])

            # Plot first second of data
            sample_rate = data["sample_rate"]
            n_samples = int(sample_rate)  # 1 second

            plt.figure(figsize=(12, 3))
            plt.plot(data["timestamps"][:n_samples], data["data"][:n_samples])
            plt.xlabel("Time (s)")
            plt.ylabel(f"Signal ({data['units']})")
            plt.title(entity["label"])
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{entity['label'].replace(' ', '_')}.png")


def pythonic_example_2():
    """Extract all spikes and organize by unit."""
    import numpy as np

    with MCDFile("NeuroshareExample.mcd") as mcd:
        # Get all segment entities (spikes)
        for entity in mcd.get_entities_by_type("segment"):
            # Read all segments
            segments = mcd.get_all_segments(entity["id"])

            # Organize by unit ID
            units = {}
            for seg in segments:
                unit_id = seg["unit_id"]
                if unit_id not in units:
                    units[unit_id] = {"timestamps": [], "waveforms": []}
                units[unit_id]["timestamps"].append(seg["timestamp"])
                units[unit_id]["waveforms"].append(seg["data"])

            # Plot average waveform for each unit
            fig, axes = plt.subplots(len(units), 1, figsize=(8, 2 * len(units)))
            if len(units) == 1:
                axes = [axes]

            for idx, (unit_id, unit_data) in enumerate(sorted(units.items())):
                waveforms = np.array(unit_data["waveforms"])
                mean_waveform = waveforms.mean(axis=0)
                std_waveform = waveforms.std(axis=0)

                axes[idx].plot(mean_waveform, "b-", linewidth=2)
                axes[idx].fill_between(
                    range(len(mean_waveform)),
                    mean_waveform - std_waveform,
                    mean_waveform + std_waveform,
                    alpha=0.3,
                )
                axes[idx].set_title(
                    f"Unit {unit_id} (n={len(unit_data['timestamps'])} spikes)"
                )
                axes[idx].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(f"{entity['label']}_units.png")


def pythonic_example_3():
    """Export data to multiple formats."""
    import numpy as np
    import json

    with MCDFile("NeuroshareExample.mcd") as mcd:
        # Export to numpy .npz
        export_dict = {}

        # Add analog data
        for entity in mcd.get_entities_by_type("analog"):
            data = mcd.get_analog_data(entity["id"])
            key = f"analog_{entity['label'].replace(' ', '_')}"
            export_dict[key] = data["data"]
            export_dict[f"{key}_time"] = data["timestamps"]
            export_dict[f"{key}_sr"] = data["sample_rate"]

        # Add events
        for entity in mcd.get_entities_by_type("event"):
            data = mcd.get_event_data(entity["id"])
            key = f"event_{entity['label'].replace(' ', '_')}"
            export_dict[f"{key}_time"] = data["timestamps"]
            if isinstance(data["values"], np.ndarray):
                export_dict[f"{key}_values"] = data["values"]

        # Save
        np.savez("exported_data.npz", **export_dict)
        print("Saved to: exported_data.npz")

        # Also save metadata as JSON
        metadata = {"file_info": mcd.info(), "entities": mcd.list_entities()}
        with open("metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        print("Metadata saved to: metadata.json")


# ==============================================================================
# KEY DIFFERENCES: MATLAB vs PYTHON
# ==============================================================================
"""
1. FILE HANDLING
   MATLAB: Manual open/close with handles
   Python: Context managers (with statement) - automatic cleanup

2. ERROR HANDLING
   MATLAB: Check nsresult after each call
   Python: Exceptions - try/except blocks

3. ARRAYS
   MATLAB: Native matrices (1-indexed)
   Python: NumPy arrays (0-indexed)

4. DATA STRUCTURES
   MATLAB: Structs
   Python: Dictionaries

5. ENTITY ACCESS
   MATLAB: Sequential ID lookups
   Python: Can filter by type, iterate easily

6. PLOTTING
   MATLAB: Built-in plot()
   Python: matplotlib (similar syntax)

ADVANTAGES OF PYTHON VERSION:
- No MEX compilation needed
- Better integration with scientific Python stack
- More expressive, less boilerplate
- Easier to extend and maintain
- Cross-platform without recompilation
- Free and open source
"""


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python matlab_vs_python.py <mcd_file>")
        sys.exit(1)

    # Update examples to use provided file
    import builtins

    original_MCDFile = MCDFile

    class MCDFileWithDefault(original_MCDFile):
        def __init__(self, filename=None, *args, **kwargs):
            if filename is None:
                filename = sys.argv[1]
            super().__init__(filename, *args, **kwargs)

    builtins.MCDFile = MCDFileWithDefault

    # Run examples
    print("Running Pythonic examples...")
    print("\n" + "=" * 70)
    print("Example 1: Reading all analog channels")
    print("=" * 70)
    pythonic_example_1()

    print("\n" + "=" * 70)
    print("Example 2: Analyzing spike data by unit")
    print("=" * 70)
    pythonic_example_2()

    print("\n" + "=" * 70)
    print("Example 3: Exporting to multiple formats")
    print("=" * 70)
    pythonic_example_3()

    print("\nDone! Check the generated files.")
