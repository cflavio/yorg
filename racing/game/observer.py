'''This module provides classes for the Observer pattern.'''


class Subject(object):
    '''This class models the subject.'''

    def __init__(self):
        self.observers = []

    def attach(self, observer):
        '''Attaches an observer.'''
        self.observers += [observer]
        self.observers = list(set(self.observers))

    def detach(self, observer):
        '''Detaches an observer.'''
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self, message='', argument=None):
        '''Notifies the observers.'''
        for obs in self.observers:
            if message:
                obs.update(self, message, argument)
            else:
                obs.update(self)


class Observer(object):
    '''This class models the observer.'''

    def update(self, subject, message='', argument=None):
        '''Pseudoabstract update method.'''
        pass
