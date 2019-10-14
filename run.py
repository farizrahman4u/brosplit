from brosplitlib import *


# rules

# Workout should not repeat the same day
def rule1(cell):
    for cell2 in cell.row:
        if cell2 != cell and cell.value == cell2.value:
            return -10.
    return 1.

# Need at least 24 hour rest period for each muscle
def rule2(cell):
    if not cell.value:
        return 1.
    if cell.i > 0:
        previous_day = cell.matrix[cell.i - 1]
        for cell2 in previous_day:
            if cell2.value == cell.value:
                return -5.
    if cell.i < len(cell.matrix) - 1:
        next_day = cell.matrix[cell.i + 1]
        for cell2 in next_day:
            if cell2.value == cell.value:
                return -5.
    return 1.

# At least 2 chest workouts per schedule?
def rule3(cell):
    for cell2 in cell.row:
        if cell2.value == 'chest':
            return 1.
    num_chest_days = 0
    for row in cell.matrix:
        for cell2 in row:
            if cell2.value == 'chest':
                num_chest_days += 1
                if num_chest_days == 2:
                    return 1.
                continue
    return -5.

rules = [rule1, rule2, rule3]

matrix = get_random_schedule_matrix(num_days=4, max_muscles_per_day=4)

for _ in range(1000):
    evolve(matrix, rules)

print_schedule(matrix)
