'''This module provides classes for the Observer pattern.'''


class Subject(object):
    '''This class models the subject.'''

    def __init__(self):
        self.observers = []

    def attach(self, obs, meth, sort=100):
        '''Attaches an observer.'''
        self.observers += [(obs, meth, sort)]

    def detach(self, observer):
        '''Detaches an observer.'''
        for obs in [obs for obs in self.observers if obs[0] == observer]:
            self.observers.remove(obs)

    def notify(self, *args):
        '''Notifies the observers.'''
        sorted_observers = sorted(self.observers, key=lambda obs: obs[2])
        map(lambda obs: obs[1](*args), sorted_observers)


class Observer(object):
    '''This class models the observer.'''
    pass
