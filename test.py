import pulp
from constraints import add_constraints

def test_headway_constraint():
    # Create a simple working timetable
    working_timetable = [
        {"train": "Train1", "station": "StationA", "arrival": None, "departure": 10},
        {"train": "Train2", "station": "StationA", "arrival": None, "departure": 12},
        {"train": "Train1", "station": "StationB", "arrival": 20, "departure": 25},
        {"train": "Train2", "station": "StationB", "arrival": 22, "departure": 30},
    ]

    # Create a solver
    solver = pulp.LpProblem("TestHeadwayConstraint", pulp.LpMinimize)

    # Create variables for arrival and departure times
    arrival_vars = pulp.LpVariable.dicts("Arrival", [(entry["train"], entry["station"]) for entry in working_timetable], lowBound=0, cat='Continuous')
    departure_vars = pulp.LpVariable.dicts("Departure", [(entry["train"], entry["station"]) for entry in working_timetable], lowBound=0, cat='Continuous')

    # Add constraints
    solver = add_constraints(solver, working_timetable, arrival_vars, departure_vars)

    # Solve the problem
    solver.solve()

    # Display the departure times for each train at each station
    print("\nDeparture Times:")
    for entry in working_timetable:
        train, station = entry["train"], entry["station"]
        departure_time = pulp.value(departure_vars[(train, station)])
        print(f"Train {train} at {station}: Departure at {departure_time}")

    # Check the headway constraint
    headway_satisfied = True
    HW_s = 5  # Minimum headway time in minutes
    for i in range(len(working_timetable) - 1):
        current, next_entry = working_timetable[i], working_timetable[i + 1]
        if current["station"] == next_entry["station"] and current["train"] != next_entry["train"]:
            train, next_train = current["train"], next_entry["train"]
            station = current["station"]
            if pulp.value(departure_vars[(next_train, station)]) - pulp.value(departure_vars[(train, station)]) < HW_s:
                headway_satisfied = False
                print(f"Headway constraint violated between {train} and {next_train} at {station}")

    if headway_satisfied:
        print("Headway constraint satisfied for all trains.")
    else:
        print("Headway constraint not satisfied.")

# Run the test
test_headway_constraint()