'''based on ynjh_jo's module for pausing and resuming
http://www.panda3d.org/forums/viewtopic.php?t=4439'''
import os
import sys
from direct.task import Task
from direct.interval.IntervalGlobal import ivalMgr
from direct.gui.DirectFrame import DirectFrame
from ..gameobject.gameobject import Gui, Logic, GameObjectMdt, Colleague


class PauseGui(Gui):
    '''This class defines the GUI of the pause.'''

    def __init__(self, mdt):
        Gui.__init__(self, mdt)

    def toggle(self):
        '''Toggles the pause.'''
        if not self.mdt.logic.is_paused:
            self.pause_frame = DirectFrame(frameColor=(.3, .3, .3, .7),
                                           frameSize=(-1.8, 1.8, -1, 1))
        else:
            self.pause_frame.destroy()


class PauseLogic(Logic):
    '''This class defines the logic of the pause.'''

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.paused_taskchain = 'ya2 paused tasks'
        taskMgr.setupTaskChain(self.paused_taskchain, frameBudget=0)
        self.is_paused = False
        fpath = os.path.dirname(sys.modules[Task.__name__].__file__)
        self.direct_dir = os.path.abspath(os.path.join(fpath, os.pardir))
        self.paused_ivals = []
        self.paused_tasks = []

    def __process_task(self, tsk):
        '''Processes a task.'''
        func = tsk.getFunction()  # ordinary tasks
        mod = func.__module__
        sys_mod = sys.modules[mod].__file__.find(self.direct_dir) < 0
        is_act = func.im_class.__name__ == 'ActorInterval'
        if mod.find('direct.interval') == 0 and not is_act:
            self.paused_tasks.append(tsk)  # python-based intervals
            tsk.interval.pause()
        elif mod not in sys.modules or sys_mod:
            self.paused_tasks.append(tsk)

    def __pause_tsk(self, tsk):
        '''Pauses a task.'''
        has_args = hasattr(tsk, 'getArgs')
        tsk.stored_extraArgs = tsk.getArgs() if has_args else None
        if hasattr(tsk, 'getFunction'):
            tsk.stored_call = tsk.getFunction()
        has_p = hasattr(tsk, '_priority')
        tsk.stored_priority = tsk._priority if has_p else tsk.getSort()
        # only active tasks can be moved to other chain, so removes doLater
        # tasks since they are in sleeping state
        if hasattr(tsk, 'remainingTime'):  # doLater tasks
            tsk.remove()
        else:  # ordinary tasks
            tsk.lastactivetime = -tsk.time if hasattr(tsk, 'time') else 0
            tsk.setTaskChain(self.paused_taskchain)

    def pause_tasks(self):
        '''Pauses tasks.'''
        self.paused_tasks = []
        is_tsk = lambda tsk: tsk and hasattr(tsk, 'getFunction')
        tasks = [tsk for tsk in taskMgr.getTasks() if is_tsk(tsk)]
        map(lambda tsk: self.__process_task(tsk), tasks)
        for tsk in [tsk for tsk in taskMgr.getDoLaters()if is_tsk(tsk)]:
            self.paused_tasks.append(tsk)
            tsk.remainingTime = tsk.wakeTime - globalClock.getFrameTime()
            # I need to alter the wakeTime during task resume,
            # so I have to save the remaining time.
        map(lambda tsk: self.__pause_tsk(tsk), self.paused_tasks)

    @staticmethod
    def __resume_do_later(tsk):
        '''Resumes a do-later task.'''
        d_t = globalClock.getRealTime() - globalClock.getFrameTime()
        temp_delay = tsk.remainingTime - d_t
        upon_death = tsk.uponDeath if hasattr(tsk, 'uponDeath') else None
        # no need to pass appendTask, since if it's already true,
        # the task is already appended to extraArgs
        new_task = taskMgr.doMethodLater(
            temp_delay, tsk.stored_call, tsk.name, uponDeath=upon_death,
            priority=tsk.stored_priority, extraArgs=tsk.stored_extraArgs)
        if hasattr(tsk, 'remainingTime'):  # restore the original delayTime
            new_task.delayTime = tsk.delayTime

    def __resume_tsk(self, tsk):
        '''Resumes a task.'''
        if hasattr(tsk, 'interval'):  # it must be python-based intervals
            tsk.interval.resume()
            if hasattr(tsk, 'stored_call'):
                tsk.setFunction(tsk.stored_call)
            return
        if hasattr(tsk, 'remainingTime'):
            self.__resume_do_later(tsk)
            return
        tsk.setDelay(tsk.lastactivetime)  # ordinary tasks
        tsk.setTaskChain('default')
        tsk.clearDelay()  # to avoid assertion error on resume

    def pause(self):
        '''Pause.'''
        self.paused_ivals = ivalMgr.getIntervalsMatching('*')
        self.pause_tasks()
        base.disableParticles()
        self.is_paused = True
        return self.is_paused

    def resume(self):
        '''Resume.'''
        map(lambda ival: ival.resume(), self.paused_ivals)
        map(lambda tsk: self.__resume_tsk(tsk), self.paused_tasks)
        base.enableParticles()
        self.is_paused = False
        return self.is_paused

    def toggle(self):
        '''Toggles the pause.'''
        self.mdt.gui.toggle()
        (self.resume if self.is_paused else self.pause)()


class PauseMgr(GameObjectMdt, Colleague):
    '''This class manages the pause.'''
    logic_cls = PauseLogic
    gui_cls = PauseGui

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
