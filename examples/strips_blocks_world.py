#!/usr/bin/env python3

from autoplan.strips import State
from autoplan.strips import Action
from autoplan.strips import Domain
from autoplan.strips import depth_first_search
from autoplan.strips import breadth_first_search
from autoplan.strips import enforced_hill_climbing_search
from autoplan.planning_graph import PlanningGraph
from autoplan.planning_graph import RelaxedPlanningGraph


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
    problem = BlocksWorld()
    init=[On('R', 'B'), On('B', 'G'), OnTable('G'), OnTable('A'), Clear('R'), Clear('A'), ]
    goal=[On('G', 'B'), On('B', 'R'), OnTable('R')]

    from pprint import pprint
    pprint(problem.ground_states)
    pprint(problem.ground_actions)
    pprint(init)
    pprint(goal)


    print("---- search ----")
    result = breadth_first_search(problem, init, goal)
    #result = depth_first_search(problem)
    if result is None:
        print("Not found")
    else:
        print(init)
        for a, s in result:
            print('    |')
            print('    V')
            print(a)
            print('    |')
            print('    V')
            print(s)


    print('---- PlanningGraph ---------------')
    pg = PlanningGraph(problem, init, goal)
    solution = pg.solve()
    if solution is not None:
        for actions in solution:
            print(', '.join(a.name for a in actions))
    else:
        print('FAILED')

    print('---- RelaxedPlanningGraph ---------------')
    rpg = RelaxedPlanningGraph(problem, init, goal)
    solution = rpg.solve()
    if solution is not None:
        for a in solution:
            print(a.name)
    else:
        print('FAILED')


    print("---- enforced hill climbing search ----")
    result = enforced_hill_climbing_search(problem, init, goal)
    if result is None:
        print("Not found")
    else:
        print(init)
        for a, s in result:
            print('    |')
            print('    V')
            print(a.name)
            print('    |')
            print('    V')
            print(list(s))
