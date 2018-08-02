#!/usr/bin/env python3

from .encodings.strips import State
from .encodings.strips import Action
from .encodings.strips import Domain
from .encodings.strips import depth_first_search
from .encodings.strips import breadth_first_search


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


problem = BlocksWorld(init=[On('R', 'B'),
                            On('B', 'G'),
                            OnTable('G'),
                            OnTable('A'),
                            Clear('R'),
                            Clear('A'),
                            ],
                      goal=[On('G', 'B'), On('B', 'R'), OnTable('R')])
from pprint import pprint
pprint(problem.ground_states)
pprint(problem.ground_actions)
pprint(problem.init)
pprint(problem.goal)


print("---- search ----")
result = breadth_first_search(problem)
#result = depth_first_search(problem)
if result is None:
    print("Not found")
else:
    print(problem.init)
    for a, s in result:
        print('    |')
        print('    V')
        print(a)
        print('    |')
        print('    V')
        print(s)
