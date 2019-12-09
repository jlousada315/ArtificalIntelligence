import time
import io
import sys
from abc import abstractmethod
from collections import defaultdict
import copy
from datetime import datetime, timedelta
import math

# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput

filedir = '/Users/joaolousada/Documents/5ºAno/IASD'

from search import Problem, astar_search


class ASARProblem(Problem):

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
                state, if there is a unique goal. Your subclass's constructor can add
                other arguments."""
        self.initial = initial
        self.goal = goal
        super().__init__(self.initial, self.goal)
        self.air_port = []
        self.air_plane = []
        self.leg = []
        self.air_rot = []
        self.profit = 0
        self.nr = 0

    @abstractmethod
    def actions(self, state):
        """Return the actions that can be executed in the given
                state. The result would typically be a list, but if there are
                many actions, consider yielding them one at a time in an
                iterator, rather than building them all at once.
                info contains: airplane code, airport of arrival, flight duration, rotation time, profit"""
        possible_actions = []
        time_limit = True

        for n in range(len(self.air_plane)):
            if state.get_values()[n] is None:
                for p in range(len(self.air_port)):
                    info = (self.air_plane[n], self.air_port[p], 0)
                    possible_actions.append(info)

            else:
                for k in range(len(self.leg)):
                    if state.adict.get(self.air_plane[n])[-2] == self.leg[k].get_air1():
                        p_time = state.get_time(self.air_plane[n])
                        b_time = time_sum(p_time, self.leg[k].get_duration())
                        a_time = time_sum(b_time, self.air_plane[n].get_rotation_time())

                        if int(b_time) < int(self.get_otime_string(self.leg[k].get_air2())):
                            aux = time_difference(self.get_otime_string(self.leg[k].get_air2()), b_time)
                            p_time = time_sum(p_time, aux)
                            b_time = time_sum(p_time, self.leg[k].get_duration())
                            a_time = time_sum(b_time, self.air_plane[n].get_rotation_time())

                        info = (self.air_plane[n], self.leg[k].get_air2(), a_time,
                                self.leg[k].get_cost(self.leg[k].get_profit(self.air_plane[n].get_model())))

                        for p in self.air_port:
                            if 0000 < int(a_time) < int(p.get_otime()):
                                if self.leg[k].get_air2() == p.get_tag() and int(a_time) + 2400 - int(p.get_otime()) > \
                                        int(p.get_ctime()) - int(p.get_otime()):
                                    time_limit = False
                            else:
                                if self.leg[k].get_air2() == p.get_tag() and int(a_time) - int(p.get_otime()) > \
                                        int(p.get_ctime()) - int(p.get_otime()):
                                    time_limit = False
                            break

                        if self.leg[k].__contains__(state.get_trips(state.get_trips_dict())) is False and time_limit is True and int(b_time) > int(self.get_otime_string(self.leg[k].get_air2())):
                            possible_actions.append(info)

        if possible_actions is not None:
            return possible_actions
        else:
            print('No possible actions were returned')
            exit()

    @abstractmethod
    def result(self, state, action):
        """Return the state that results from executing the given
               action in the given state. The action must be one of
               self.actions(state)."""
        copied = dict((k, v) for k, v in state.adict.items())
        for i in state.get_keys():
            if i == action[0]:
                key_idx = i

        if len(action) == 3 and state.adict.get(key_idx) is None:  # for the initial state
            new_state = State(copied)
            next_state = tuple((action[1].get_tag(), action[1].get_otime()))
            new_state.set_values(key_idx, next_state)
        elif len(action) == 4:
            new_state = State(copied)
            next_state = tuple([action[1], action[2]])
            new_state.set_values(key_idx, next_state)
        self.nr += 1
        return new_state

    @abstractmethod
    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        keys = state.get_keys()
        flag = False
        if len(self.leg) == len(state.get_trips(state.get_trips_dict())):
            for i in keys:
                if state.get_values_of_key(i) is not None:
                    flag = (state.get_values_of_key(i)[0] == state.get_values_of_key(i)[-2])
                if flag is False:
                    return flag
        return flag

    @abstractmethod
    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + (action[-1])

    @abstractmethod
    def h(self, n):
        """" returns the heuristic of node n """

        legs = []
        for i in self.leg:
            if i.__contains__(n.state.get_trips(n.state.get_trips_dict())) is False:
                legs.append(i)

        res = 0
        for leg in legs:
            res = n.path_cost + leg.get_cost(leg.get_min())
        return res

        """
        res = 0
        for leg in legs:
            res += self.get_max_profit() - leg.get_max()
        return res
        """
    @abstractmethod
    def load(self, file, state):
        """" loads a problem from a (opened) file object f """
        with open(file, "r") as f:
            rows = [l for l in (line.strip() for line in f) if l]

        airports = []
        airplanes = []
        legs = []
        classes = []

        rows = [i.replace('  ', ' ') for i in rows]
        myList = [i.split(' ') for i in rows]
        for i in range(len(myList)):
            if myList[i][0] == 'A':
                airports.append(myList[i][1:])
            elif myList[i][0] == 'P':
                airplanes.append(myList[i][1:])
            elif myList[i][0] == 'L':
                legs.append(myList[i][1:])
            elif myList[i][0] == 'C':
                classes.append(myList[i][1:])
            elif myList[i][0] == '':
                pass
            else:
                print('Wrong input format')
                exit()

        # _______________________ Airports class build

        for i in range(len(airports)):
            self.air_port.append(Airport(airports[i][0], airports[i][1], airports[i][2]))

        # _______________________ Airplanes class build

        for i in range(len(airplanes)):
            self.air_plane.append(Airplane(airplanes[i][0], airplanes[i][1]))

        # _______________________ leg class build

        tuples = []

        for i in range(len(legs)):
            if len(legs[i][3:]) % 2 == 0:
                tuples.append(tuple(legs[i][3:]))
            else:
                print('Wrong input format. In Leg, tuple must be <class>/<profit> pair  ')
                exit()

            self.leg.append(Leg(legs[i][0], legs[i][1], legs[i][2], tuples[i]))
        # _______________________ Air Rotation class build

        for i in range(len(classes)):
            self.air_rot.append(AirRotation(classes[i][0], classes[i][1]))

        for i in range(len(self.air_plane)):
            for n in range(len(self.air_rot)):
                self.air_plane[i].set_rotation_time(self.air_rot[n])

        # ________________________ initial state

        for i in range(len(self.air_plane)):
            state.set_key(self.air_plane[i])
        return state

    @abstractmethod
    def save(self, file, state):
        """" saves a solution state s to a (opened) file object f """
        f = open(file, "w+")

        if state is None:
            f.write('Infeasible')
            f.close()
            exit()

        profit = 0
        keys = []
        values = []
        schedule = []
        routes = []
        tup = defaultdict(list)
        text = ''

        for x, y in state.adict.items():
            keys.append(x)
            values.append(y)

        for i in range(len(keys)):
            schedule.append(values[i][1:][::2])
            routes.append(values[i][0:][::2])

        for i in range(len(keys)):
            for p in range((len(schedule[i])) - 1):
                tup[keys[i]].append((schedule[i][p], routes[i][p], routes[i][p + 1]))

        for x, y in tup.items():
            text += 'S' + ' ' + x.get_code() + ' '
            for i in range(len(y)):
                text += y[i][0] + ' ' + y[i][1] + ' ' + y[i][2] + ' '
                profit += self.get_profit_leg(y[i][1], y[i][2], x.get_model())
            text += '\n'

        print(text, profit)
        print(self.nr)
        print(self.get_profit_so_far(state))
        f.write(text)
        f.write('P %d' % profit)

        f.close()

    def get_max_profit(self, max_profit=0):
        for i in range(len(self.leg)):
            partial = []
            for p in range(len(self.air_plane)):
                partial.append(self.leg[i].get_profit(self.air_plane[p].get_model()))
                partial.sort(reverse=True)
            max_profit += partial[0]
        return max_profit

    def get_max_legs(self, leg):
        partial = []
        for p in range(len(self.air_plane)):
            partial.append(leg.get_profit(self.air_plane[p].get_model()))
        partial.sort(reverse=True)
        return partial[0]

    def get_max_cost(self, max_cost = 0):
        for i in range(len(self.leg)):
            partial = []
            for p in range(len(self.air_plane)):
                partial.append(self.leg[i].get_cost(self.leg[i].get_profit(self.air_plane[p].get_model())))
                partial.sort(reverse=True)
            max_cost += partial[0]
        return max_cost

    def get_profit_leg(self, air1, air2, model):
        for i in self.leg:
            if i.airport1 == air1 and i.airport2 == air2:
                return i.get_profit(model)

    def get_otime_string(self, air1: str):
        for i in self.air_port:
            if i.get_tag() == air1:
                return i.get_otime()

    def get_profit_so_far(self, state):
        profit = 0
        keys = []
        values = []
        routes = defaultdict(list)

        for x, y in state.adict.items():
            keys.append(x)
            values.append(y)

        for i in range(len(keys)):
            if values[i] is not None and len(values[i]) > 2:
                routes[keys[i]] = values[i][0:][::2]

        for i in keys:
            if routes.get(i) is not None:
                for p in range(len(routes.get(i))-1):
                    profit += self.get_profit_leg(routes.get(i)[p], routes.get(i)[p + 1], i.get_model())
        return profit


# ______________________________________________________________________________


class Leg:

    def __init__(self, airport1, airport2, dl, ap):
        """" creates each Leg, containing dept. and arr. airports, flight duration, planes and profit."""
        self.airport1 = airport1
        self.airport2 = airport2
        self.dl = dl
        self.res = tuple(ap[n:n + 2] for n, i in enumerate(ap)
                         if n % 2 == 0)

    def get_air1(self):
        return self.airport1

    def get_air2(self):
        return self.airport2

    def get_duration(self):
        return self.dl

    def get_max(self):
        max = 0
        for p in range(len(self.res)):
            if max < int(self.res[p][1]):
                max = int(self.res[p][1])
        return max

    def get_min(self):
        min = 0
        for p in range(len(self.res)):
            if min > int(self.res[p][1]):
                min = int(self.res[p][1])
        return min

    def get_profit(self, model):
        for p in range(len(self.res)):
            if self.res[p][0] == model:
                return int(self.res[p][1])
                break

    def get_cost(self, profit):
        return self.get_max() - profit

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))

    def __contains__(self, item: list):
        t = (self.airport1, self.airport2)
        return t in item


# ______________________________________________________________________________


class Airport:

    def __init__(self, airport, otime, ctime):
        """" creates each Airport, containing airport tag, opening time and closing time"""
        self.airport = airport
        self.otime = otime
        self.ctime = ctime

    def __eq__(self, other):
        return self.airport == other

    def __hash__(self):
        return hash(self.airport)

    def get_tag(self):
        """"returns airport tag"""
        return self.airport

    def get_otime(self):
        """"returns opening time of specific airport"""
        return self.otime

    def get_ctime(self):
        """"returns closing time of specific airport"""
        return self.ctime

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


# ______________________________________________________________________________


class AirRotation:

    def __init__(self, model, rot_t):
        self.model = model
        self.rot_t = rot_t

    def get_rotation_time(self):
        return self.rot_t

    def get_model(self):
        return self.model

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


# ______________________________________________________________________________


class Airplane:

    def __init__(self, rcode, model):
        self.rcode = rcode
        self.model = model
        self.rotation_time = None

    def __eq__(self, other):
        return self.rcode == other.rcode and self.model == other.model

    def __hash__(self):
        return hash(self.rcode)

    def get_code(self):
        return self.rcode

    def get_model(self):
        return self.model

    def set_rotation_time(self, A: AirRotation):
        if A.get_model() == self.model:
            self.rotation_time = A.get_rotation_time()

    def get_rotation_time(self):
        return self.rotation_time

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


# ______________________________________________________________________________

class State:
    """ Key is the airplane tag, and the value an array containing the current airport and the current time
    """

    def __init__(self, adict):
        self.adict = adict
        self.profit = 0

    def __eq__(self, other):
        return self.adict.__eq__(other.adict)

    def __hash__(self):
        return hash(self.adict.values())

    def __gt__(self, other):
        if len(self.adict) > len(other.adict):
            return True
        else:
            return False

    def set_key(self, key):
        self.adict.setdefault(key)

    def set_profit(self, profit):
        self.profit = profit

    def set_values(self, key, tup):
        if self.get_values_of_key(key) is None:
            self.adict[key] = tup
        else:
            aux = self.get_values_of_key(key) + tup
            self.adict[key] = aux

    def set_time_last(self, time: str, key):
        self.adict[key]

    def get_profit(self):
        return self.profit

    def get_values(self):
        return list(self.adict.values())

    def get_values_of_key(self, key):
        return self.adict.get(key)

    def get_keys(self):
        return list(self.adict.keys())

    def get_time(self, key):
        return self.adict[key][-1]

    def print(self):
        for x, y in self.adict.items():
            t = x.get_code()
            print(t, y)

    def contains_airport(self, key, airport):
        for y in self.adict.get(key):
            if y is None:
                break
            if y[-2] in airport:
                return True
        return False

    def get_trips_dict(self):
        t = dict()
        tup = defaultdict(list)
        a = dict()
        keys = self.adict.keys()

        for x, y in self.adict.items():
            a.setdefault(x, y)
            t.setdefault(x)
        for p in keys:
            if self.adict.get(p) is not None and len(self.adict.get(p)) > 2:
                t[p] = list(a.get(p))[::2]
                for i in range(len(t.get(p)) - 1):
                    if t[p][i] != t[p][i + 1]:
                        tup[p].append((t[p][i], t[p][i + 1]))
        return tup

    def get_trips(self, tup):
        trips = []

        for i in tup.keys():
            if tup[i] is not None:
                for n in range(len(tup[i])):
                    trips.append(tup[i][n])
        return trips




# ______________________________________________________________________________


def time_sum(a, b):
    dt1 = datetime.strptime(a, '%H%M')
    dt2 = datetime.strptime(b, '%H%M')
    dt2_delta = timedelta(hours=dt2.hour, minutes=dt2.minute)
    dt3 = dt1 + dt2_delta
    str_t3 = datetime.strftime(dt3, '%H%M')
    return str_t3


def time_difference(a, b):
    dt1 = datetime.strptime(a, '%H%M')
    dt2 = datetime.strptime(b, '%H%M')
    dt2_delta = timedelta(hours=dt2.hour, minutes=dt2.minute)
    dt3 = dt1 - dt2_delta
    str_t3 = datetime.strftime(dt3, '%H%M')
    return str_t3


# ____________________

def main():
    timer = time.time()
    state1 = State({})
    asar = ASARProblem(state1)
    asar.load('examples/simple8.txt', state1)

    final = astar_search(asar)
    if final is None:
        print('Infeasible')
        asar.save('solutions/simp1.txt', None)
    else:
        final.path()[-1].state.set_profit(asar.get_max_profit() - asar.profit)
        asar.save('solutions/simp1.txt', final.path()[-1].state)

    print("--- %s seconds ---" % (time.time() - timer))


if __name__ == '__main__':
    main()
