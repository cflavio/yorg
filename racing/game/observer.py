'''This module provides classes for the Observer pattern.'''


class Subject(object):
    '''This class models the subject.'''

    def __init__(self):
        self.observers = []

    def attach(self, obs_meth, sort=10):
        '''Attaches an observer.'''
        self.observers += [(obs_meth, sort)]

    def detach(self, obs_meth):
        '''Detaches an observer.'''
        for obs in [obs for obs in self.observers if obs[0] == obs_meth]:
            self.observers.remove(obs)

    def notify(self, *args):
        '''Notifies the observers.'''
        sorted_observers = sorted(self.observers, key=lambda obs: obs[1])
        map(lambda obs: obs[0](*args), sorted_observers)

    def destroy(self):
        '''Destroys subject's stuff.'''
        self.observers = None


class Observer(object):
    '''This class models the observer.'''
    pass
