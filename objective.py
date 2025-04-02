import pulp

def set_objective(solver, working_timetable, arrival_vars, departure_vars):
    print("\nSetting objective function...")

    # Create variables for absolute deviations
    arrival_dev_vars = pulp.LpVariable.dicts("ArrivalDeviation", 
        ((entry["train"], entry["station"]) for entry in working_timetable if entry["arrival"] is not None),
        lowBound=0)
    departure_dev_vars = pulp.LpVariable.dicts("DepartureDeviation", 
        ((entry["train"], entry["station"]) for entry in working_timetable if entry["departure"] is not None),
        lowBound=0)

    # Add constraints to define absolute deviations
    for entry in working_timetable:
        if entry["arrival"] is not None:
            train, station = entry["train"], entry["station"]
            solver += arrival_dev_vars[(train, station)] >= arrival_vars[(train, station)] - entry["arrival"]
            solver += arrival_dev_vars[(train, station)] >= entry["arrival"] - arrival_vars[(train, station)]
        
        if entry["departure"] is not None:
            train, station = entry["train"], entry["station"]
            solver += departure_dev_vars[(train, station)] >= departure_vars[(train, station)] - entry["departure"]
            solver += departure_dev_vars[(train, station)] >= entry["departure"] - departure_vars[(train, station)]

    # Calculate total deviations
    total_arrival_deviation = pulp.lpSum(arrival_dev_vars.values())
    total_departure_deviation = pulp.lpSum(departure_dev_vars.values())

    # Set weightage for arrival and departure deviations
    arrival_weight = 1
    departure_weight = 1

    # Combine the two objectives
    total_weighted_deviation = (arrival_weight * total_arrival_deviation + departure_weight * total_departure_deviation)

    solver += total_weighted_deviation, "Minimize total weighted deviation from schedule"

    return solver