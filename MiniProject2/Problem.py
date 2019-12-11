
import probability


class Problem:

    def __init__(self, fh):
        # Place here your code to load problem from opened file object fh # and use probability.BayesNet() to create
        # the Bayesian network
        self.fh = fh
        self.room = []
        self.connections = []
        self.sensor = []
        self.measures = []
        self.prob = 0

        self.load()

    def solve(self):
        # Place here your code to determine the maximum likelihood solution
        # returning the solution room name and likelihood
        # use probability.elimination_ask() to perform probabilistic inference return (room, likelihood)
        pass


    def load(self):
        fo = open(self.fh, "r")
        myList = fo.readlines()
        """" loads a problem from a (opened) file object f """
        rooms = []
        connection = []
        sensors = []
        measurements = []

        myList = [i.replace('  ', ' ') for i in myList]
        myList = [i.replace('\n', '') for i in myList]

        myList = [i.split(' ') for i in myList]

        for i in range(len(myList)):
            if myList[i][0] == 'R':
                rooms.append(myList[i][1:])
            elif myList[i][0] == 'C':
                connection.append(myList[i][1:])
            elif myList[i][0] == 'S':
                sensors.append(myList[i][1:])
            elif myList[i][0] == 'P':
                probab = myList[i][1]
            elif myList[i][0] == 'M':
                measurements.append(myList[i][1:])
            elif myList[i][0] == '':
                pass
            else:
                print('Wrong input format')
                exit()
        # _______________________ Room class build

        for i in range(len(rooms[0])):
            self.room.append(Room(rooms[0][i]))

        # _______________________ Connections class build

        for i in range(len(connection[0])):
            self.connections.append(Connections(connection[0][i]))

        # _______________________ Sensors class build

        for n in range(len(sensors[0])):
            sens_split = sensors[0][n].split(':')
            self.sensor.append(Sensor(sens_split[0], sens_split[1], sens_split[2], sens_split[3]))

        # _______________________ Measurement class build
        for i in range(len(measurements)):
            tuple_sensors = ()
            tuple_flag = ()
            for n in range(len(measurements[i])):
                meas_split = measurements[i][n].split(':')
                tuple_sensors += meas_split[0],
                tuple_flag += meas_split[1],

            self.measures.append(Measurement(tuple_sensors, tuple_flag))

        self.prob = probab

    def save(self):
        pass


def solver(input_file):
    return Problem(input_file).solve()


class Room:

    def __init__(self, room: str):
        self.room = room

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


class Connections:

    def __init__(self, connects: tuple):
        self.connects = connects

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


class Sensor:

    def __init__(self, sensor: str, room: Room, tpr: float, fpr: float):
        self.sensor = sensor
        self.room = room
        self.tpr = tpr
        self.fpr = fpr

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


class Measurement:

    def __init__(self, sensors: tuple, measure: tuple):
        self.sensors = sensors
        self.measure = measure

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


problem = Problem('example.txt')

for i in problem.room:
    i.print()

for i in problem.connections:
    i.print()

for i in problem.sensor:
    i.print()

for i in problem.measures:
    i.print()

print("probability: %s" % problem.prob)

# =====================================

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