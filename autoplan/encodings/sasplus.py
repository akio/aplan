#!/usr/bin/env python3


class State:
    pass

class Action:
    pass


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
