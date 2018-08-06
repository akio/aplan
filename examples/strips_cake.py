#!/usr/bin/env python3

from autoplan.strips import State
from autoplan.strips import Action
from autoplan.strips import Domain
from autoplan.strips import depth_first_search
from autoplan.strips import breadth_first_search
from autoplan.strips import enfoced_hill_climbing_search
from autoplan.planning_graph import PlanningGraph
from autoplan.planning_graph import RelaxedPlanningGraph

from pprint import pprint

class Have(State):
    variables = ['?obj']

class NotHave(State):
    variables = ['?obj']

class Eaten(State):
    variables = ['?obj']

class NotEaten(State):
    variables = ['?obj']

class Eat(Action):
    variables =  ['?cake']
    preconditions = [Have('?cake')]
    add_effects = [Eaten('?cake'), NotHave('?cake')]
    del_effects = [Have('?cake'), NotEaten('?cake') ]
    cost = 1

class Bake(Action):
    variables =  ['?cake']
    preconditions = [NotHave('?cake')]
    add_effects = [Have('?cake')]
    del_effects = [NotHave('?cake')]
    cost = 1


class CakeWorld(Domain):
    objects = ['cake']
    predicates = [Have, NotHave, Eaten, NotEaten]
    actions = [Eat, Bake]

def run():
    init = [Have('cake'), NotEaten('cake')]
    goal = [Have('cake'), Eaten('cake')]
    problem = CakeWorld()
    pprint(problem.ground_states)
    pprint(problem.ground_actions)
    pprint(init)
    pprint(goal)


    print("---- search ----")
    result = breadth_first_search(problem)
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


    print('-------------------')
    pg = PlanningGraph(problem, init, goal)
    solution = pg.solve()

    #pg.visualize()
    if solution is not None:
        for actions in solution:
            print(', '.join(a.name for a in actions))
    else:
        print('FAILED')

    print('-------------------')
    rpg = RelaxedPlanningGraph(problem, init, goal)
    solution = rpg.solve()
    if solution is not None:
        for actions in solution:
            print(', '.join(a.name for a in actions))
    else:
        print('FAILED')

    print("---- test 1 ----")

    rpg = RelaxedPlanningGraph(problem, [NotHave('cake'), Eaten('cake')],
                               [Have('cake'), Eaten('cake')])
    print('x=', rpg._possible_goal())
    solution = rpg.solve()
    print('h=', len(solution))
    print(solution)
    rpg.visualize()

    print("---- test 2 ----")

    rpg = RelaxedPlanningGraph(problem, [Have('cake'), Eaten('cake')],
                               [Have('cake'), Eaten('cake')])
    print('x=', rpg._possible_goal())
    solution = rpg.solve()
    print('h=', len(solution))
    print(solution)

    print("---- enforced hill climbing search ----")
    result = enfoced_hill_climbing_search(problem, init, goal)
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

