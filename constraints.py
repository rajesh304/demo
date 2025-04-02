

def add_constraints(solver, working_timetable, arrival_vars, departure_vars, blocked_section, blockage_start, blockage_end, valid_segments, platform_capacity):
    """
    Adds all constraints to the optimization model.
    """
    print("\nAdding constraints...")

    # Single-track conflict constraints
    solver = add_single_track_conflict_constraints(solver, working_timetable, arrival_vars, departure_vars, valid_segments)

    # Blocking constraints
    solver = add_blocking_constraints(solver, working_timetable, blocked_section, blockage_start, blockage_end, departure_vars)

    # Platform capacity constraints
    solver = add_platform_capacity_constraints(solver, working_timetable, arrival_vars, departure_vars, platform_capacity)

    # Running time constraints
    solver = add_running_time_constraints(solver, working_timetable, arrival_vars, departure_vars)

    # Dwell time constraints
    solver = add_dwell_time_constraints(solver, working_timetable, arrival_vars, departure_vars)

    # Headway constraints
    solver = add_headway_constraints(solver, working_timetable, arrival_vars, departure_vars)

    print("Finished adding all constraints.")
    return solver

def add_single_track_conflict_constraints(solver, working_timetable, arrival_vars, departure_vars, valid_segments):
    """
    Adds constraints to prevent conflicts on single-track segments.
    """
    print("\nAdding single-track conflict constraints...")

    for i in range(len(working_timetable)):
        for j in range(i + 1, len(working_timetable)):
            current, next_entry = working_timetable[i], working_timetable[j]

            if current["train"] != next_entry["train"]:
                current_train, next_train = current["train"], next_entry["train"]
                current_station, next_station = current["station"], next_entry["station"]

                if (current_station, next_station) in valid_segments:
                    if (next_train, current_station) in departure_vars and (current_train, next_station) in arrival_vars:
                        solver += (
                            departure_vars[(next_train, current_station)] >= arrival_vars[(current_train, next_station)],
                            f"Single_Track_Conflict_{current_train}_{next_train}_{current_station}_To_{next_station}"
                        )

    print("Finished adding single-track conflict constraints.")
    return solver

def add_blocking_constraints(solver, working_timetable, blocked_section, blockage_start, blockage_end, departure_vars):
    """
    Adds blocking constraints for a specific blocked section during a given time window.
    """
    print("\nAdding blocking constraints...")

    for entry in working_timetable:
        train = entry["train"]
        station = entry["station"]
        departure = entry["departure"]

        if station == blocked_section[0] and departure is not None and blockage_start <= departure <= blockage_end:
            solver += (
                departure_vars[(train, station)] >= blockage_end,
                f"Block_Departure_{train}_{station}"
            )

    print("Finished adding blocking constraints.")
    return solver

import pulp


def add_platform_capacity_constraints(solver, working_timetable, arrival_vars, departure_vars, platform_capacity):
    """
    Adds platform capacity constraints dynamically, enforcing strict capacity limits and train presence rules.
    """
    print("\n=== Adding Improved Platform Capacity Constraints ===")

    for station, capacity in platform_capacity.items():
        print(f"\n--- Station: {station} --- (Capacity: {capacity} platforms)")

        # Skip start and terminal stations
        if station in ["A", "E"]:
            print(f"  Skipping constraints for start/terminal station: {station}")
            continue

        # Collect train schedules at the station
        station_stops = [entry for entry in working_timetable if entry['station'] == station]
        train_names = [entry['train'] for entry in station_stops]
        print(f"  Trains stopping at {station}: {train_names}")

        # Create binary occupancy variables for each train
        occupancy_vars = {}
        for train in station_stops:
            train_name = train["train"]
            arrival = arrival_vars.get((train_name, station))
            departure = departure_vars.get((train_name, station))

            if arrival is None or departure is None:
                print(f"    [WARNING] Missing arrival or departure variable for Train {train_name} at station {station}")
                continue

            var_name = f"Train_{train_name}_Occupying_{station}"
            occupancy_vars[train_name] = pulp.LpVariable(var_name, cat="Binary")

            # Big-M constraints to link occupancy with arrival and departure times
            M = 1000  # A sufficiently large number
            solver += (
                arrival - M * (1 - occupancy_vars[train_name]) <= departure,
                f"OccupancyActive_Start_{train_name}_{station}"
            )
            solver += (
                departure <= arrival + M * occupancy_vars[train_name],
                f"OccupancyActive_End_{train_name}_{station}"
            )
            print(f"    Linked Train {train_name} occupancy at {station}.")

        # Add platform capacity constraint
        solver += (
            pulp.lpSum(occupancy_vars.values()) <= capacity,
            f"TotalCapacity_{station}"
        )
        print(f"  Added total capacity constraint for {station} (Max Capacity: {capacity}).")

        # Add pairwise non-overlapping constraints to ensure no simultaneous occupancy
        for i, train1 in enumerate(station_stops):
            for train2 in station_stops[i + 1:]:
                train1_name, train2_name = train1['train'], train2['train']
                arrival1, departure1 = arrival_vars.get((train1_name, station)), departure_vars.get((train1_name, station))
                arrival2, departure2 = arrival_vars.get((train2_name, station)), departure_vars.get((train2_name, station))

                if arrival1 and departure1 and arrival2 and departure2:
                    solver += (
                        departure1 <= arrival2 + M * (1 - occupancy_vars[train2_name]),
                        f"NoOverlap_{train1_name}_{train2_name}_{station}_1"
                    )
                    solver += (
                        departure2 <= arrival1 + M * (1 - occupancy_vars[train1_name]),
                        f"NoOverlap_{train1_name}_{train2_name}_{station}_2"
                    )
                    print(f"    Added non-overlapping constraint between {train1_name} and {train2_name} at {station}")

    print("\n=== Finished Adding Improved Platform Capacity Constraints ===")
    return solver




def add_running_time_constraints(solver, working_timetable, arrival_vars, departure_vars):
    """
    Adds constraints to enforce minimum running times between stations.
    """
    print("\nAdding running time constraints...")

    for i in range(len(working_timetable) - 1):
        current, next_entry = working_timetable[i], working_timetable[i + 1]
        if current["train"] == next_entry["train"] and current["departure"] is not None and next_entry["arrival"] is not None:
            solver += (
                arrival_vars[(next_entry["train"], next_entry["station"])] -
                departure_vars[(current["train"], current["station"])] >= 10,
                f"Running_{current['train']}_{current['station']}_To_{next_entry['station']}"
            )

    print("Finished adding running time constraints.")
    return solver

def add_dwell_time_constraints(solver, working_timetable, arrival_vars, departure_vars):
    """
    Adds constraints to enforce minimum and maximum dwell times at stations.
    """
    print("\nAdding dwell time constraints...")

    for entry in working_timetable:
        if entry["departure"] is not None and entry["arrival"] is not None:
            train, station = entry["train"], entry["station"]
            solver += (
                departure_vars[(train, station)] - arrival_vars[(train, station)] >= 2,
                f"Min_Dwell_Time_{train}_{station}"
            )
            solver += (
                departure_vars[(train, station)] - arrival_vars[(train, station)] <= 100,
                f"Max_Dwell_Time_{train}_{station}"
            )

    print("Finished adding dwell time constraints.")
    return solver

def add_headway_constraints(solver, working_timetable, arrival_vars, departure_vars, headway_time=5):
    """
    Adds headway constraints to ensure safe time gaps between trains at the same station.
    """
    print("\nAdding headway constraints...")

    for i in range(len(working_timetable)):
        for j in range(i + 1, len(working_timetable)):
            current, next_entry = working_timetable[i], working_timetable[j]

            if current["station"] == next_entry["station"] and current["train"] != next_entry["train"]:
                train, next_train = current["train"], next_entry["train"]
                station = current["station"]

                if current["departure"] is not None and next_entry["departure"] is not None:
                    solver += (
                        departure_vars[(next_train, station)] - departure_vars[(train, station)] >= headway_time,
                        f"Headway_Departure_{train}_{next_train}_{station}"
                    )

                if current["arrival"] is not None and next_entry["arrival"] is not None:
                    solver += (
                        arrival_vars[(next_train, station)] - arrival_vars[(train, station)] >= headway_time,
                        f"Headway_Arrival_{train}_{next_train}_{station}"
                    )

    print("Finished adding headway constraints.")
    return solver
