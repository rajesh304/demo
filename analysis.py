import pulp

def analyze_solution(working_timetable, arrival_vars, departure_vars):
    print("\nAnalyzing solution...")

    optimized_timetable = []
    total_delay = 0

    for entry in working_timetable:
        train, station = entry["train"], entry["station"]
        original_arrival, original_departure = entry["arrival"], entry["departure"]

        # Retrieve optimized values
        new_arrival = pulp.value(arrival_vars.get((train, station))) if (train, station) in arrival_vars else original_arrival
        new_departure = pulp.value(departure_vars.get((train, station))) if (train, station) in departure_vars else original_departure

        # Calculate delays
        arrival_delay = max(0, (new_arrival or 0) - (original_arrival or 0))
        departure_delay = max(0, (new_departure or 0) - (original_departure or 0))

        total_delay += arrival_delay + departure_delay

        # Create optimized timetable entry
        optimized_entry = {
            "train": train,
            "station": station,
            "original_arrival": original_arrival,
            "original_departure": original_departure,
            "new_arrival": new_arrival,
            "new_departure": new_departure,
            "arrival_delay": arrival_delay,
            "departure_delay": departure_delay
        }
        optimized_timetable.append(optimized_entry)

    print(f"\nTotal delay: {total_delay:.2f} minutes")
    return optimized_timetable