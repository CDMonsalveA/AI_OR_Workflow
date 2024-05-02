"""CFLP (Capacitated Facility Location Problem)"""

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, PULP_CBC_CMD


class CFLP:
    """
    Capacitated Facility Location Problem

    Problem Description
    -------------------
    CFLP chooses facility locations in order to minimize the total cost
    of building the facilities and transporting goods from facilities
    to customers. The CFLP is a combinatorial optimization problem.

    Sets
    ----
    I   : set of facilities
    J   : set of customers

    Parameters
    ----------
    h_i : demand of customer i
    c_ij: cost to transform one unit of demand from facility j to customer i
    f_j : fixed cost to open a facility at site j
    v_j : maximum capacity of facility j

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
    sum(h_i * y_ij) <= v_j for all j in J
    x_j in {0, 1} for all j in J
    y_ij >= 0 for all i in I, j in J

    References
    ----------
    - [Lawrence .V Snyder, Zuo-Jun Max Shen "Fundamentals of Supply Chain Theory" 28 June 2019]
    (https://onlinelibrary.wiley.com/doi/book/10.1002/9781119584445)
    """

    def __init__(self, h_i, c_ij, f_j, v_j) -> None:
        # Check the size of the input
        if len(h_i) != len(c_ij):
            raise ValueError("The size of h_i and c_ij must be the same.")
        if len(c_ij[0]) != len(f_j):
            raise ValueError("The size of c_ij and f_j must be the same.")
        if len(f_j) != len(v_j):
            raise ValueError("The size of f_j and v_j must be the same.")
        self.h_i = h_i
        self.c_ij = c_ij
        self.f_j = f_j
        self.v_j = v_j
        self.I = len(self.h_i)  # pylint: disable=invalid-name
        self.J = len(self.f_j)  # pylint: disable=invalid-name
        # Pulp variables
        self.pulp_model = None
        self.x = None
        self.y = None
        self.solution_by_pulp = None

    def load_to_pulp(self):
        """
        Load the CFLP to Pulp
        """
        # Create the model
        model = LpProblem(name="CFLP", sense=LpMinimize)

        # Initialize the decision variables
        self.x = {
            j: LpVariable(name=f"x_{j}", lowBound=0, upBound=1, cat="Integer")
            for j in range(self.J)
        }
        self.y = {
            (i, j): LpVariable(name=f"y_{i}_{j}", lowBound=0)
            for i in range(self.I)
            for j in range(self.J)
        }

        # Set the objective
        model += lpSum(self.f_j[j] * self.x[j] for j in range(self.J)) + lpSum(
            self.h_i[i] * self.c_ij[i][j] * self.y[i, j]
            for i in range(self.I)
            for j in range(self.J)
        )

        # Add constraints
        for i in range(self.I):
            model += lpSum(self.y[i, j] for j in range(self.J)) == 1
        for i in range(self.I):
            for j in range(self.J):
                model += self.y[i, j] <= self.x[j]
        for j in range(self.J):
            model += (
                lpSum(self.h_i[i] * self.y[i, j] for i in range(self.I)) <= self.v_j[j]
            )
        # Optional constraint
        model += lpSum(self.v_j[j] * self.x[j] for j in range(self.J)) <= lpSum(
            self.h_i[i] for i in range(self.I)
        )

        # Save the model
        self.pulp_model = model

    def solve_by_pulp(self, solver=PULP_CBC_CMD()):
        """
        Solve the CFLP by Pulp

        Parameters
        ----------
        solver: pulp solver
            any pulp solver, like
            - PULP_CBC_CMD()
            - GUROBI_CMD()
            - CPLEX_CMD()
        """
        self.pulp_model.solve(solver)

        # Check the status
        if self.pulp_model.status != 1:
            raise ValueError("The problem is infeasible.")

    def get_solution_by_pulp(self):
        """
        Get the solution of the CFLP by Pulp
        """
        self.solution_by_pulp = {
            "status": self.pulp_model.status,
            "objective": value(self.pulp_model.objective.value()),
            "x": {j: value(self.x[j]) for j in range(self.J)},
            "y": {
                (i, j): value(self.y[i, j])
                for i in range(self.I)
                for j in range(self.J)
            },
        }
        return self.solution_by_pulp

    def pulp_solve(self, solver=PULP_CBC_CMD()):
        """
        Solve the CFLP by Pulp

        Parameters
        ----------
        solver: pulp solver
            any pulp solver, like
            - PULP_CBC_CMD()
            - GUROBI_CMD()
            - CPLEX_CMD()
        """
        # Check if the parameters are loaded to pulp
        if self.I is None or self.J is None:
            raise ValueError("The parameters are not loaded to pulp.")
        print("loading to pulp ...")
        self.load_to_pulp()
        print("solving by pulp...")
        self.solve_by_pulp(solver)
        print("getting the solution...")
        return self.get_solution_by_pulp()
