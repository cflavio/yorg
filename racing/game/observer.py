class Subject(object):

    def __init__(self):
        self.observers = []

    def attach(self, obs, sort=10):
        self.observers += [(obs, sort)]

    def detach(self, obs):
        observers = [_obs for _obs in self.observers if _obs[0] == obs]
        if not observers:
            raise Exception
        map(self.observers.remove, observers)

    def notify(self, meth, *args, **kwargs):
        sorted_observers = sorted(self.observers, key=lambda obs: obs[1])
        map(lambda obs: getattr(obs[0], meth)(*args, **kwargs), sorted_observers)

    def destroy(self):
        self.observers = None


class Observer(object):
    pass
