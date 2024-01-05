# Operations Research Models for Supply Chain Design
## Table of Contents
- [Introduction](#introduction)
- [UFLP (Uncapacitated Facility Location Problem)](#uflp-uncapacitated-facility-location-problem)
- [CFLP (Capacitated Facility Location Problem)](#cflp-capacitated-facility-location-problem)
- [Three-echelon supply chain network design](#three-echelon-supply-chain-network-design)

## Introduction
Operations Research (OR) is the discipline of applying advanced analytical methods to help make better decisions. By using techniques such as mathematical modeling to analyze complex situations, operations research gives executives the power to make more effective decisions and build more productive systems based on:

- **Data-driven decision making**: using facts to guide management actions.
- **Quantitative analysis**: using mathematical and statistical models to support decision making.
- **Problem structuring and abstraction**: using models to understand and analyze specific situations and to communicate the essence of complex systems.
- **Optimization**: using mathematical techniques to identify the best decisions.

> [!NOTE]
> The following models are formulated using the premise that the demand must be satisfied independently of the availability of the supply.
# UFLP (Uncapacitated Facility Location Problem)
- [UFLP](https://en.wikipedia.org/wiki/Facility_location_problem#Uncapacitated_facility_location_problem_(UFLP))
- [UFLP formulation](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119584445)

## Problem Description
UFLP chooses facility locations in
order to minimize the total cost of building the facilities and transporting goods from
facilities to customers. The UFLP is a combinatorial optimization problem. It is a special case of the capacitated facility location problem (CFLP) where the capacity of all facilities is infinite.

## Model
### Sets
- $I$: set of customers
- $J$: set of potential facility locations
### Parameters
- $h_i$: annual demand of customer $i \in I$
- $c_{ij}$: cost to transform one unit of demand from facility $j \in J$ to customer $i \in I$
- $f_j$: fixed annual cost to open a facility at site $j \in J$
> distances can be computed using:
> - [Eucledian distance](https://en.wikipedia.org/wiki/Euclidean_distance)
>   $$ distance(i, j) = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2} $$
> - [Manhattan distance](https://en.wikipedia.org/wiki/Taxicab_geometry)
>   $$ distance(i, j) = |x_i - x_j| + |y_i - y_j| $$
> - [Great-circle distance](https://en.wikipedia.org/wiki/Great-circle_distance)
>   $$ distance(i, j) = 2 * r * arcsin(\sqrt{sin^2(\frac{\phi_i - \phi_j}{2}) + cos(\phi_i) * cos(\phi_j) * sin^2(\frac{\lambda_i - \lambda_j}{2})}) $$
>   where r is the radius of earth, aproximately 6371.01 km, and $\phi_i, \phi_j, \lambda_i, \lambda_j$ are the latitude and longitude of customer $i$ and facility $j$ respectively.
> - [Highway/Network distance](https://project-osrm.org/):
> the distance between two points is the shortest path between them in the road network.
> - [Matrix Distance](https://en.wikipedia.org/wiki/Distance_matrix): A matrix containing the distances between all pairs of customers and facilities.
### Decision Variables
- $x_j$: 1 if a facility is opened at site $j \in J$, 0 otherwise
- $y_{ij}$: the fraction of the customer $i$'s demand that is served by facility $j$

### Objective Function
$$ \min \sum_{j \in J} f_j x_j + \sum_{i \in I} \sum_{j \in J} h_{i} c_{ij} y_{ij} $$
### Constraints
the total of $y_{ij}$ used to serve customer $i$ must be equal to 1 to satisfy the demand of customer $i$.

$$ \sum_{j \in J} y_{ij} = 1 \quad \forall i \in I $$

Each facility $j$ can only serve customers if it is opened.

$$ y_{ij} \leq x_j \quad \forall i \in I, j \in J $$

logical constraints

$$ x_j \in \{0, 1\} \quad \forall j \in J $$
$$ y_{ij} \geq 0 \quad \forall i \in I, j \in J $$

# CFLP (Capacitated Facility Location Problem)
- [CFLP](https://en.wikipedia.org/wiki/Facility_location_problem#Capacitated_facility_location_problem_(CFLP))
- [CFLP formulation](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119584445)

## Problem Description
The capacitated facility location problem (CFLP) is a classical combinatorial optimization problem. It is a generalization of the facility location problem (FLP) and the uncapacitated facility location problem (UFLP). In the CFLP, there are a set of potential facility locations and a set of customers. Each facility has a capacity and an opening cost. Each customer has a demand and a connection cost. The objective is to minimize the total cost of opening facilities and connecting customers to open facilities while satisfying the capacity constraints of the facilities.

## Model
### Sets
- $I$: set of customers
- $J$: set of potential facility locations
### Parameters
- $h_i$: annual demand of customer $i \in I$
- $c_{ij}$: cost to transform one unit of demand from facility $j \in J$ to customer $i \in I$
- $f_j$: fixed annual cost to open a facility at site $j \in J$
- $v_j$: maximum capacity of facility $j \in J$
### Decision Variables
- $x_j$: 1 if a facility is opened at site $j \in J$, 0 otherwise
- $y_{ij}$: the fraction of the customer $i$'s demand that is served by facility $j$
> the transportation cost $c_{ij}$ might be of the form 
> $$ k * distance(i, j) $$
> where $k$ is a constant and $distance(i, j)$ is the distance between customer $i$ and facility $j$.

### Objective Function
$$ \min \sum_{j \in J} f_j x_j + \sum_{i \in I} \sum_{j \in J} h_{i} c_{ij} y_{ij} $$
### Constraints
the total of $y_{ij}$ used to serve customer $i$ must be equal to 1 to satisfy the demand of customer $i$.

$$ \sum_{j \in J} y_{ij} = 1 \quad \forall i \in I $$

Each facility $j$ can only serve customers if it is opened.

$$ y_{ij} \leq x_j \quad \forall i \in I, j \in J $$

the annual demand of the customers served by facility $j$ must not exceed the capacity of facility $j$.

$$ \sum_{i \in I} h_i y_{ij} \leq v_j \quad \forall j \in J $$

logical constraints

$$ x_j \in \{0, 1\} \quad \forall j \in J $$

$$ y_{ij} \geq 0 \quad \forall i \in I, j \in J $$

Optional constraints

$$ \sum_{j \in J} v_j x_j \leq \sum_{i \in I} h_i $$

> the total capacity of the opened facilities is sufficient to serve all the customers. Is redundant but tightens the formulation.

# Three-echelon supply chain network design
- [Three-echelon supply chain network design](https://en.wikipedia.org/wiki/Supply_chain_network)
- [Three-echelon supply chain network design formulation](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119584445)

## Problem Description
This problem is concerned with a three-echelon system
consisting of plants, DCs, and customers. The customer locations are fixed, but the plant
and DC locations are to be optimized.

## Model
### Sets
- $I$: set of customers
- $J$: set of potential DC locations
- $K$: set of potential plant locations
- $L$: set of products

### Parameters

#### Demands and Capacities
- $h_{il}$: annual demand of customer $i \in I$ for product $l \in L$
- $v_{j}$: maximum capacity of DC $j \in J$
- $b_{k}$: maximum capacity of plant $k \in K$
- $s_{l}$: units of capacity consumed by one unit of product $l \in L$
#### Costs
- $f_{j}$: fixed annual cost to open a DC at site $j \in J$
- $g_{k}$: fixed annual cost to open a plant at site $k \in K$
- $c_{ijl}$: cost to transform one unit of product $l \in L$ from DC $j \in J$ to customer $i \in I$
- $d_{ikl}$: cost to transform one unit of product $l \in L$ from plant $k \in K$ to DC $j \in J$

### Decision Variables
- $x_{j}$: 1 if a DC is opened at site $j \in J$, 0 otherwise
- $z_{k}$: 1 if a plant is opened at site $k \in K$, 0 otherwise
- $y_{ijl}$: number of units of product $l \in L$ that are shipped from DC $j \in J$ to customer $i \in I$
- $w_{ikl}$: number of units of product $l \in L$ that are shipped from plant $k \in K$ to DC $j \in J$

### Objective Function
$$ \min \sum_{j \in J} f_{j} x_{j} + \sum_{k \in K} g_{k} z_{k} + \sum_{l \in L} \left[ \sum_{j \in J} \sum_{i \in I} c_{ijl} y_{ijl} + \sum_{k \in K} \sum_{j \in J} d_{ikl} w_{ikl} \right] $$

### Constraints
the demand of customer $i$ for product $l$ must be satisfied by the DCs.
$$ \sum_{j \in J} y_{ijl} = h_{il} \quad \forall i \in I, l \in L $$
the capacity of the DCs must not be exceeded.
$$ \sum_{i \in I} s_{l} y_{ijl} \leq v_{j} x_{j} \quad \forall j \in J, l \in L $$
the input and output of the DCs must be balanced.
$$ \sum_{i \in I} y_{ijl} = \sum_{k \in K} w_{ikl} \quad \forall j \in J, l \in L $$
the capacity of the plants must not be exceeded.
$$ \sum_{j \in J} s_{l} w_{ikl} \leq b_{k} z_{k} \quad \forall k \in K, l \in L $$
logical constraints
$$ x_{j} \in \{0, 1\} \quad \forall j \in J $$
$$ z_{k} \in \{0, 1\} \quad \forall k \in K $$
$$ y_{ijl} \geq 0 \quad \forall i \in I, j \in J, l \in L $$
$$ w_{ikl} \geq 0 \quad \forall i \in I, k \in K, l \in L $$

# References



