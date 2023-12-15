
class CFLP:
    """
    Definition
    ----------

    The Capacitated Fixed-Charge Location Problem (CFLP)

    The CFLP is a combinatorial optimization problem that consists of locating
    a set of facilities to minimize the total cost of serving the clients
    while respecting the capacity of the facilities.

    The CFLP is a generalization of the Uncapacitated Facility Location

    Formulation
    -----------

    index sets:
        - I: set of clients
        - J: set of facilities
    
    parameters:
    variables:
    objective:
    constraints:

    Parameters
    ----------

    I: 
        set of clients
    J: set of facilities
    d: demand of clients
    f: fixed cost of facilities
    c: cost of serving clients from facilities
    q: capacity of facilities

    Attributes
    ----------
    self.I: set of clients
    self.J: set of facilities
    self.d: demand of clients

    """
