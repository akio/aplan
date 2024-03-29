import os
import sys
import math
from typing import List, Dict
import itertools
from pprint import pprint, pformat
from collections import defaultdict
import time

class Level:
    def __init__(self):
        self.actions= set()
        self.precondition_edges = set()
        self.add_edges = set()
        self.del_edges = set()
        self.states = set()
        self.mutex_states = set()
        self.mutex_actions = set()

    def __eq__(self, other):
        if self.states ^ other.states:
            return False
        if self.actions ^ other.actions:
            return False
        if self.precondition_edges ^ other.precondition_edges:
            return False
        if self.add_edges ^ other.add_edges:
            return False
        if self.del_edges ^ other.del_edges:
            return False
        if self.mutex_states ^ other.mutex_states:
            return False
        if self.mutex_actions ^ other.mutex_actions:
            return False
        return True

    def __repr__(self):
        buffer = []
        buffer.append('layer {')
        buffer.append('    states {')
        buffer.append('         \n'.join(x.name for x in self.states))
        buffer.append('    }')
        buffer.append('    actions {')
        buffer.append('         \n'.join(x.name for x in self.actions))
        buffer.append('    }')
        buffer.append('}')
        return '\n'.join(buffer)


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

    def __eq__(self, other):
        return hash(self) == hash(other)


class PlanningGraph:
    def __init__(self, problem, init=[], goal=[]):
        # type: (Domain) -> None
        self._problem = problem
        self._levels = []
        level = Level()
        level.states = frozenset(init)
        self._goals = frozenset(goal)
        self._levels.append(level)

    def solve(self):
        while True:
            if self._possible_goal():
                print("Trying to extract solution...")
                solution = self._extract_solution()
                if solution:
                    return solution
            if not self._expand_graph():
                print("Failed to solve problem")
                return None

    def _possible_goal(self):
        goals = self._goals
        if not goals.issubset(self._levels[-1].states):
            return False
        for g, h in itertools.permutations(goals, 2):
            if set([g, h]) in self._levels[-1].mutex_states:
                print("WARN: {} and {} are mutex states".format(g, h))
                return False
        return True

    def _expand_graph(self):
        now_level = self._levels[-1]
        new_level = Level()

        # Extend no opts
        for s in now_level.states:
            noop = Noop(s)
            now_level.precondition_edges.add((s, noop))
            now_level.add_edges.add((noop, s))
            now_level.actions.add(noop)
            new_level.states.add(s)

        # Extend actions
        for a in self._problem.ground_actions:
            if a.preconditions.issubset(now_level.states):
                now_level.actions.add(a)
                for s in a.preconditions:
                    now_level.precondition_edges.add((s, a))
                for e in a.add_effects:
                    now_level.add_edges.add((a, e))
                    new_level.states.add(e)
                for e in a.del_effects:
                    if e in new_level.states:
                        now_level.del_edges.add((a, e))

        # If a new layer has the same stetes with previous layer, return False
        if now_level == new_level:
            return False

        # Analyze mutex relations
        for a, b in itertools.permutations(now_level.actions, 2):
            # Incositent effects
            if a.del_effects.intersection(b.add_effects):
                now_level.mutex_actions.add(frozenset([a, b]))
            if b.del_effects.intersection(a.add_effects):
                now_level.mutex_actions.add(frozenset([a, b]))

            # Interference
            if a.del_effects.intersection(b.preconditions):
                now_level.mutex_actions.add(frozenset([a, b]))
            if b.del_effects.intersection(a.preconditions):
                now_level.mutex_actions.add(frozenset([a, b]))

            # Competing needs
            for s, t in itertools.product(a.preconditions, b.preconditions):
                if frozenset([s, t]) in self._levels[-1].mutex_states:
                    now_level.mutex_actions.add(frozenset([a, b]))

        # Check inconsistent support
        for s, t in itertools.permutations(new_level.states, 2):
            actions_for_s = [e[0] for e in now_level.add_edges if s == e[1]]
            actions_for_t = [e[0] for e in now_level.add_edges if t == e[1]]
            for a, b in itertools.product(actions_for_s, actions_for_t):
                if frozenset([a, b]) not in now_level.mutex_actions:
                    break
            else:
                new_level.mutex_states.add(frozenset([s, t]))

        self._levels.append(new_level)
        return True

    def _extract_solution(self):
        """Extract a solution from this planning graph

        Perform backward depth-first search

        """
        goal_set = self._goals
        index = len(self._levels) - 1
        if index == 0:
            return []
        search_stack = []
        action_tree = {}
        action_candidates = []
        for g in goal_set:
            actions = set([e[0] for e in self._levels[index - 1].add_edges
                           if e[1] == g])
            action_candidates.append(actions)
        for action_tuple in itertools.product(*action_candidates):
            for a, b in itertools.combinations(action_tuple, 2):
                if set([a, b]) in self._levels[index - 1].mutex_actions:
                    break
            else:
                key = (index - 1, action_tuple)
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
                actions = set([e[0] for e in self._levels[index - 1].add_edges
                               if e[1] == g])
                action_candidates.append(actions)
            for action_tuple in itertools.product(*action_candidates):
                for a, b in itertools.combinations(action_tuple, 2):
                    if set([a, b]) in self._levels[index - 1].mutex_actions:
                        break
                else:
                    if (index - 1) == 0:
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
                        key = (index - 1, tuple(action_tuple))
                        action_tree[key] = (index, parent_actions)
                        search_stack.append(key)

    def visualize(self):
        """Visualize planning graph with Graphviz"""
        from graphviz import Digraph

        g = Digraph(format='png')
        g.attr(overlap='false', rankdir='LR', ranksep="2", splines="compound")
        g.attr('node', shape='box')
        for i, level in enumerate(self._levels[1:]):
            this = '_L{}'.format(i)
            succ = '_L{}'.format(i + 1)
            for a in level.actions:
                g.node(a.safe_name + this, label=a.name)
            noop_nodes = []
            for e in level.precondition_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + this,
                        headport='w', tailport='e', arrowhead='none')
            for e in level.add_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + succ,
                        headport='w', tailport='e', arrowhead='none')
            for e in level.del_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + succ,
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
    def __init__(self, problem, init=[], goal=[]):
        # type: (Domain) -> None
        self._problem = problem
        self._reverse_precondition_map = {}
        for s in self._problem.ground_states:
            self._reverse_precondition_map[s] = set()
            for a in self._problem.ground_actions:
                if s in a.preconditions:
                    self._reverse_precondition_map[s].add(a)

        self.reset(init, goal)

    def solve(self):
        while True:
            if self._possible_goal():
                solution = self._extract_solution_relaxed()
                #solution = self._extract_solution()
                if solution is not None:
                    return solution
            if not self._expand_graph():
                return None

    def reset(self, init=[], goal=[]):
        self._levels = []
        level = Level()
        level.states = frozenset(init)
        self._goals = frozenset(goal)
        self._levels.append(level)
        self._layer_membership = defaultdict(lambda: -1)
        self._action_counters = defaultdict(lambda: 0)
        self._ready_actions = []

        for s in init:
            self._layer_membership[s] = 0
            for a in self._reverse_precondition_map[s]:
                self._action_counters[a] += 1
                if self._action_counters[a] == len(a.preconditions):
                    self._ready_actions.append(a)

    def _possible_goal(self):
        return all(self._layer_membership[x] >= 0 for x in self._goals)

    def _expand_graph(self):
        index = len(self._levels) - 1
        now_level = self._levels[-1]
        new_level = Level()

        # Extend no opts
        for s in now_level.states:
            noop = Noop(s)
            now_level.actions.add(noop)
            now_level.precondition_edges.add((s, noop))
            now_level.add_edges.add((noop, s))
            new_level.states.add(s)

        # Extend actions
        new_ready_actions = []
        for a in self._ready_actions:
            now_level.actions.add(a)
            if self._layer_membership[a] < 0:
                self._layer_membership[a] = index
            for s in a.preconditions:
                now_level.precondition_edges.add((s, a))
            for e in a.add_effects:
                now_level.add_edges.add((a, e))
                new_level.states.add(e)
                if self._layer_membership[e] < 0:
                    self._layer_membership[e] = index + 1
                    for a in self._reverse_precondition_map[e]:
                        self._action_counters[a] += 1
                        if self._action_counters[a] == len(a.preconditions):
                            new_ready_actions.append(a)
        self._ready_actions.extend(new_ready_actions)

        # If a new layer has the same stetes with previous layer, return False
        if now_level == new_level:
            return False

        self._levels.append(new_level)
        return True

    def _expand_graph_1(self):
        """Expand 1 layer"""
        index = len(self._levels) - 1
        now_level = self._levels[-1]
        new_level = Level()

        # Extend no opts
        for s in now_level.states:
            noop = Noop(s)
            now_level.actions.add(noop)
            now_level.precondition_edges.add((s, noop))
            now_level.add_edges.add((noop, s))
            new_level.states.add(s)

        # Extend actions
        ready_actions = [a for a in self._problem.ground_actions
                         if len(a.preconditions) == self._action_counters[a]]
        for a in ready_actions:
            now_level.actions.add(a)
            if self._layer_membership[a] < 0:
                self._layer_membership[a] = index
            for s in a.preconditions:
                now_level.precondition_edges.add((s, a))
            for e in a.add_effects:
                now_level.add_edges.add((a, e))
                new_level.states.add(e)
                if self._layer_membership[e] < 0:
                    self._layer_membership[e] = index + 1
                    for a in self._reverse_precondition_map[e]:
                        self._action_counters[a] += 1

        # If a new layer has the same stetes with previous layer, return False
        if now_level == new_level:
            return False

        self._levels.append(new_level)
        return True

    def _extract_solution_relaxed(self):
        solution = []
        goals = self._goals
        m = len(self._levels)
        G = [None] * (m + 1)
        mark_table = defaultdict(lambda: False)
        for i in range(1, m + 1):
            G[i] = {g for g in goals if self._layer_membership[g] == i}
        for i in range(m, 0, -1):
            for g in [x for x in G[i] if not mark_table[(i, x)]]:
                os = []
                for o in self._levels[i - 1].actions:
                    if g in o.add_effects and self._layer_membership[o] == (i - 1):
                        difficulty = sum(self._layer_membership[p] for p in o.preconditions)
                        os.append((o, difficulty))
                o, _ = min(os, key=lambda x: x[1])
                solution.append(o)
                for f in [f for f in o.preconditions
                          if self._layer_membership[f] != 0 and not mark_table[(i - 1, f)]]:
                    G[self._layer_membership[f]].add(f)
                for f in o.add_effects:
                    mark_table[(i, f)] = True
                    mark_table[(i - 1, f)] = True
        return list(reversed(solution))


    def _extract_solution(self):
        """Extract a solution from this planning graph

        Perform backward depth-first search

        """
        goal_set = self._goals
        index = len(self._levels) - 1
        if index == 0:
            return []
        search_stack = []
        action_tree = {}
        action_candidates = []
        for g in goal_set:
            actions = set([e[0] for e in self._levels[index - 1].add_edges
                           if e[1] == g])
            action_candidates.append(actions)
        for action_tuple in itertools.product(*action_candidates):
            for a, b in itertools.combinations(action_tuple, 2):
                if set([a, b]) in self._levels[index - 1].mutex_actions:
                    break
            else:
                key = (index - 1, action_tuple)
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
                actions = set([e[0] for e in self._levels[index - 1].add_edges
                               if e[1] == g])
                action_candidates.append(actions)
            for action_tuple in itertools.product(*action_candidates):
                for a, b in itertools.combinations(action_tuple, 2):
                    if set([a, b]) in self._levels[index - 1].mutex_actions:
                        break
                else:
                    if (index - 1) == 0:
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
                        key = (index - 1, tuple(action_tuple))
                        action_tree[key] = (index, parent_actions)
                        search_stack.append(key)

    def visualize(self):
        """Visualize planning graph with Graphviz"""
        from graphviz import Digraph

        g = Digraph(format='png')
        g.attr(overlap='false', rankdir='LR', ranksep="2", splines="compound")
        g.attr('node', shape='box')
        for i, level in enumerate(self._levels[1:]):
            this = '_L{}'.format(i)
            succ = '_L{}'.format(i + 1)
            for s in level.states:
                g.node(s.safe_name + this, label=s.name)
            for a in level.actions:
                g.node(a.safe_name + this, label=a.name)
            noop_nodes = []
            for e in level.precondition_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + this,
                        headport='w', tailport='e', arrowhead='none')
            for e in level.add_edges:
                g.edge(e[0].safe_name + this, e[1].safe_name + succ,
                        headport='w', tailport='e', arrowhead='none')
            for name in noop_nodes:
                g.node(name, label='')
            g.body.append('{rank=same; ' + '; '.join(s.safe_name + this for s in level.states) + ';}')
        g.view()
