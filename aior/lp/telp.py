"""Three-echelons location problem (TELP)"""

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, PULP_CBC_CMD


class TELP:
    """
    Three-echelons location problem

    Problem Description
    -------------------
    This problem is concerned with a three-echelon system
    consisting of plants, DCs, and customers. The customer locations are fixed, but the plant
    and DC locations are to be optimized.

    Sets
    ----
    I   : set of customers
    J   : set of potential DC locations
    K   : set of potential plant locations
    L   : set of products

    Parameters
    ----------
    h_il: annual demand of customer i for product l
    v_j : maximum capacity of DC j
    b_k : maximum capacity of plant k
    s_l : units of capacity consumed by one unit of product l

    f_j : fixed annual cost to open a DC at site j
    g_k : fixed annual cost to open a plant at site k
    c_ijl: cost to transform one unit of product l from DC j to customer i
    d_ikl: cost to transform one unit of product l from plant k to DC j

    Variables
    ---------
    x_j : 1 if a DC is opened at site j, 0 otherwise
    z_k : 1 if a plant is opened at site k, 0 otherwise
    y_ijl: number of units of product l that are shipped from DC j to customer i
    w_ikl: number of units of product l that are shipped from plant k to DC j

    Objective Function
    ------------------
    minimize sum(f_j * x_j) + sum(g_k * z_k) + sum(c_ijl * y_ijl) + sum(d_ikl * w_ikl)

    Constraints
    -----------
    sum(y_ijl) = h_il for all i in I, l in L
    sum(s_l * y_ijl) <= v_j * x_j for all j in J, l in L
    sum(y_ijl) = sum(w_ikl) for all j in J, l in L
    sum(s_l * w_ikl) <= b_k * z_k for all k in K, l in L
    x_j in {0, 1} for all j in J
    z_k in {0, 1} for all k in K
    y_ijl >= 0 for all i in I, j in J, l in L
    w_ikl >= 0 for all i in I, k in K, l in L

    References
    ----------
    - [Operations Research Models and Methods]
    (https://www.wiley.com/en-us/Operations+Research+Models+and
    +Methods%3A+With+Excel+Tools%2C+2nd+Edition-p-9781119495173)
    """

    def __init__(self, h_il, v_j, b_k, s_l, f_j, g_k, c_ijl, d_ikl) -> None:
        # Check the size of the input
        if len(h_il) != len(c_ijl):
            raise ValueError("The size of h_il and c_ijl must be the same.")
        if len(c_ijl[0]) != len(v_j):
            raise ValueError("The size of c_ijl and v_j must be the same.")
        if len(v_j) != len(s_l):
            raise ValueError("The size of v_j and s_l must be the same.")
        if len(s_l) != len(d_ikl[0]):
            raise ValueError("The size of s_l and d_ikl must be the same.")
        if len(d_ikl) != len(b_k):
            raise ValueError("The size of d_ikl and b_k must be the same.")
        if len(b_k) != len(g_k):
            raise ValueError("The size of b_k and g_k must be the same.")
        self.h_il = h_il
        self.v_j = v_j
        self.b_k = b_k
        self.s_l = s_l
        self.f_j = f_j
        self.g_k = g_k
        self.c_ijl = c_ijl
        self.d_ikl = d_ikl
        self.I = len(self.h_il)  # pylint: disable=invalid-name
        self.J = len(self.v_j)  # pylint: disable=invalid-name
        self.K = len(self.b_k)  # pylint: disable=invalid-name
        self.L = len(self.s_l)  # pylint: disable=invalid-name
        # Pulp variables
        self.pulp_model = None
        self.x = None
        self.z = None
        self.y = None
        self.w = None
        self.solution_by_pulp = None

    def load_to_pulp(self):
        """
        Load the Three-echelons location problem to Pulp
        """
        # Create the model
        model = LpProblem(name="TELP", sense=LpMinimize)

        # Initialize the decision variables
        self.x = {
            j: LpVariable(name=f"x_{j}", lowBound=0, upBound=1, cat="Integer")
            for j in range(self.J)
        }
        self.z = {
            k: LpVariable(name=f"z_{k}", lowBound=0, upBound=1, cat="Integer")
            for k in range(self.K)
        }
        self.y = {
            (i, j, l): LpVariable(
                name=f"y_{i}_{j}_{l}", lowBound=0, upBound=None, cat="Continuous"
            )
            for i in range(self.I)
            for j in range(self.J)
            for l in range(self.L)
        }
        self.w = {
            (i, k, l): LpVariable(
                name=f"w_{i}_{k}_{l}", lowBound=0, upBound=None, cat="Continuous"
            )
            for i in range(self.I)
            for k in range(self.K)
            for l in range(self.L)
        }

        # Set the objective
        model += (
            lpSum(self.f_j[j] * self.x[j] for j in range(self.J))
            + lpSum(self.g_k[k] * self.z[k] for k in range(self.K))
            + lpSum(
                self.c_ijl[i][j][l] * self.y[i, j, l]
                for i in range(self.I)
                for j in range(self.J)
                for l in range(self.L)
            )
            + lpSum(
                self.d_ikl[i][k][l] * self.w[i, k, l]
                for i in range(self.I)
                for k in range(self.K)
                for l in range(self.L)
            )
        )

        # Add constraints
        for i in range(self.I):
            for l in range(self.L):
                model += (
                    lpSum(self.y[i, j, l] for j in range(self.J)) == self.h_il[i][l]
                )
        for j in range(self.J):
            for l in range(self.L):
                model += (
                    lpSum(self.s_l[l] * self.y[i, j, l] for i in range(self.I))
                    <= self.v_j[j] * self.x[j]
                )
        for j in range(self.J):
            for l in range(self.L):
                model += lpSum(self.y[i, j, l] for i in range(self.I)) == lpSum(
                    self.w[i, k, l] for k in range(self.K)
                )
        for k in range(self.K):
            for l in range(self.L):
                model += (
                    lpSum(self.s_l[l] * self.w[i, k, l] for i in range(self.I))
                    <= self.b_k[k] * self.z[k]
                )

        # save the model
        self.pulp_model = model

    def solve_by_pulp(self, solver=PULP_CBC_CMD()):
        """
        Solve the Three-echelons location problem by Pulp

        Parameters
        ----------
        solver: pulp solver
            any pulp solver, like
            - PULP_CBC_CMD()
            - GUROBI_CMD()
            - CPLEX_CMD()
        """
        self.pulp_model.solve(solver)

    def get_solution_by_pulp(self):
        """
        Get the solution of the Three-echelons location problem by Pulp
        """
        self.solution_by_pulp = {
            "status": self.pulp_model.status,
            "objective": value(self.pulp_model.objective),
            "x": {j: value(self.x[j]) for j in range(self.J)},
            "z": {k: value(self.z[k]) for k in range(self.K)},
            "y": {
                (i, j, l): value(self.y[i, j, l])
                for i in range(self.I)
                for j in range(self.J)
                for l in range(self.L)
            },
            "w": {
                (i, k, l): value(self.w[i, k, l])
                for i in range(self.I)
                for k in range(self.K)
                for l in range(self.L)
            },
        }
        return self.solution_by_pulp

    def pulp_solve(self, solver=PULP_CBC_CMD()):
        """
        Solve the Three-echelons location problem by Pulp

        Parameters
        ----------
        solver: pulp solver
            any pulp solver, like
            - PULP_CBC_CMD()
            - GUROBI_CMD()
            - CPLEX_CMD()
        """
        # check if the parameters are loaded to pulp
        if self.I is None or self.J is None or self.K is None or self.L is None:
            raise ValueError("The parameters are not loaded to pulp.")
        print("loading to pulp ...")
        self.load_to_pulp()
        print("solving by pulp...")
        self.solve_by_pulp(solver)
        print("getting the solution...")
        return self.get_solution_by_pulp()
