import numpy as np

# Some domain knowledge
num_days = 4
max_muscles_per_day = 4
muscles = ['chest', 'back', 'shoulders', 'legs', 'biceps', 'triceps', 'forearms']
muscles += ['calves']  # I have small calves, so I train them independently from legs
muscles += [None]
muscles_index = {m:i for (i, m) in enumerate(muscles)}

big_muscles = ['chest', 'back', 'shoulders', 'legs']
small_muscles = ['biceps', 'triceps', 'forearms']
small_muscles += ['calves']

def get_random_schedule_matrix(num_days=num_days, max_muscles_per_day=max_muscles_per_day):
    matrix = np.random.random((num_days, max_muscles_per_day, len(muscles)))
    matrix = np.exp(matrix)
    s = np.sum(matrix, -1, keepdims=True)
    matrix /= s
    return matrix

def devectorize(matrix):
    days = []
    for row in matrix:
        day = []
        for prob in row:
            musc_idx = np.argmax(prob)
            musc = muscles[musc_idx]
            if musc:
                day.append(musc)
        days.append(day)
    return days

_cell_cache = {}
def get_cell(matrix, i, j):
    k = (id(matrix), i, j)
    try:
        return _cell_cache[k]
    except KeyError:
        cell = Cell(matrix, i, j)
        _cell_cache[k] = cell
        return cell

class Cell():
    def __init__(self, matrix, i, j):
        self.i = i
        self.j = j
        self.raw_matrix = matrix


    @property
    def matrix(self):
        m, n = self.raw_matrix.shape[:2]
        return [[get_cell(self.raw_matrix, i, j) for j in range(n)] for i in range(m)]

    @property
    def prob_dist(self):
        return self.raw_matrix[self.i, self.j]

    @property
    def value_idx(self):
        return np.argmax(self.prob_dist)

    @property
    def value(self):
        return muscles[self.value_idx]

    @property
    def row(self):
        try:
            return self._row
        except AttributeError:
            self._row = [get_cell(self.raw_matrix, self.i, j) for j in range(self.raw_matrix.shape[1])]
            return self._row

    @property
    def column(self):
        try:
            return self._column
        except AttributeError:
            self._column = [get_cell(self.raw_matrix, i, self.j) for i in range(self.raw_matrix.shape[0])]
            return self._row


def get_score_matrix(matrix, rules):
    m, n = matrix.shape[:2]
    score = lambda cell: min([rule(cell) for rule in rules])
    return np.array([[score(get_cell(matrix, i, j)) for j in range(n)] for i in range(m)])

def get_random_mask(score_matrix):
    rand_mask = np.zeros(score_matrix.shape[:2])
    mx = np.max(score_matrix)
    ltz = score_matrix < 0
    rand_mask = 1. * ltz + (1. - ltz) * (1. - (score_matrix /mx)) # sorry
    return rand_mask

def apply_random_mask(matrix, random_mask):
    # careful, inplace operation
    rand1 = np.random.random(matrix.shape)
    rand2 = np.random.random(matrix.shape[:2])
    gate =  rand2 < random_mask
    rand1 = np.exp(rand1)
    rand1 /= np.sum(rand1, axis=-1, keepdims=True)
    matrix += np.expand_dims(gate, -1) * (rand1 - matrix)

def evolve(matrix, rules):
    apply_random_mask(matrix, get_random_mask(get_score_matrix(matrix, rules)))

def print_schedule(matrix):
    schedule = devectorize(matrix)
    out = ''
    for i, muscles in enumerate(schedule):
        out += 'Day {} - {}'.format(i + 1, ', '.join(muscles)) + '\n'
    print(out)
