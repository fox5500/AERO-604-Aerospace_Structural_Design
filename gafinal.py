import random
import numpy as np
from DOEmethods import LHS


def inertia_calc(t, h, w):
    # RETURNS THE AREA MOMENT OF INERTIA OF STIFFENERS
    # t - THICKNESS OF SHEET BENT INTO STIFFENER, in.
    # h - EFFECTIVE HEIGHT OF STIFFENER, in.
    # w - WIDTH OF STIFFENER, in.
    #### TOP-HALF ####
    A_top = abs(h - t) * t
    x_barT = -w / 2
    y_barT = -h / 2
    I_xxTop = (1 / 12) * (w ** 3 * t)
    I_yyTop = (1 / 12) * (t ** 3 * w)
    #### BOTTOM-HALF ####
    A_bot = w * t
    x_barB = -t / 2
    y_barB = 0.0
    I_xxBot = (1 / 12) * (t ** 3 * abs(h - t))
    I_yyBot = (1 / 12) * (abs(h - t) ** 3 * t)
    #### ADJUSTED VALUES ####
    x_barTot = ((x_barT * A_top) + (x_barB * A_bot)) / (A_top * A_bot)
    y_barTot = ((y_barT * A_top) + (y_barB * A_bot)) / (A_top * A_bot)
    r_xTop = abs(x_barTot - x_barT)
    r_yTop = abs(y_barTot - y_barT)
    r_xBot = abs(x_barTot - x_barB)
    r_yBot = abs(y_barTot - y_barB)
    I_xxTopN = (r_xTop ** 2 * A_top) + I_xxTop
    I_yyTopN = (r_yTop ** 2 * A_top) + I_yyTop
    I_xxBotN = (r_xBot ** 2 * A_bot) + I_xxBot
    I_yyBotN = (r_yBot ** 2 * A_bot) + I_yyBot
    #### TOTAL VALUES ####
    I_xxTot = I_xxTopN + I_xxBotN
    I_yyTot = I_yyTopN + I_yyBotN
    return I_xxTot, I_yyTot


def buckle_eval(input_vars):
    #### MATERIAL PROPS ####
    E = 11e06               # ELASTIC MODULUS, psi.
    nu = 0.3                # POISSON'S RATIO
    sigma_y = 50e03         # YIELD STRESS, psi.
    rho = 0.1               # DENSITY, lb/in.^3

    #### PLATE CHARACTERISTICS ####
    w_plate = 60.0          # PANEL WIDTH, in.
    d_panel = 90.0          # PANEL DEPTH, in.
    l_panel = 40.0          # PANEL LOAD, lbf/in.
    k_c = 7.2               # PLATE BUCKLING COEFFICIENT

    #### REFERENCE SLENDERNESS RATIO ####
    c = 4.0                 # BOUNDARY CONDITION COEFFICIENT
    slender_ref = np.sqrt((np.pi ** 2 * E * c) / sigma_y)

    #### VARIABLE DEFINITIONS ####
    t_skin  = input_vars[0]
    t_stiff = input_vars[1]
    n_stiff = input_vars[2]
    h_stiff = input_vars[3]
    w_stiff = input_vars[4]
    # if (input_vars == 0).any():
    #     print(input_vars)
    #     user_input = int(input("Pausing for debugging"))
    #### TEST CONDITIONS ####
    w_domain = w_plate / n_stiff
    A_skin   = w_domain * t_skin
    A_stiff  = (abs(h_stiff - t_stiff) * t_stiff) + (w_stiff * t_stiff)
    F_stiff  = l_panel * w_domain * (A_stiff / (A_stiff + A_skin))
    F_skin   = l_panel * w_domain * (A_skin / (A_stiff + A_skin))
    N_skin   = F_skin / w_domain

    #### COMPUTING STIFFENER BUCKLING ####
    I_xx, I_yy = inertia_calc(t_stiff, h_stiff, w_stiff)
    if I_xx < I_yy:                     # TWO-DIRECTION BUCKLING CONDITION CHECK
        I_test = I_xx
    else:
        I_test = I_yy
    r_gyration  = np.sqrt(I_test / A_stiff)
    slender_rat = d_panel / r_gyration
    if slender_rat > slender_ref:       # CHECKING FOR EULER OR JOHNSON SOLUTION CONDITION
        sigma_crS = (c * (np.pi ** 2) * E) / ((d_panel / r_gyration) ** 2)
    else:
        sigma_crS = sigma_y * (1.0 - ((sigma_y * (d_panel / r_gyration) ** 2) / (4 * c * (np.pi ** 2) * E)))
    sigma_stiff = F_stiff / A_stiff

    #### COMPUTING PLATE BUCKLING ####
    sigma_crP   = (np.pi ** 2 * k_c * E) / (12 * (1 - nu ** 2)) * (t_skin / w_domain) ** 2
    if N_skin == 0 or A_skin == 0:
        print("N_skin = ", N_skin)
        print("A_skin = ", A_skin)
        user_input = int(input("Pausing for debugging"))
    sigma_plate = N_skin / A_skin

    #### DID SOMETHING BUCKLE? ####
    # sigma_crS - CRITICAL BUCKLING STRESS FOR STIFFENER
    # sigma_crP - CRITICAL BUCKLING STRESS FOR PLATE
    if sigma_crS > sigma_stiff or sigma_crP > sigma_plate:
        failure = 0
    else:
        failure = 1

    #### ASSEMBLY CHARACTERISTICS ####
    m_assem = ((A_skin * d_panel) + (A_stiff * d_panel * n_stiff)) * rho

    output_vals = np.array([failure, m_assem])
    return output_vals


# ADJUST DVs TO ACCOUNT FOR THE UPPER AND LOWER BOUNDS OF EACH PARAMETER
def adjust_DVs(population, bounds):
    for j in range(population.shape[1]):
        for i in range(population.shape[0]):
            range_size = bounds[1, j] - bounds[0, j]
            population[i, j] = bounds[0, j] + (range_size * population[i, j])
            if j == 2:
                population[i, j] = round(population[i, j], 0)
    return population


# DEFINE THE CONSTRAINT CHECK OPERATOR
def constraint_check(population, DV_chars):
    # CHECKS TO SEE IF SET OF PARAMETERS HAS BUCKLED
    mask = (DV_chars[:, 0] == 1)
    indices = np.where(mask)[0]
    population = np.delete(population, indices, axis=0)
    DV_chars = np.delete(DV_chars, indices, axis=0)
    return population, DV_chars


# DEFINE THE CROSSOVER OPERATOR
def crossover(parent1, parent2, bounds):
    # GENERATE A RANDOM WEIGHT FOR THE LINEAR INTERPOLATION
    weight = np.random.uniform(size=parent1.shape)

    # INTERPOLATE BETWEEN THE PARENT VALUES USING THE WEIGHT
    new_values = (1 - weight) * parent1 + weight * parent2

    # APPLY BOUNDS CHECKING TO THE NEW VALUES
    new_values = np.clip(new_values, bounds[0, :], bounds[1, :])
    new_values[2] = round(new_values[2], 0)
    return new_values


# DEFINE THE MUTATION OPERATOR
def mutate(offspring, mutation_rate, bounds):
    for i in range(offspring.shape[0]):
        if np.random.rand() < mutation_rate:
            offspring[i] += np.random.normal(scale=0.1, size=offspring.shape[1])
            offspring[i] = np.clip(offspring[i], 0, 5)
    return offspring


# FUNCTION TO HOPEFULLY PREVENT ALGORITHM FROM BREAKING
def check_zero(population):
    # CHANGING WHERE A PARAMETER IS MISTAKENLY SET TO ZERO BECAUSE APPARENTLY THAT'S A THING
    row_ind, col_ind = np.where(population == 0)
    for row, col in zip(row_ind, col_ind):
        column = population[:, col][population[:, col] != 0]
        population[row, col] = np.random.choice(column)
    return population


# FUNCTION TO CHECK IF INDIVIDUAL VIOLATES BOUNDS
def check_bounds(parents, bounds):
    yay_or_nay = 0
    for i in range(parents.shape[0]):
        if parents[i] < bounds[0] or parents[i] > bounds[1]:
            yay_or_nay = 1
    return yay_or_nay


def genetic_algorithm(bounds, population_size, num_generations, mutation_rate):
    # INITIALIZE POPULATION
    initial_population = np.array(LHS(5, population_size))

    # ADJUST STARTING POPULATION TO ACCOUNT FOR DESIGN LIMITS
    population = adjust_DVs(initial_population, bounds)

    # ITERATE OF NUMBER OF GENERATIONS
    for i in range(num_generations):
        # EVALUATE POPULATION TO CHECK FOR BUCKLING
        DV_chars = np.array([buckle_eval(x) for x in population])

        # SEARCH DV_chars TO DETERMINE IF INDIVIDUAL VIOLATED CONSTRAINT AND REMOVE BOTH FROM GENE POOL
        population, DV_chars = constraint_check(population, DV_chars)

        # RANK SURVIVING INDIVIDUALS BASED ON LOWEST MASS
        ranked_population = np.concatenate((population, DV_chars), axis=1)
        ranked_population = ranked_population[np.argsort(DV_chars[:, 1]), :]
        population = ranked_population[:, :5]

        # SELECT TOP % OF PARENTS TO MATE
        percent2mate = 10
        number2mate = population_size * (percent2mate / 100)
        if not number2mate.is_integer():
            print("The percent2mate results in a non-integer value for number2mate.")
            break
        parents = population[:int(number2mate), :]

        # PRODUCE OFFSPRING W/MUTATIONS AND RETAIN PARENTS
        num_children = int(population_size - number2mate)
        offspring = np.zeros((num_children, 5))
        for j in range(num_children):
            p1, p2 = random.sample(range(9), 2)
            offspring[j, :] = crossover(parents[p1, :], parents[p2, :], bounds)
        offspring = mutate(offspring, mutation_rate, bounds)
        new_pop = np.vstack((offspring, parents))

        # CHECK FOR ZEROS IN THE POPULATION (Should be obsolete with check_bounds())
        new_pop = check_zero(new_pop)
        population = new_pop
    # CHECK FOR ZEROS IN THE POPULATION...AGAIN
    population = check_zero(population)

    # EVALUATE THE NEW POPULATION FOR BUCKLING
    DV_chars = np.array([buckle_eval(x) for x in population])

    # FINDING PARAMETERS WITH MINIMUM MASS
    min_mass = np.argmin(DV_chars)
    best_mass = DV_chars[min_mass, 1]
    best_design = population[min_mass, :]

    return best_design, best_mass


# OPTIMIZATION START
# DENOTE DV BOUNDS
dim_bounds = np.array([[0.05, 0.10, 3.00, 0.50, 1.00],
                      [1.00, 1.00, 30.0, 2.00, 2.00]])
#                     [[t_skinL, t_stiffL, n_stiffL, h_stiffL, w_stiffL],
#                     [t_skinU, t_stiffU, n_stiffU, h_stiffU, w_stiffU]]

# RUN OPTIMIZER
opt_soln, mass = genetic_algorithm(dim_bounds, population_size=100, num_generations=100, mutation_rate=0.05)
round_num = 4
print("t_skin:  ", round(opt_soln[0], round_num))
print("t_stiff: ", round(opt_soln[1], round_num))
print("n_stiff: ", opt_soln[2])
print("h_stiff: ", round(opt_soln[3], round_num))
print("w_stiff: ", round(opt_soln[4], round_num))
print("Mass:    ", round(mass, round_num))
