#!/usr/bin/env python3

import copy
from typing import List, Dict
import itertools
from pprint import pprint


class State:
    """

    Example
    --------


    """
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

    @property
    def name(self):
        cls = self.__class__.__name__
        return '{}({})'.format(cls, ', '.join(self.args))

    @property
    def safe_name(self):
        cls = self.__class__.__name__
        return '{}_{}'.format(cls, '_'.join(self.args))

    def __hash__(self):
        return hash(self.safe_name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(self.args))


class Action:
    """

    Example
    ---------


    """
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
        return hash(self.safe_name)

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
    def __init__(self, init=[], goal=[]):
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
        self.ground_actions = frozenset(actions)

        self.init = frozenset(init)
        self.goal = frozenset(goal)


def depth_first_search(problem):
    # type: (Domain) -> List[(Action, State)]
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
    # type: (Domain) -> List[(Action, State)]
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

def enfoced_hill_climbing_search(problem):
    # type: (Domain) -> List[(Action, State)]
    plan = []
    s = problem.init
    while relaxed_graphplan(s) != 0:
        pass



class Level:
    def __init__(self):
        self.actions= set()
        self.precondition_edges = set()
        self.add_edges = set()
        self.del_edges = set()
        self.states = set()
        self.mutex_states = set()
        self.mutex_actions = set()

class Noop:
    def __init__(self, state):
        self.preconditions = frozenset([state])
        self.add_effects = frozenset([state])
        self.del_effects = frozenset([])
        self.state = state

    @property
    def name(self):
        return ''

    @property
    def safe_name(self):
        return '__NOOP__{}'.format(self.state.safe_name)

    def __hash__(self):
        return hash(self.safe_name)

    def __repr__(self):
        return ''

class PlanningGraph:
    def __init__(self, problem):
        # type: (Domain) -> None
        self._problem = problem
        self._levels = []
        level = Level()
        level.states = problem.init
        self._levels.append(level)

    def solve(self):
        while True:
            if self._possible_goal():
                solution = self._extract_solution()
                if solution:
                    return solution
            if not self._expand_graph():
                return None

    def _possible_goal(self):
        goals = self._problem.goal
        if not goals.issubset(self._levels[-1].states):
            print("not subuset")
            return False
        for g, h in itertools.permutations(goals, 2):
            if set([g, h]) in self._levels[-1].mutex_states:
                print("goal state is mutex")
                return False
        return True

    def _expand_graph(self):
        states = self._levels[-1].states
        cur_level = self._levels[-1]
        new_level = Level()

        # Extend no opts
        for s in states:
            noop = Noop(s)
            new_level.precondition_edges.add((s, noop))
            new_level.add_edges.add((noop, s))
            new_level.states.add(s)
            new_level.actions.add(noop)

        # Extend actions
        for a in self._problem.ground_actions:
            if a.preconditions.issubset(states):
                new_level.actions.add(a)
                for s in a.preconditions:
                    new_level.precondition_edges.add((s, a))
                for e in a.add_effects:
                    new_level.add_edges.add((a, e))
                    new_level.states.add(e)
                for e in a.del_effects:
                    if e in states:
                        new_level.del_edges.add((a, e))

        # If a new layer has the same stetes with previous layer, return False
        if states == new_level.states:
            return False

        # Analyze mutex relations
        for a, b in itertools.permutations(new_level.actions, 2):
            # Incositent effects
            if a.del_effects.intersection(b.add_effects):
                new_level.mutex_actions.add(frozenset([a, b]))
            if b.del_effects.intersection(a.add_effects):
                new_level.mutex_actions.add(frozenset([a, b]))

            # Interference
            if a.del_effects.intersection(b.preconditions):
                new_level.mutex_actions.add(frozenset([a, b]))
            if b.del_effects.intersection(a.preconditions):
                new_level.mutex_actions.add(frozenset([a, b]))

            # Competing needs
            for s, t in itertools.product(a.preconditions, b.preconditions):
                if set([s, t]) in self._levels[-1].mutex_states:
                    new_level.mutex_actions.add(frozenset([a, b]))

        # Check inconsistent support
        for s, t in itertools.permutations(new_level.states, 2):
            actions_for_s = [e[0] for e in new_level.add_edges if s == e[1]]
            actions_for_t = [e[0] for e in new_level.add_edges if t == e[1]]
            for a, b in itertools.product(actions_for_s, actions_for_t):
                if set([a, b]) not in new_level.mutex_actions:
                    break
            else:
                new_level.mutex_states.add(frozenset([s, t]))

        self._levels.append(new_level)
        return True

    def _extract_solution(self):
        """Extract a solution from this planning graph

        Perform backward depth-first search

        """
        goal_set = self._problem.goal
        index = len(self._levels) - 1
        search_stack = []
        action_tree = {}
        action_candidates = []
        for g in goal_set:
            actions = set([e[0] for e in self._levels[index].add_edges
                           if e[1] == g])
            action_candidates.append(actions)
        for action_tuple in itertools.product(*action_candidates):
            for a, b in itertools.combinations(action_tuple, 2):
                if set([a, b]) in self._levels[index].mutex_actions:
                    break
            else:
                key = (index, action_tuple)
                action_tree[key] = None
                search_stack.append(key)
        while True:
            if len(search_stack) == 0:
                # No solution
                return None
            parent_key = search_stack.pop()
            index, parent_actions = parent_key
            goal_set = set()
            for a in parent_actions:
                goal_set.update(a.preconditions)
            action_candidates = []
            for g in goal_set:
                actions = set([e[0] for e in self._levels[index-1].add_edges
                               if e[1] == g])
                action_candidates.append(actions)
            for action_tuple in itertools.product(*action_candidates):
                for a, b in itertools.combinations(action_tuple, 2):
                    if set([a, b]) in self._levels[index-1].mutex_actions:
                        break
                else:
                    if (index - 1) == 1:
                        # Solution found
                        solution = [frozenset([a for a in action_tuple
                                               if not isinstance(a, Noop)])]
                        a = (index, parent_actions)
                        while a is not None:
                            action = frozenset([a for a in a[1]
                                                if not isinstance(a, Noop)])
                            solution.append(action)
                            a = action_tree[a]
                        return solution
                    else:
                        key = (index-1, tuple(action_tuple))
                        action_tree[key] = (index, parent_actions)
                        search_stack.append(key)

    def visualize(self):
        """Visualize planning graph with Graphviz"""
        from graphviz import Digraph

        g = Digraph(format='png')
        g.attr(overlap='false', rankdir='LR', ranksep="2", splines="compound")
        g.attr('node', shape='box')
        for s in self._levels[0].states:
            g.node(s.safe_name + '_L0')
        for i, level in enumerate(self._levels[1:]):
            prev = '_L{}'.format(i)
            this = '_L{}'.format(i+1)
            for a in level.actions:
                g.node(a.safe_name + this, label=a.name)
            noop_nodes = []
            for e in level.precondition_edges:
                g.edge(e[0].safe_name + prev, e[1].safe_name + this,
                        headport='w', tailport='e', arrowhead='none')
            for e in level.add_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + this,
                        headport='w', tailport='e', arrowhead='none')
            for e in level.del_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + this,
                       style='dotted', headport='w', tailport='e', arrowhead='none')
            for name in noop_nodes:
                g.node(name, label='')
            for m in level.mutex_actions:
                m = list(m)
                g.edge(m[0].safe_name + this, m[1].safe_name + this,
                    arrowhead='none', color='red',
                    constraint='false', headport='w', tailport='w')
            for m in level.mutex_states:
                m = list(m)
                g.edge(m[0].safe_name + this, m[1].safe_name + this,
                    arrowhead='none', color='blue',
                    constraint='false', headport='w', tailport='w')
            for s in level.states:
                g.node(s.safe_name + this, label=s.name)
            g.body.append('{rank=same; ' + '; '.join(s.safe_name + this for s in level.states) + ';}')
        g.view()


class RelaxedPlanningGraph:
    def __init__(self, problem):
        # type: (Domain) -> None
        self._problem = problem
        self._levels = []
        level = Level()
        level.states = problem.init
        self._levels.append(level)

    def solve(self):
        while True:
            if self._possible_goal():
                solution = self._extract_solution()
                if solution:
                    return solution
            if not self._expand_graph():
                return None

    def _possible_goal(self):
        goals = self._problem.goal
        if not goals.issubset(self._levels[-1].states):
            print("not subuset")
            return False
        for g, h in itertools.permutations(goals, 2):
            if set([g, h]) in self._levels[-1].mutex_states:
                print("goal state is mutex")
                return False
        return True

    def _expand_graph(self):
        states = self._levels[-1].states
        cur_level = self._levels[-1]
        new_level = Level()

        # Extend no opts
        for s in states:
            noop = Noop(s)
            new_level.precondition_edges.add((s, noop))
            new_level.add_edges.add((noop, s))
            new_level.states.add(s)
            new_level.actions.add(noop)

        # Extend actions
        for a in self._problem.ground_actions:
            if a.preconditions.issubset(states):
                new_level.actions.add(a)
                for s in a.preconditions:
                    new_level.precondition_edges.add((s, a))
                for e in a.add_effects:
                    new_level.add_edges.add((a, e))
                    new_level.states.add(e)

        # If a new layer has the same stetes with previous layer, return False
        if states == new_level.states:
            return False

        self._levels.append(new_level)
        return True

    def _extract_solution2(self):
        g = self._problem.goal
        m = len(self._levels)
        G = []*m
        mark_table = {}
        for i in range(1, m):
            G[i] =

        for i in range(len(self._levels) - 1, 0, -1):
            for g in x:
                for f in o.preconditions:

                for f in o.add_effects:
                    mark_table[(i, f)] = True
                    mark_table[(i - 1, f)] = True


    def _extract_solution(self):
        """Extract a solution from this planning graph

        Perform backward depth-first search

        """
        goal_set = self._problem.goal
        index = len(self._levels) - 1
        search_stack = []
        action_tree = {}
        action_candidates = []
        for g in goal_set:
            actions = set([e[0] for e in self._levels[index].add_edges
                           if e[1] == g])
            action_candidates.append(actions)
        for action_tuple in itertools.product(*action_candidates):
            for a, b in itertools.combinations(action_tuple, 2):
                if set([a, b]) in self._levels[index].mutex_actions:
                    break
            else:
                key = (index, action_tuple)
                action_tree[key] = None
                search_stack.append(key)
        while True:
            if len(search_stack) == 0:
                # No solution
                return None
            parent_key = search_stack.pop()
            index, parent_actions = parent_key
            goal_set = set()
            for a in parent_actions:
                goal_set.update(a.preconditions)
            action_candidates = []
            for g in goal_set:
                actions = set([e[0] for e in self._levels[index-1].add_edges
                               if e[1] == g])
                action_candidates.append(actions)
            for action_tuple in itertools.product(*action_candidates):
                for a, b in itertools.combinations(action_tuple, 2):
                    if set([a, b]) in self._levels[index-1].mutex_actions:
                        break
                else:
                    if (index - 1) == 1:
                        # Solution found
                        solution = [frozenset([a for a in action_tuple
                                               if not isinstance(a, Noop)])]
                        a = (index, parent_actions)
                        while a is not None:
                            action = frozenset([a for a in a[1]
                                                if not isinstance(a, Noop)])
                            solution.append(action)
                            a = action_tree[a]
                        return solution
                    else:
                        key = (index-1, tuple(action_tuple))
                        action_tree[key] = (index, parent_actions)
                        search_stack.append(key)

    def visualize(self):
        """Visualize planning graph with Graphviz"""
        from graphviz import Digraph

        g = Digraph(format='png')
        g.attr(overlap='false', rankdir='LR', ranksep="2", splines="compound")
        g.attr('node', shape='box')
        for s in self._levels[0].states:
            g.node(s.safe_name + '_L0')
        for i, level in enumerate(self._levels[1:]):
            prev = '_L{}'.format(i)
            this = '_L{}'.format(i+1)
            for a in level.actions:
                g.node(a.safe_name + this, label=a.name)
            noop_nodes = []
            for e in level.precondition_edges:
                g.edge(e[0].safe_name + prev, e[1].safe_name + this,
                        headport='w', tailport='e', arrowhead='none')
            for e in level.add_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + this,
                        headport='w', tailport='e', arrowhead='none')
            for name in noop_nodes:
                g.node(name, label='')
            for m in level.mutex_actions:
                m = list(m)
                g.edge(m[0].safe_name + this, m[1].safe_name + this,
                    arrowhead='none', color='red',
                    constraint='false', headport='w', tailport='w')
            for m in level.mutex_states:
                m = list(m)
                g.edge(m[0].safe_name + this, m[1].safe_name + this,
                    arrowhead='none', color='blue',
                    constraint='false', headport='w', tailport='w')
            for s in level.states:
                g.node(s.safe_name + this, label=s.name)
            g.body.append('{rank=same; ' + '; '.join(s.safe_name + this for s in level.states) + ';}')
        g.view()


