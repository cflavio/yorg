from os.path import exists
from traceback import print_exc
from yorg.yorg import Yorg
import direct.particles.ParticleManagerGlobal  # for deploy-ng


if __name__ == '__main__' or exists('main.pyo'):
    yorg = Yorg()
    try: yorg.run()
    except Exception as e:
        print_exc()
        yorg.kill()
