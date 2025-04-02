import unittest
import pulp
from main import (
    trains, stations, schedule, thresholds,
    create_model, add_constraints, define_objective, solve_model,
    plot_schedule
)

class TestTrainRescheduling(unittest.TestCase):
    def setUp(self):
        self.problem = pulp.LpProblem("Test_Train_Rescheduling", pulp.LpMinimize)
        self.variables = create_model(trains, stations)

if __name__ == '__main__':
    unittest.main()
