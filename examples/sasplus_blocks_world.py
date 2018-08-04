#!/usr/bin/env python3

from .encodings.sasplus import State
from .encodings.sasplus import Action
from .encodings.sasplus import Domain
from .encodings.sasplus import depth_first_search
from .encodings.sasplus import breadth_first_search

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
