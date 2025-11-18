"""
Example script demonstrating how to use the neuroshare_mcd module
to read Multi Channel Systems .mcd files.
"""

import numpy as np
import matplotlib.pyplot as plt
from neuroshare_mcd import MCDFile, print_mcd_info


def example_basic_usage(mcd_filename):
    """
    Basic example: Open file, print info, and list entities.
    """
    print("=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)

    with MCDFile(mcd_filename) as mcd:
        # Get file information
        info = mcd.info()
        print(f"\nFile Information:")
        print(f"  Type: {info['file_type']}")
        print(f"  Entities: {info['entity_count']}")
        print(f"  Duration: {info['time_span']:.2f} seconds")

        # List all entities
        print(f"\nEntities in file:")
        for entity in mcd.list_entities():
            print(
                f"  [{entity['id']}] {entity['label']:<40} "
                f"({entity['type_name']}, {entity['item_count']} items)"
            )


def example_read_analog_data(mcd_filename):
    """
    Example: Read and plot analog signal data.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Reading Analog Data")
    print("=" * 70)

    with MCDFile(mcd_filename) as mcd:
        # Find all analog entities
        analog_entities = mcd.get_entities_by_type("analog")

        if not analog_entities:
            print("No analog entities found in file")
            return

        # Read data from the first analog entity
        entity_id = analog_entities[0]["id"]
        print(f"\nReading analog entity {entity_id}: {analog_entities[0]['label']}")

        data = mcd.get_analog_data(entity_id)

        print(f"  Sample rate: {data['sample_rate']} Hz")
        print(f"  Units: {data['units']}")
        print(f"  Samples: {len(data['data'])}")
        print(
            f"  Duration: {data['timestamps'][-1] - data['timestamps'][0]:.2f} seconds"
        )
        print(f"  Value range: [{data['data'].min():.6f}, {data['data'].max():.6f}]")

        # Plot a segment of the data
        plot_samples = min(1000, len(data["data"]))
        plt.figure(figsize=(12, 4))
        plt.plot(data["timestamps"][:plot_samples], data["data"][:plot_samples])
        plt.xlabel("Time (s)")
        plt.ylabel(f"Signal ({data['units']})")
        plt.title(f"Analog Signal: {data['label']}")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("analog_signal_example.png", dpi=150)
        print("\nPlot saved to: analog_signal_example.png")


def example_read_events(mcd_filename):
    """
    Example: Read event data (triggers).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Reading Event Data")
    print("=" * 70)

    with MCDFile(mcd_filename) as mcd:
        # Find all event entities
        event_entities = mcd.get_entities_by_type("event")

        if not event_entities:
            print("No event entities found in file")
            return

        # Read data from the first event entity
        entity_id = event_entities[0]["id"]
        print(f"\nReading event entity {entity_id}: {event_entities[0]['label']}")

        data = mcd.get_event_data(entity_id)

        print(f"  Number of events: {len(data['timestamps'])}")
        print(
            f"  Time range: [{data['timestamps'][0]:.3f}, {data['timestamps'][-1]:.3f}] seconds"
        )

        # Print first few events
        n_show = min(10, len(data["timestamps"]))
        print(f"\n  First {n_show} events:")
        for i in range(n_show):
            print(f"    {i}: t={data['timestamps'][i]:.3f}s, value={data['values'][i]}")

        # Calculate inter-event intervals
        if len(data["timestamps"]) > 1:
            intervals = np.diff(data["timestamps"])
            print(f"\n  Inter-event intervals:")
            print(f"    Mean: {intervals.mean():.3f} s")
            print(f"    Median: {np.median(intervals):.3f} s")
            print(f"    Min: {intervals.min():.3f} s")
            print(f"    Max: {intervals.max():.3f} s")


def example_read_segments(mcd_filename):
    """
    Example: Read segment data (spike waveforms).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Reading Segment Data (Spikes)")
    print("=" * 70)

    with MCDFile(mcd_filename) as mcd:
        # Find all segment entities
        segment_entities = mcd.get_entities_by_type("segment")

        if not segment_entities:
            print("No segment entities found in file")
            return

        # Read data from the first segment entity
        entity_id = segment_entities[0]["id"]
        entity_info = segment_entities[0]
        print(f"\nReading segment entity {entity_id}: {entity_info['label']}")
        print(f"  Total segments: {entity_info['item_count']}")

        # Get entity details
        info = mcd.get_entity_info(entity_id)
        print(f"  Sources: {info.get('source_count', 'N/A')}")
        print(f"  Sample rate: {info.get('sample_rate', 'N/A')} Hz")

        # Read first few segments
        n_segments = min(5, entity_info["item_count"])
        print(f"\n  Reading first {n_segments} segments:")

        for i in range(n_segments):
            seg = mcd.get_segment_data(entity_id, i)
            print(
                f"    Segment {i}: t={seg['timestamp']:.3f}s, "
                f"samples={seg['sample_count']}, unit_id={seg['unit_id']}"
            )

        # Plot first segment
        if entity_info["item_count"] > 0:
            seg = mcd.get_segment_data(entity_id, 0)
            plt.figure(figsize=(10, 6))

            # If multiple sources, plot each
            if seg["data"].ndim > 1:
                for source_idx in range(seg["data"].shape[1]):
                    plt.plot(
                        seg["data"][:, source_idx],
                        label=f"Source {source_idx}",
                        alpha=0.7,
                    )
                plt.legend()
            else:
                plt.plot(seg["data"])

            plt.xlabel("Sample")
            plt.ylabel("Amplitude")
            plt.title(f"Spike Waveform (Segment 0, t={seg['timestamp']:.3f}s)")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig("spike_waveform_example.png", dpi=150)
            print("\nPlot saved to: spike_waveform_example.png")


def example_filter_and_export(mcd_filename, output_filename):
    """
    Example: Filter specific entity types and export to numpy format.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Filter and Export")
    print("=" * 70)

    with MCDFile(mcd_filename) as mcd:
        export_data = {}

        # Export all analog channels
        analog_entities = mcd.get_entities_by_type("analog")
        print(f"\nExporting {len(analog_entities)} analog channels...")

        for entity in analog_entities:
            data = mcd.get_analog_data(entity["id"])
            channel_name = entity["label"].replace(" ", "_").replace("/", "_")
            export_data[f"analog_{channel_name}"] = {
                "data": data["data"],
                "timestamps": data["timestamps"],
                "sample_rate": data["sample_rate"],
                "units": data["units"],
            }

        # Export all events
        event_entities = mcd.get_entities_by_type("event")
        print(f"Exporting {len(event_entities)} event channels...")

        for entity in event_entities:
            data = mcd.get_event_data(entity["id"])
            event_name = entity["label"].replace(" ", "_").replace("/", "_")
            export_data[f"event_{event_name}"] = {
                "timestamps": data["timestamps"],
                "values": data["values"],
            }

        # Save to numpy format
        np.savez(output_filename, **export_data)
        print(f"\nData exported to: {output_filename}")
        print(f"Keys in file: {list(export_data.keys())}")


def example_comprehensive_analysis(mcd_filename):
    """
    Comprehensive example combining multiple data types.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Comprehensive Analysis")
    print("=" * 70)

    with MCDFile(mcd_filename) as mcd:
        # Get summary statistics for each entity type
        entities_by_type = {}

        for entity in mcd.list_entities():
            etype = entity["type_name"]
            if etype not in entities_by_type:
                entities_by_type[etype] = []
            entities_by_type[etype].append(entity)

        print(f"\nEntity Summary:")
        for etype, entities in sorted(entities_by_type.items()):
            print(f"\n  {etype.upper()} ({len(entities)} entities):")
            total_items = sum(e["item_count"] for e in entities)
            print(f"    Total items: {total_items}")
            print(f"    Labels: {', '.join(e['label'][:20] for e in entities[:3])}")
            if len(entities) > 3:
                print(f"    ... and {len(entities) - 3} more")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python examples.py <mcd_file>")
        print(
            "\nThis script demonstrates various ways to read MCD files using neuroshare_mcd"
        )
        sys.exit(1)

    mcd_file = sys.argv[1]

    # Run all examples
    try:
        print_mcd_info(mcd_file)
        example_basic_usage(mcd_file)
        example_read_analog_data(mcd_file)
        example_read_events(mcd_file)
        example_read_segments(mcd_file)
        example_filter_and_export(mcd_file, "exported_data.npz")
        example_comprehensive_analysis(mcd_file)

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
