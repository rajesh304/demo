import matplotlib.pyplot as plt

def plot_timetable(timetable, title, station_order, filename, blocked_section=None, blockage_start=None, blockage_end=None):
    """
    Plots the train timetable with optional blocked section visualization.

    Parameters:
        timetable: List of train schedules (arrival, departure times).
        title: Title of the graph.
        station_order: List of stations in their physical order.
        filename: Filename to save the graph.
        blocked_section: Tuple of blocked section (start_station, end_station).
        blockage_start: Start time of the blockage (minutes).
        blockage_end: End time of the blockage (minutes).
    """
    print(f"\nPlotting timetable: {title}")

    plt.figure(figsize=(12, 8))
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'cyan', 'magenta']
    station_positions = {station: i for i, station in enumerate(station_order)}
    trains = sorted(set(entry['train'] for entry in timetable))

    # Plot train schedules
    for idx, train in enumerate(trains):
        train_schedule = [entry for entry in timetable if entry['train'] == train]
        times, station_y, annotations = [], [], []

        for entry in train_schedule:
            station = entry['station']
            for time_type in ['arrival', 'departure', 'new_arrival', 'new_departure']:
                if entry.get(time_type) is not None:
                    times.append(entry[time_type])
                    station_y.append(station_positions[station])
                    annotations.append((time_type, entry[time_type]))

        plt.plot(times, station_y, marker='o', color=colors[idx % len(colors)], label=train)

        for (time_type, time), y in zip(annotations, station_y):
            offset = 10 if 'arrival' in time_type else -10
            plt.annotate(f"{int(time)}", (time, y), textcoords="offset points",
                         xytext=(0, offset), ha='center', fontsize=8)

    # Debug print statements before the condition
    print(f"Blocked section: {blocked_section}")
    print(f"Blockage start: {blockage_start}")
    print(f"Blockage end: {blockage_end}")


    plt.title(title)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlabel("Time (minutes from midnight)")
    plt.ylabel("Stations")
    plt.yticks(range(len(station_order)), station_order)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
