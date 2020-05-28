from os.path import exists
from traceback import print_exc
# import direct.particles.ParticleManagerGlobal  # for deploy-ng
from yorg.yorg import Yorg


if __name__ == '__main__' or exists('main.pyo'):
    yorg = Yorg()
    try: yorg.run()
    except Exception as exc:
        print_exc()
        yorg.kill()
