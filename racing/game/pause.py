'''based on ynjh_jo's module for pausing and resuming
http://www.panda3d.org/forums/viewtopic.php?t=4439'''
import os
import sys
from direct.task import Task
from panda3d.core import AnimControl, AudioSound, MovieTexture, \
    AsyncTaskManager
from direct.interval.IntervalGlobal import ivalMgr
from direct.showbase.Messenger import Messenger


class PauseMgr(object):
    '''This class manages the pause.'''

    def __init__(self):
        self.pr_msg = Messenger()
        self.ide_ivals_name = 'IDE_IVALS_'
        self.ide_tasks_name = 'IDE_TASKS_'
        self.paused_taskchain_name = 'ya2 paused tasks'
        self.is_paused = 0
        self.resume_locked = 0
        fpath = os.path.dirname(sys.modules[Task.__name__].__file__)
        dir_path = os.path.abspath(os.path.join(fpath, os.pardir))
        self.direct_modules_dir = dir_path
        self.not_pausable_movies = []
        self.paused_ivals = []
        self.unneeded_tasks = []

        # keeps the original C++ functions
        self.anim_ctrl_orig_play = AnimControl.play
        self.anim_ctrl_orig_loop = AnimControl.loop
        self.anim_ctrl_orig_pingpong = AnimControl.pingpong
        self.anim_ctrl_orig_stop = AnimControl.stop
        self.audiosound_orig_play = AudioSound.play
        self.audiosound_orig_stop = AudioSound.stop
        self.movietexture_orig_play = MovieTexture.play
        self.movietexture_orig_stop = MovieTexture.stop
        #new_movie_play.__doc__ = self.movietexture_orig_play.__doc__
        #Dtool_funcToMethod(new_movie_play, MovieTexture, 'play')
        #del new_movie_play
        #new_movie_stop.__doc__ = movietexture_orig_stop.__doc__
        #Dtool_funcToMethod(new_movie_stop, MovieTexture, 'stop')
        #del new_movie_stop
        #Dtool_funcToMethod(set_pausable, MovieTexture)
        #del set_pausable

    def new_movie_play(self):
        '''Playing of new movies.'''
        self.pr_msg.accept('pauseAllMovies', self, self.pause_movie, [self, 0])
        m_pause = 'pausePausableMovies'
        self.pr_msg.accept(m_pause, self, self.pause_movie, [self])
        self.movietexture_orig_play(self)

    def new_movie_stop(self):
        '''Stopping of new movies.'''
        for evt in self.pr_msg.getAllAccepting(self):
            self.pr_msg.ignore(evt, self)
        self.movietexture_orig_stop(self)

    def set_pausable(self, status):
        '''Sets a movie pausable.'''
        if self in self.not_pausable_movies:
            self.not_pausable_movies.remove(self)
        if not status:
            self.not_pausable_movies.append(self)

    def pause_movie(self, respect_tag=1):
        '''Pauses a movie.'''
        if respect_tag and self in self.not_pausable_movies:
            return
        self.pr_msg.ignore('pauseAllMovies', self)
        self.pr_msg.ignore('pausePausableMovies', self)
        self.pr_msg.accept('resumeAllMovies', self, self.resume_movie, [self])
        self.movietexture_orig_stop(self)

    def resume_movie(self):
        '''Resumes a movie.'''
        self.pr_msg.ignore('resumeAllMovies', self)
        self.pr_msg.accept('pauseAllMovies', self, self.pause_movie, [self, 0])
        m_pause = 'pausePausableMovies'
        self.pr_msg.accept(m_pause, self, self.pause_movie, [self])
        self.restart()

    def pause_ivals(self, exclude_name_prefix=''):
        '''Pauses an interval.'''
        self.paused_ivals = ivalMgr.getIntervalsMatching('*')
        excluded = []
        for i in self.paused_ivals:
            not_found = i.getName().find(self.ide_ivals_name) == 0
            pref_not_found = i.getName().find(exclude_name_prefix) == 0
            excl_pref = exclude_name_prefix and pref_not_found
            excluded.append(i) if excl_pref or not_found else i.pause()
        map(lambda evt: self.paused_ivals.remove(evt), excluded)

    def resume_ivals(self):
        '''Resumes an interval.'''
        map(lambda ival: ival.resume(), self.paused_ivals)

    def pause_tasks(self, excluded_task_name_prefix, no_collision):
        '''Pauses tasks.'''
        if not AsyncTaskManager.getGlobalPtr().findTaskChain(
                self.paused_taskchain_name):
            taskMgr.setupTaskChain(self.paused_taskchain_name, frameBudget=0)
            # frameBudget=0 doesn't allow any task to run
        unneeded_tasks_name = []
        if no_collision:
            unneeded_tasks_name += ['collisionLoop', 'resetPrevTransform']
        self.unneeded_tasks = [taskMgr.getTasksNamed(tn)[0]
                               for tn in unneeded_tasks_name]
        for tsk in taskMgr.getTasks():  # ordinary tasks
            found_t = tsk.name.find(self.ide_tasks_name) != 0
            fnd_exc = tsk.name.find(excluded_task_name_prefix)
            excl = excluded_task_name_prefix and fnd_exc
            is_excl = not excluded_task_name_prefix or excl
            if tsk and hasattr(tsk, 'getFunction') and found_t and is_excl:
                func = tsk.getFunction()
                mod = func.__module__
                # python-based intervals
                modfile = sys.modules[mod].__file__
                fmd = modfile.find(self.direct_modules_dir) < 0
                if mod.find('direct.interval') == 0:
                    is_int = func.im_class.__name__ == 'ActorInterval'
                    no_pause = func.im_self.actor.hasNetTag('nopause')
                    if not (is_int and no_pause):
                        self.unneeded_tasks.append(tsk)
                        tsk.interval.pause()
                elif mod not in sys.modules or fmd:
                    self.unneeded_tasks.append(tsk)
        curr_t = globalClock.getFrameTime()
        for tsk in taskMgr.getDoLaters():  # doLater tasks
            t_fnd = tsk.name.find(excluded_task_name_prefix)
            exc_f = excluded_task_name_prefix and t_fnd
            is_excl = not excluded_task_name_prefix or exc_f
            if tsk and hasattr(tsk, 'getFunction') and is_excl:
                self.unneeded_tasks.append(tsk)
                # I need to alter the wakeTime during task resume,
                # so I have to save the remaining time.
                # Just save it as its attribute, nobody would notice :D
                tsk.remainingTime = tsk.wakeTime - curr_t
        # "pauses" tasks
        for tsk in self.unneeded_tasks:
            has_args = hasattr(tsk, 'getArgs')
            tsk.ORIG_extraArgs = tsk.getArgs() if has_args else None
            if hasattr(tsk, 'getFunction'):
                tsk.ORIG_call = tsk.getFunction()
            has_p = hasattr(tsk, '_priority')
            tsk.ORIG_priority = tsk._priority if has_p else tsk.getSort()
            # only active tasks can be moved to other chain, so removes doLater
            # tasks since they are in sleeping state
            if hasattr(tsk, 'remainingTime'):  # doLater tasks
                tsk.remove()
            else:  # ordinary tasks
                tsk.lastactivetime = -tsk.time if hasattr(tsk, 'time') else 0
                tsk.setTaskChain(self.paused_taskchain_name)

    def resume_tasks(self):
        '''Resumes tasks.'''
        for tsk in self.unneeded_tasks:
            if hasattr(tsk, 'interval'):  # it must be python-based intervals
                tsk.interval.resume()
                if hasattr(tsk, 'ORIG_call'):
                    tsk.setFunction(tsk.ORIG_call)
            else:
                if hasattr(tsk, 'remainingTime'):  # doLater tasks
                    r_t = globalClock.getRealTime()
                    d_t = r_t - globalClock.getFrameTime()
                    temp_delay = tsk.remainingTime - d_t
                    has_up = hasattr(tsk, 'uponDeath')
                    upon_death = tsk.uponDeath if has_up else None
                    # no need to pass appendTask, since if it's already true,
                    # the task is already appended to extraArgs
                    new_task = taskMgr.doMethodLater(
                        temp_delay, tsk.ORIG_call, tsk.name,
                        priority=tsk.ORIG_priority,
                        extraArgs=tsk.ORIG_extraArgs,
                        uponDeath=upon_death)
                    # restore the original delayTime
                    if hasattr(tsk, 'remainingTime'):
                        new_task.delayTime = tsk.delayTime
                else:  # ordinary tasks
                    tsk.setDelay(tsk.lastactivetime)
                    tsk.setTaskChain('default')
                    # very important to avoid assertion error on resume
                    tsk.clearDelay()

    def pause(self, all_anims=0, all_audios=0, all_movies=0, collision=1,
              excluded_task_name_prefix='', excluded_ival_name_prefix='',
              lower_level_operation=1):
        '''
            allAnims  : pause all animations or only the not "nopause" tagged
                        ones
            allAudios : pause all audio sounds or only the pausable ones
            allMovies : pause all movies or only the pausable ones
            collision : pause collision detection or not
            excludedTaskNamePrefix : do not pause tasks with this name prefix
            excludedIvalNamePrefix : do not pause intervals with this name
                                     prefix
            lowerLevelOperation : <DO NOT use this>
        '''
        if self.is_paused:
            print 'WARNING : SCENE IS ALREADY PAUSED !'
            return self.is_paused
        if all_anims:
            self.pr_msg.send('pauseAllAnims')
        else:
            self.pr_msg.send('pauseNotTaggedAnims')
        if all_audios:
            self.pr_msg.send('pauseAllSounds')
        else:
            self.pr_msg.send('pausePausableSounds')
        if all_movies:
            self.pr_msg.send('pauseAllMovies')
        else:
            self.pr_msg.send('pausePausableMovies')
        self.pause_ivals(excluded_ival_name_prefix)
        self.pause_tasks(excluded_task_name_prefix, collision)
        base.disableParticles()
        self.is_paused = 1
        self.resume_locked = lower_level_operation
        return self.is_paused

    def resume(self, lower_level_operation=1):
        '''Resume.'''
        if self.resume_locked and not lower_level_operation:
            print 'WARNING : RESUME IS LOCKED'
            return 2
        if not self.is_paused:
            print 'WARNING : SCENE IS ALREADY RESUMED'
            return self.is_paused
        self.pr_msg.send('resumeAllAnims')  # resume all animations
        self.pr_msg.send('resumeAllSounds')  # resume all audio
        self.pr_msg.send('resumeAllMovies')  # resume all movie
        self.resume_ivals()
        self.resume_tasks()
        base.enableParticles()
        self.is_paused = 0
        return self.is_paused

    def get_is_paused(self):
        '''Is the application paused?'''
        return self.is_paused
