#!/usr/bin/env python3

import copy
from typing import List, Dict
import itertools
from pprint import pprint


class State:
    def __init__(self, *args):
        if len(args) != len(self.variables):
            raise ValueError("Length not match")
        self.args = copy.deepcopy(self.variables)
        self.bind(**dict(zip(self.variables, args)))

    def ground(self):
        pass

    def bind(self, **kwargs):
        for i, a in enumerate(self.args):
            if a.startswith('?'):
                if a in kwargs:
                    self.args[i] = kwargs[a]

    def __hash__(self):
        return hash(tuple([self.__class__.__name__, *self.args]))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(self.args))

class Action:
    def __init__(self, *args):
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

    def name(self):
        cls = self.__class__.__name__
        args = [self.bindings[k] for k in self.variables]
        return '{}({})'.format(cls, ', '.join(args))

    def __repr__(self):
        buf = []
        buf.append('{} {{'.format(self.name()))
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
    def __init__(self, init=[], goal=[]):
        states = []
        for pred in self.predicates:
            nparams = len(pred.variables)
            for args in itertools.permutations(self.objects, nparams):
                p = pred(*args)
                states.append(p)
        self.ground_states = states

        actions = []
        for act in self.actions:
            nparams = len(act.variables)
            for args in itertools.permutations(self.objects, nparams):
                a = act(*args)
                actions.append(a)
        self.ground_actions = actions

        self.init = init
        self.goal = goal

def depth_first_search(problem):
    init_set = frozenset(problem.init)
    goal_set = frozenset(problem.goal)

    print("INIT_SET: {}".format(init_set))
    print("GOAL_SET: {}".format(goal_set))

    open_nodes = [init_set]
    closed_nodes = []
    edges = []

    while len(open_nodes) > 0:
        state = open_nodes.pop()
        print("CURRENT: {}".format(state))
        for a in problem.ground_actions:
            if a.preconditions.issubset(state):
                new_state = (state | a.add_effects) - a.del_effects
                edges.append((state, new_state, a))
                if goal_set.issubset(new_state):
                    print("Solution found")
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


def breadth_first_search(problem):
    init_set = frozenset(problem.init)
    goal_set = frozenset(problem.goal)

    print("INIT_SET: {}".format(init_set))
    print("GOAL_SET: {}".format(goal_set))

    open_nodes = [init_set]
    closed_nodes = []
    edges = []

    while len(open_nodes) > 0:
        state = open_nodes.pop(0)
        print("CURRENT: {}".format(state))
        for a in problem.ground_actions:
            if a.preconditions.issubset(state):
                new_state = (state | a.add_effects) - a.del_effects
                edges.append((state, new_state, a))
                if goal_set.issubset(new_state):
                    print("Solution found")
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

class PlanningGraph:
    def __init__(self, problem):
        pass


