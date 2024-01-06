"""UFLP: Uncapacitated Facility Location Problem"""

import numpy as np
import pandas as pd
from pulp import *
from mealpy import GA

class UFLP:
    """
    Uncapacitated Facility Location Problem

    Problem Description
    -------------------
    UFLP chooses facility locations in order to minimize the total cost
    of building the facilities and transporting goods from facilities
    to customers. The UFLP is a combinatorial optimization problem.
    It is a special case of the capacitated facility location problem
    (CFLP) where the capacity of all facilities is infinite.

    Sets
    ----
    I   : set of facilities
    J   : set of customers

    Parameters
    ----------
    h_i : demand of customer i
    c_ij: cost to transform one unit of demand from facility j to customer i
    f_j : fixed cost to open a facility at site j

    Variables
    ---------
    x_j : 1 if a facility is opened at site j, 0 otherwise
    y_ij: the fraction of the customer i's demand that is served by facility j

    Objective Function
    ------------------
    minimize sum(f_j * x_j) + sum(h_i * c_ij * y_ij)

    Constraints
    -----------
    sum(y_ij) = 1 for all i in I
    y_ij <= x_j for all i in I, j in J
    x_j in {0, 1} for all j in J
    y_ij >= 0 for all i in I, j in J

    References
    ----------
    - [Lawrence .V Snyder, Zuo-Jun Max Shen "Fundamentals of Supply Chain Theory" 28 June 2019]
    (https://onlinelibrary.wiley.com/doi/book/10.1002/9781119584445)
    """

    def __init__(self, h_i, c_ij, f_j):
        # Check the size of the input
        if len(h_i) != len(c_ij):
            raise ValueError("The size of h_i and c_ij must be the same.")
        if len(c_ij[0]) != len(f_j):
            raise ValueError("The size of c_ij and f_j must be the same.")
        self.h_i = h_i
        self.c_ij = c_ij
        self.f_j = f_j
        self.I = len(h_i)  # pylint: disable=invalid-name
        self.J = len(f_j)  # pylint: disable=invalid-name
        # Pulp variables
        self.pulp_model = None
        self.x = None
        self.y = None
        self.solution_by_pulp = None

    def load_to_pulp(self):
        """
        Solve the UFLP by Pulp

        Returns
        -------
        solution_by_pulp: dict
        """
        print("loading data...")
        # Create the model
        model = LpProblem(name="UFLP", sense=LpMinimize)

        # Initialize the decision variables
        x = {j: LpVariable(name=f"x{j}", cat="Binary") for j in range(self.J)}
        y = {
            (i, j): LpVariable(name=f"y{i}_{j}", lowBound=0)
            for i in range(self.I)
            for j in range(self.J)
        }

        # Add the objective function to the model
        model += lpSum(self.f_j[j] * x[j] for j in range(self.J)) + lpSum(
            self.h_i[i] * self.c_ij[i][j] * y[i, j]
            for i in range(self.I)
            for j in range(self.J)
        )

        # Add constraints to the model
        for i in range(self.I):
            model += lpSum(y[i, j] for j in range(self.J)) == 1
        for i in range(self.I):
            for j in range(self.J):
                model += y[i, j] <= x[j]

        # Save the model
        self.pulp_model = model

        # Solve the problem
        model.solve(PULP_CBC_CMD(timeLimit=10*60, msg=1))

        # Get the results
        solution_by_pulp = {
            "x": {j: x[j].value() for j in range(self.J)},
            "y": {(i, j): y[i, j].value() for i in range(self.I) for j in range(self.J)},
        }
        self.solution_by_pulp = solution_by_pulp
        return solution_by_pulp
    
def main():
    i = 100
    j = 1000
    hi = np.random.randint(1, 10, size=i)
    cij = np.random.randint(1, 10, size=(i,j))
    fj = np.random.randint(1, 10, size=j)
    uflp = UFLP(hi, cij, fj)
    solution_by_pulp = uflp.solve_by_pulp()

    print( type(solution_by_pulp), type(hi), type(cij), type(fj) )
    print("Solution by Pulp:")
    # print("x = ", solution_by_pulp["x"])
    # print("y = ", solution_by_pulp["y"])

    # Check the solution
    print("Check the solution:")
    print("sum(y_ij) = ", sum(solution_by_pulp["y"].values()))
    print("y_ij <= x_j:", all(solution_by_pulp["y"][i, j] <= solution_by_pulp["x"][j] for i in range(uflp.I) for j in range(uflp.J)))
    print("x_j in {0, 1}:", all(solution_by_pulp["x"][j] in {0, 1} for j in range(uflp.J)))

if __name__ == "__main__":
    main()
        

