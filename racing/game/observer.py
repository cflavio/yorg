class Subject(object):

    def __init__(self):
        self.observers = []

    def attach(self, obs_meth, sort=10):
        self.observers += [(obs_meth, sort)]

    def detach(self, obs_meth):
        observers = [obs for obs in self.observers if obs[0] == obs_meth]
        if not observers:
            raise Exception
        map(self.observers.remove, observers)

    def notify(self, *args):
        sorted_observers = sorted(self.observers, key=lambda obs: obs[1])
        map(lambda obs: obs[0](*args), sorted_observers)

    def destroy(self):
        self.observers = None


class Observer(object):
    pass
