#!/usr/bin/env python3

from autoplan.strips import State
from autoplan.strips import Action
from autoplan.strips import Domain
from autoplan.strips import depth_first_search
from autoplan.strips import breadth_first_search
from autoplan.strips import enforced_hill_climbing_search
from autoplan.planning_graph import PlanningGraph
from autoplan.planning_graph import RelaxedPlanningGraph

from pprint import pprint
import time


class Object(State):
    variables = ['?o']

class Truck(State):
    variables = ['?t']

class Airplane(State):
    variables = ['?p']

class Vehicle(State):
    variables = ['?v']

class Location(State):
    variables = ['?l']

class Airport(State):
    variables = ['?a']

class City(State):
    variables = ['?c']

class Loc(State):
    variables = ['?l', '?c']

class At(State):
    variables = ['?x', '?l']

class In(State):
    variables = ['?p', '?v']

class Load(Action):
    variables =  ['?o', '?v', '?l']
    preconditions = [Object('?o'), Vehicle('?v'), Location('?l'),
                     At('?v', '?l'), At('?o', '?l')]
    add_effects = [In('?o', '?v')]
    del_effects = [At('?o', '?l')]
    cost = 1

class Unload(Action):
    variables =  ['?o', '?v', '?l']
    preconditions = [Object('?o'), Vehicle('?v'), Location('?l'),
                     At('?v', '?l'), In('?o', '?v')]
    add_effects = [At('?o', '?l')]
    del_effects = [In('?o', '?v')]
    cost = 1

class Drive(Action):
    variables =  ['?t', '?l1', '?l2', '?c']
    preconditions = [Truck('?t'), Location('?l1'), Location('?l2'), City('?c'),
                     At('?t', '?l1'), Loc('?l1', '?c'), Loc('?l2', '?c')]
    add_effects = [At('?t', '?l2')]
    del_effects = [In('?t', '?l1')]
    cost = 1

class Fly(Action):
    variables =  ['?p', '?a1', '?a2']
    preconditions = [Airplane('?p'), Airport('?a1'), Airport('?a2'),
                     At('?p', '?a1')]
    add_effects = [At('?p', '?a2')]
    del_effects = [At('?p', '?a1')]
    cost = 1

class BlocksWorld(Domain):
    objects = ['city1', 'city2', 'city3',
               'truck1', 'truck2', 'truck3',
               'airplane1',
               'office1', 'office2', 'office3',
               'airport1', 'airport2', 'airport3',
               'packet1', 'packet2']
    predicates = [Object, Truck, Airplane, Vehicle, Location, Airport, City, Loc, At, In]
    actions = [Load, Unload, Drive, Fly]

def run():

    init = [
        Object('packet1'), Object('packet2'),
        Vehicle('truck1'), Vehicle('truck2'), Vehicle('truck3'), Vehicle('airplane1'),
        Truck('truck1'), Truck('truck2'), Truck('truck3'), Airplane('airplane1'),
        Location('office1'), Location('office2'), Location('office3'),
        Location('airport1'), Location('airport2'), Location('airport3'),
        Airport('airport1'), Airport('airport2'), Airport('airport3'),
        City('city1'), City('city2'), City('city3'),

        Loc('office1', 'city1'), Loc('airport1', 'city1'), Loc('office2', 'city2'),
        Loc('airport2', 'city2'), Loc('office3', 'city3'), Loc('airport3', 'city3'),
        At('packet1', 'office1'),
        At('packet2', 'office3'),
        At('truck1', 'airport1'),
        At('truck2', 'airport2'),
        At('truck3', 'office3'),
        At('airplane1', 'airport1'),
    ]
    goal = [At('packet1', 'office2'), At('packet2', 'office2')]
    problem = BlocksWorld()
    from pprint import pprint
    pprint(problem.ground_states)
    pprint(problem.ground_actions)
    pprint(init)
    pprint(goal)

    #print("---- Depth First Search ----")
    #start = time.time()
    #result = depth_first_search(problem, init, goal)
    #end = time.time()
    #print('TIME: ', end - start)
    #if result is None:
    #    print("Not found")
    #else:
    #    print(init)
    #    for a, s in result:
    #        print(a.name)

    #print("---- Breadth First Search ----")
    #start = time.time()
    #result = breadth_first_search(problem, init, goal)
    #end = time.time()
    #print('TIME: ', end - start)
    #if result is None:
    #    print("Not found")
    #else:
    #    print(init)
    #    for a, s in result:
    #        print(a.name)


    print('---- Graph Plan ---------------')
    pg = PlanningGraph(problem, init, goal)
    start = time.time()
    solution = pg.solve()
    end = time.time()
    print('TIME: ', end - start)
    if solution is not None:
        for actions in solution:
            print(', '.join(a.name for a in actions))
    else:
        print('FAILED')

    print('---- Relaxed Planning Graph ---------------')
    rpg = RelaxedPlanningGraph(problem, init, goal)
    start = time.time()
    solution = rpg.solve()
    end = time.time()
    print('TIME: ', end - start)
    if solution is not None:
        for a in solution:
            print(a.name)
    else:
        print('FAILED')
    #rpg.visualize()

    print("---- Enforced Hill Climbing Search ----")
    start = time.time()
    result = enforced_hill_climbing_search(problem, init, goal)
    end = time.time()
    print('TIME: ', end - start)
    if result is None:
        print("Not found")
    else:
        print(init)
        for a, s in result:
            print(a.name)

