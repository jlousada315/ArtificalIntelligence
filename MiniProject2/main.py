import probability


# ====================================

class Problem:

    def __init__(self, fh):
        # Place here your code to load problem from opened file object fh # and use probability.BayesNet() to create
        # the Bayesian network
        self.fh = fh
        self.rooms = []
        self.connections = []
        self.sensors = []
        self.measures = []
        self.prob = []

        self.load()

    def solve(self):
        # Place here your code to determine the maximum likelihood solution
        # returning the solution room name and likelihood
        # use probability.elimination_ask() to perform probabilistic inference return (room, likelihood)
        pass

    def load(self):
        pass

    def save(self):
        pass


def solver(input_file):
    return Problem(input_file).solve()


# ====================================

class State:

    def __init__(self):
        pass


# ====================================

class Rooms:

    def __init__(self, rooms: tuple):
        self.rooms = rooms


# ====================================

class Connections:

    def __init__(self, connects: tuple):
        self.connects = connects


# ====================================

class Sensors:

    def __init__(self, sensors: tuple, rates: tuple, rooms: tuple):
        self.sensors = sensors
        self.rates = rates
        self.rooms = rooms


# ====================================

class Prob:

    def __init__(self, prob: float):
        self.prob = prob

    def get_probability(self):
        return self.prob

    def set_probability(self, prob: float):
        self.prob = prob


# ====================================
"""
class Measurement:

    def __init__(self, sensors: list[Sensors], measure: list[str]):
        self.sensors = sensors
        self.measure = measure
"""
# ====================================

T, F = True, False


fire = probability.BayesNet([
    ('R02_0', '', 0.5000000000000000),
    ('R03_0', '', 0.5000000000000000),

    ('R03_1', 'R02_0 R03_0',
        {(T, T): 1, (T, F):  0.07549526619046759, (F, T): 1, (F, F): 0}),
    ('R02_1', 'R02_0 R03_0',
        {(T, T): 1, (T, F): 1, (F, T): 0.07549526619046759, (F, F): 0}),
    ('S01_1', 'R03_1', {T: 0.9423140000000000, F: 0.1215520000000000}),

    ('R03_2', 'R02_1 R03_1',
        {(T, T): 1, (T, F):  0.07549526619046759, (F, T): 1, (F, F): 0}),
    ('R02_2', 'R02_1 R03_1',
        {(T, T): 1, (T, F): 1, (F, T): 0.07549526619046759, (F, F): 0}),
    ('S01_2', 'R03_2', {T: 0.9423140000000000, F: 0.1215520000000000}),

    ('R03_3', 'R02_2 R03_2',
        {(T, T): 1, (T, F):  0.07549526619046759, (F, T): 1, (F, F): 0}),
    ('R02_3', 'R02_2 R03_2',
        {(T, T): 1, (T, F): 1, (F, T): 0.07549526619046759, (F, F): 0}),
    ('S01_3', 'R03_3', {T: 0.9423140000000000, F: 0.1215520000000000}),

    ('R03_4', 'R02_3 R03_3',
        {(T, T): 1, (T, F):  0.07549526619046759, (F, T): 1, (F, F): 0}),
    ('R02_4', 'R02_3 R03_3',
        {(T, T): 1, (T, F): 1, (F, T): 0.07549526619046759, (F, F): 0}),
    ('S01_4', 'R03_3', {T: 0.9423140000000000, F: 0.1215520000000000})])


print(probability.elimination_ask('R03_4', dict(S01_1=F, S01_2=T, S01_3=T, S01_4=T), fire).show_approx())
