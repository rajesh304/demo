import pulp

def create_model(working_timetable):
    print("\nCreating optimization model...")

    solver = pulp.LpProblem("Train_Timetable_Optimization", pulp.LpMinimize)

    # Create arrival and departure variables
    arrival_vars = {
        (entry["train"], entry["station"]): pulp.LpVariable(
            f"arrival_{entry['train']}_{entry['station']}", lowBound=0, cat="Continuous"
        )
        for entry in working_timetable if entry["arrival"] is not None
    }

    departure_vars = {
        (entry["train"], entry["station"]): pulp.LpVariable(
            f"departure_{entry['train']}_{entry['station']}", lowBound=0, cat="Continuous"
        )
        for entry in working_timetable if entry["departure"] is not None
    }

    print("\nCreated Variables:")
    print(f"Arrival Variables: {len(arrival_vars)}")
    print(f"Departure Variables: {len(departure_vars)}")

    return solver, arrival_vars, departure_vars
