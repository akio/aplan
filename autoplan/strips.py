#!/usr/bin/env python3

import copy
from typing import List, Dict
from pprint import pprint
import itertools
from .planning_graph import PlanningGraph
from .planning_graph import RelaxedPlanningGraph
import heapq


class State:
    """A state

    Example
    --------

        # Define a state litral with 2 varaible
        class On(State):
            variables = ['?obj1', '?obj2']

        # Create a state instance
        o = On('block-1', 'block-2')

    """
    def __init__(self, *args):
        if len(args) != len(self.variables):
            raise ValueError("Length not match")
        self.args = copy.deepcopy(self.variables)
        self.bind(**dict(zip(self.variables, args)))
        self._identifier = None

    def ground(self):
        return all(not x.startswith('?') for x in self.args)

    def bind(self, **kwargs):
        for i, a in enumerate(self.args):
            if a.startswith('?'):
                if a in kwargs:
                    self.args[i] = kwargs[a]
        if self.ground():
            self._hash = hash(tuple([self.__class__.__name__, *self.args]))

    @property
    def name(self):
        cls = self.__class__.__name__
        return '{}({})'.format(cls, ', '.join(self.args))

    @property
    def safe_name(self):
        cls = self.__class__.__name__
        return '{}_{}'.format(cls, '_'.join(self.args))

    def __hash__(self):
        if self._hash is None:
            raise Exception("Only grounded states support hashing")
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(self.args))


class Action:
    """

    Example
    ---------

        # Define an action template with 3 varaible
        class Move(Action):
            variables =  ['?obj', '?from', '?to']
            preconditions = [On('?obj', '?from'),
                            Clear('?obj'),
                            Clear('?to')]
            add_effects = [On('?obj', '?to'), Clear('?from')]
            del_effects = [On('?obj', '?from'), Clear('?to')]
            cost = 1

        # Create an action instance
        m = Move('block-1', 'block-2', 'block-3')

    """
    def __init__(self, *args):
        self._tuple =  tuple([self.__class__.__name__, *args])
        self._hash = hash(self._tuple)

        self.bindings = dict(zip(self.variables, args))

        preconditions = []
        for state in self.preconditions:
            s = copy.deepcopy(state)
            args = {}
            for var in state.args:
                if var.startswith('?'):
                    if var in self.bindings:
                        args[var] = self.bindings[var]
                    else:
                        raise KeyError("No such variable: {}".format(var))
            s.bind(**args)
            preconditions.append(s)
        self.preconditions = frozenset(preconditions)

        add_effects = []
        for state in self.add_effects:
            s = copy.deepcopy(state)
            args = {}
            for var in state.args:
                if var.startswith('?'):
                    if var in self.bindings:
                        args[var] = self.bindings[var]
                    else:
                        raise KeyError("No such variable: {}".format(var))
            s.bind(**args)
            add_effects.append(s)
        self.add_effects = frozenset(add_effects)

        del_effects = []
        for state in self.del_effects:
            s = copy.deepcopy(state)
            args = {}
            for var in state.args:
                if var.startswith('?'):
                    if var in self.bindings:
                        args[var] = self.bindings[var]
                    else:
                        raise KeyError("No such variable: {}".format(var))
            s.bind(**args)
            del_effects.append(s)
        self.del_effects = frozenset(del_effects)

    @property
    def name(self):
        cls = self.__class__.__name__
        args = [self.bindings[k] for k in self.variables]
        return '{}({})'.format(cls, ', '.join(args))

    @property
    def safe_name(self):
        cls = self.__class__.__name__
        args = [self.bindings[k] for k in self.variables]
        return '{}_{}_'.format(cls, '_'.join(args))

    def __hash__(self):
        return self._hash

    def __repr__(self):
        buf = []
        buf.append('{} {{'.format(self.name))
        buf.append('  Preconditions:')
        for s in self.preconditions:
            buf.append('    {}'.format(s))
        buf.append('  AddEffects:')
        for s in self.add_effects:
            buf.append('    {}'.format(s))
        buf.append('  DelEffects:')
        for s in self.del_effects:
            buf.append('    {}'.format(s))
        buf.append('}')

        return '\n'.join(buf)


class Domain:
    """

    Example
    --------

    """
    def __init__(self):
        states = []
        for pred in self.predicates:
            nparams = len(pred.variables)
            for args in itertools.permutations(self.objects, nparams):
                p = pred(*args)
                states.append(p)
        self.ground_states = frozenset(states)

        actions = []
        for act in self.actions:
            nparams = len(act.variables)
            for args in itertools.permutations(self.objects, nparams):
                a = act(*args)
                actions.append(a)
        self.ground_actions = actions


def depth_first_search(problem, init=[], goal=[]):
    # type: (Domain) -> List[(Action, State)]
    init_set = frozenset(init)
    goal_set = frozenset(goal)

    open_nodes = [init_set]
    closed_nodes = []
    edges = []

    while len(open_nodes) > 0:
        state = open_nodes.pop()
        for a in problem.ground_actions:
            if a.preconditions.issubset(state):
                new_state = (state | a.add_effects) - a.del_effects
                edges.append((state, new_state, a))
                if goal_set.issubset(new_state):
                    s = new_state
                    path = []
                    while s != init_set:
                        for src, dst, act in edges:
                            if dst == s:
                                s = src
                                path.append((act, dst))
                                break
                    return reversed(path)
                if new_state not in closed_nodes:
                    open_nodes.append(new_state)
        closed_nodes.append(state)
    return None


def breadth_first_search(problem, init=[], goal=[]):
    # type: (Domain) -> List[(Action, State)]
    init_set = frozenset(init)
    goal_set = frozenset(goal)

    open_nodes = [init_set]
    closed_nodes = []
    edges = []

    while len(open_nodes) > 0:
        state = open_nodes.pop(0)
        for a in problem.ground_actions:
            if a.preconditions.issubset(state):
                new_state = (state | a.add_effects) - a.del_effects
                edges.append((state, new_state, a))
                if goal_set.issubset(new_state):
                    s = new_state
                    path = []
                    while s != init_set:
                        for src, dst, act in edges:
                            if dst == s:
                                s = src
                                path.append((act, dst))
                                break
                    return reversed(path)
                if new_state not in closed_nodes:
                    open_nodes.append(new_state)
        closed_nodes.append(state)
    return None


def rpg_heuristic(rpg, init, goal):
    rpg.reset(init, goal)
    return len(rpg.solve())

def _search_better_state(problem, rpg, init, goal):
    """Search a state that has a better heuristic value with breadth first search
    """
    h = rpg_heuristic(rpg, init, goal)
    open_nodes = [init]
    edges = []
    closed_nodes = set()
    while open_nodes:
        s = open_nodes.pop(0)
        for a in problem.ground_actions:
            if a.preconditions.issubset(s):
                new_s = (s | a.add_effects) - a.del_effects
                new_h = rpg_heuristic(rpg, new_s, goal)
                edges.append((s, new_s, a, new_h))
                if new_h < h:
                    print('h = ', new_h)
                    path = []
                    x = new_s
                    while x != init:
                        for src, dst, act, heu in edges:
                            if dst == x:
                                x = src
                                path.append((act, dst, heu))
                                break
                    return list(reversed(path))
                if new_s not in closed_nodes:
                    open_nodes.append(new_s)
        closed_nodes.add(s)
    return None


def enforced_hill_climbing_search(problem, rpg, init=[], goal=[]):
    # type: (Domain) -> List[(Action, State)]
    nodes = []
    heapq.heapify(nodes)
    plan = []
    g = frozenset(goal)
    s = frozenset(init)
    h = rpg_heuristic(rpg, s, g)
    print('INITIAL h = ', h)
    while h != 0:
        xs = _search_better_state(problem, rpg, s, g)
        if xs is None:
            return None
        plan.extend(x[:2] for x in xs)
        _, s, h = xs[-1]
    return plan

