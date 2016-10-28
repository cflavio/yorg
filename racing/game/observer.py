class Subject(object):

    def __init__(self):
        self.observers = []

    def attach(self, obs_meth, sort=10):
        self.observers += [(obs_meth, sort)]

    def detach(self, obs):
        observers = [_obs for _obs in self.observers if _obs[0] == obs]
        if not observers:
            raise Exception
        map(self.observers.remove, observers)

    def notify(self, meth, *args, **kwargs):
        meth_observers = [obs for obs in self.observers if obs[0].__name__ == meth]
        sorted_observers = sorted(meth_observers, key=lambda obs: obs[1])
        map(lambda obs: obs[0](*args, **kwargs), sorted_observers)

    def destroy(self):
        self.observers = None


class Observer(object):
    pass
