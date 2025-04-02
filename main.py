from model import create_model
from analysis import analyze_solution
from data import original_timetable, working_timetable, blocked_section, blockage_start, blockage_end, valid_segments, platform_capacity
from constraints import add_constraints  # Updated to include all constraints
from objective import set_objective
from visualization import plot_timetable
import pulp

def add_delay(solver, working_timetable, departure_vars, train, station, delay):
    original_departure = next(entry["departure"] for entry in working_timetable if entry["train"] == train and entry["station"] == station)
    solver += departure_vars[(train, station)] == original_departure + delay, f"Delay_{train}_{station}"
    return solver
def analyze_platform_occupancy(working_timetable, arrival_vars, departure_vars, platform_capacity):
    """
    Analyzes and prints platform occupancy timelines, including when platforms are occupied and released.
    """
    print("\n=== Platform Occupancy Analysis ===")
    for station, capacity in platform_capacity.items():
        if station in ["A", "E"]:  # Skip start and terminal stations
            continue
        print(f"\n--- Station: {station} --- (Capacity: {capacity} platforms)")

        # Collect all events (arrival and departure)
        events = []
        station_stops = [entry for entry in working_timetable if entry['station'] == station]
        print(f"DEBUG: Station stops at {station}: {station_stops}")
        for entry in station_stops:
            train = entry['train']
            arrival_key = (train, station)
            departure_key = (train, station)
            
            # Debug: Print the keys and their presence in the dictionaries
            print(f"DEBUG: Checking arrival_key: {arrival_key}, Present: {arrival_key in arrival_vars}")
            print(f"DEBUG: Checking departure_key: {departure_key}, Present: {departure_key in departure_vars}")
            
            arrival_var = arrival_vars.get(arrival_key)
            departure_var = departure_vars.get(departure_key)
            
            if arrival_var is not None and departure_var is not None:
                arrival_time = pulp.value(arrival_var)
                departure_time = pulp.value(departure_var)
                print(f"DEBUG: Train {train} - Arrival: {arrival_time}, Departure: {departure_time}")
                if arrival_time is not None and departure_time is not None:
                    events.append((arrival_time, 'arrival', train))
                    events.append((departure_time, 'departure', train))
            else:
                print(f"WARNING: Missing arrival or departure variable for Train {train} at Station {station}")

        # Sort events by time
        events.sort()
        print(f"DEBUG: Sorted events at {station}: {events}")

        # Track platform occupancy
        occupied = 0
        for time, event_type, train in events:
            if event_type == 'arrival':
                occupied += 1
                print(f"  Time {time:.2f}: Train {train} occupies a platform (Occupied: {occupied}, Free: {capacity - occupied})")
            elif event_type == 'departure':
                print(f"  Time {time:.2f}: Train {train} releases a platform (Occupied: {occupied - 1}, Free: {capacity - (occupied - 1)})")
                occupied -= 1
def main():
    # Create the optimization model
    solver, arrival_vars, departure_vars = create_model(working_timetable)

    print("\nDEBUG: Adding constraints...")
    # Add constraints to the solver, including the blocking constraints and single-track conflicts
    solver = add_constraints(solver, working_timetable, arrival_vars, departure_vars,
                             blocked_section, blockage_start, blockage_end, valid_segments, platform_capacity)
    print("DEBUG: Constraints added.")

    # Debug: Print all constraints added to the solver
    print("\n=== Constraints Added to Solver ===")
    for name, constraint in solver.constraints.items():
        print(f"{name}: {constraint}")
    # Add a delay for Train TX at station D
    delay = 50
    solver = add_delay(solver, working_timetable, departure_vars, "T3", "C", delay)
    # Set the objective function
    solver = set_objective(solver, working_timetable, arrival_vars, departure_vars)

    # Solve the problem
    print("\nSolving the optimization problem...")
    status = solver.solve()

    # Check if the solution is optimal
    if pulp.LpStatus[status] == "Optimal":
        print("\nFound an optimal solution!")
        optimized_timetable = analyze_solution(working_timetable, arrival_vars, departure_vars)

        print("\nOptimized Timetable:")
        for entry in optimized_timetable:
            print(entry)

        # Analyze platform occupancy
        analyze_platform_occupancy(working_timetable, arrival_vars, departure_vars, platform_capacity)

        # Visualize the timetables
        station_order = ["A", "B", "C", "D", "E"]
        plot_timetable(
            original_timetable,
            "Original Timetable",
            station_order,
            "original_timetable.png",
            blocked_section=blocked_section,
            blockage_start=blockage_start,
            blockage_end=blockage_end
        )
        plot_timetable(optimized_timetable, "Optimized Timetable", station_order, "optimized_timetable.png")
    else:
        print("\nCould not find an optimal solution.")

if __name__ == "__main__":
    main()