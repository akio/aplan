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


class On(State):
    variables = ['?obj1', '?obj2']

class OnTable(State):
    variables = ['?obj']

class Clear(State):
    variables = ['?obj']

class Move(Action):
    variables =  ['?obj', '?from', '?to']
    preconditions = [On('?obj', '?from'),
                     Clear('?obj'),
                     Clear('?to')]
    add_effects = [On('?obj', '?to'), Clear('?from')]
    del_effects = [On('?obj', '?from'), Clear('?to')]
    cost = 1

class ToTable(Action):
    variables =  ['?obj','?from']
    preconditions = [On('?obj', '?from'), Clear('?obj')]
    add_effects = [OnTable('?obj'), Clear('?from')]
    del_effects = [On('?obj', '?from')]
    cost = 1

class FromTable(Action):
    variables =  ['?obj','?to']
    preconditions = [OnTable('?obj'), Clear('?obj'), Clear('?to')]
    add_effects = [On('?obj', '?to')]
    del_effects = [OnTable('?obj'), Clear('?to')]
    cost = 1

class BlocksWorld(Domain):
    objects = ['R', 'G', 'B', 'A']
    predicates = [On, OnTable, Clear]
    actions = [Move, ToTable, FromTable]

def run():
    init = [On('R', 'B'),
            On('B', 'G'),
            OnTable('G'),
            OnTable('A'),
            Clear('R'),
            Clear('A'),
            ]
    goal = [On('A', 'G'), On('G', 'B'), On('B', 'R'), OnTable('R')]
    problem = BlocksWorld()
    from pprint import pprint
    pprint(problem.ground_states)
    pprint(problem.ground_actions)
    pprint(init)
    pprint(goal)

    print("---- Depth First Search ----")
    start = time.time()
    result = depth_first_search(problem, init, goal)
    end = time.time()
    print('TIME: ', end - start)
    if result is None:
        print("Not found")
    else:
        print(init)
        for a, s in result:
            print(a.name)

    print("---- Breadth First Search ----")
    start = time.time()
    result = breadth_first_search(problem, init, goal)
    end = time.time()
    print('TIME: ', end - start)
    if result is None:
        print("Not found")
    else:
        print(init)
        for i, (a, s) in enumerate(result):
            print(i, a.name)

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

    #print('LEVEL = ', len(rpg._levels))
    #print(rpg._expand_graph())
    #print('LEVEL = ', len(rpg._levels))
    #print(rpg._expand_graph())
    #print('LEVEL = ', len(rpg._levels))

    solution = rpg.solve()
    if solution is not None:
        for i, a in enumerate(solution):
            print(i, a.name)
    else:
        print('FAILED')
    #rpg.visualize()

    print("---- Enforced Hill Climbing Search ----")
    rpg = RelaxedPlanningGraph(problem)
    start = time.time()
    result = enforced_hill_climbing_search(problem, rpg, init, goal)
    end = time.time()
    print('TIME: ', end - start)
    if result is None:
        print("Not found")
    else:
        print(init)
        for i, (a, s) in enumerate(result):
            print(i, a.name)

