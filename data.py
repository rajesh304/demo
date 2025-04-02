import copy

# Synthetic timetable data
# Example blockage scenario
blocked_section = ("B", "C")
blockage_start = 10
blockage_end = 55
valid_segments = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")]
platform_capacity = {
    'A': 30,
    'B': 6,
    'C': 6,
    'D': 6,
    'E': 30
}
# Adjusted timetable
original_timetable = [
    # Train T1
    {"train": "T1", "station": "A", "arrival": None, "departure": 0},
    {"train": "T1", "station": "B", "arrival": 15, "departure": 19},
    {"train": "T1", "station": "C", "arrival": 34, "departure": 38},
    {"train": "T1", "station": "D", "arrival": 53, "departure": 57},
    {"train": "T1", "station": "E", "arrival": 72, "departure": None},

    # Train T2
    {"train": "T2", "station": "A", "arrival": None, "departure": 25},  # Starts after T1 leaves B
    {"train": "T2", "station": "B", "arrival": 40, "departure": 44},
    {"train": "T2", "station": "C", "arrival": 59, "departure": 63},
    {"train": "T2", "station": "D", "arrival": 78, "departure": 82},
    {"train": "T2", "station": "E", "arrival": 97, "departure": None},

    # Train T3
    {"train": "T3", "station": "A", "arrival": None, "departure": 50},  # Starts after T2 leaves B
    {"train": "T3", "station": "B", "arrival": 65, "departure": 69},
    {"train": "T3", "station": "C", "arrival": 84, "departure": 88},
    {"train": "T3", "station": "D", "arrival": 103, "departure": 107},
    {"train": "T3", "station": "E", "arrival": 122, "departure": None},
    # Train T4
    {"train": "T4", "station": "A", "arrival": None, "departure": 75},  # Starts after T3 leaves B
    {"train": "T4", "station": "B", "arrival": 90, "departure": 94},
    {"train": "T4", "station": "C", "arrival": None, "departure": None},
    {"train": "T4", "station": "D", "arrival": 128, "departure": 132},
    {"train": "T4", "station": "E", "arrival": 147, "departure": None},

    # Train T5
    {"train": "T5", "station": "A", "arrival": None, "departure": 100},  # Starts after T4 leaves B
    {"train": "T5", "station": "B", "arrival": 115, "departure": 119},
    {"train": "T5", "station": "C", "arrival": 134, "departure": 138},
    {"train": "T5", "station": "D", "arrival": 153, "departure": 157},
    {"train": "T5", "station": "E", "arrival": 172, "departure": None},

    # Train T6
    {"train": "T6", "station": "A", "arrival": None, "departure": 125},  # Starts after T5 leaves B
    {"train": "T6", "station": "B", "arrival": 140, "departure": 144},
    {"train": "T6", "station": "C", "arrival": None, "departure": None},
    {"train": "T6", "station": "D", "arrival": 178, "departure": 182},
    {"train": "T6", "station": "E", "arrival": 197, "departure": None},
]

# Create a working copy of the original timetable
working_timetable = copy.deepcopy(original_timetable)

# Print the working timetable
print("Working Timetable:")
for entry in working_timetable:
    print(entry)