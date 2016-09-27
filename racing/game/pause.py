'''ynjh_jo's module for pausing and resuming
http://www.panda3d.org/forums/viewtopic.php?t=4439'''


__all__ = []

import sys
import time
importTime = time.clock()
PRmodules = [k for k in sys.modules.keys() if k.find(__name__) > -1]
PRmodulesTime = [sys.modules[m].importTime for m in PRmodules]
PRmodulesTime.sort()
PRmod1stImport = [sys.modules[m] for m in PRmodules
                  if sys.modules[m].importTime == PRmodulesTime[0]][0]
# print PRmodules,PRmodulesTime
if len(PRmodules) > 1:
    for k in PRmodules:
        if importTime == sys.modules[k].importTime:
            sys.modules[k] = PRmod1stImport
            print 'WARNING : PauseResume module was ALREADY IMPORTED,' + \
                '\n          using the 1st imported one.'
            break
else:
    import os
    from direct.task import Task
    directModulesDir = os.path.abspath(
        os.path.join(os.path.dirname(sys.modules[Task.__name__].__file__),
                     os.pardir))

    from pandac.extension_native_helpers import Dtool_funcToMethod
    from pandac.PandaModules import AnimControl, AudioSound, MovieTexture, \
        PandaSystem, AsyncTaskManager
    from direct.interval.IntervalGlobal import ivalMgr
    from direct.showbase.Messenger import Messenger

    atLeast16 = PandaSystem.getMajorVersion() * 10 + \
        PandaSystem.getMinorVersion() >= 16
    taskFunc = lambda t: t.getFunction() if atLeast16 else t.__call__
    taskFuncNameQuery = lambda t: 'getFunction' if atLeast16 else '__call__'
    taskXArgs = lambda t: t.getArgs() if atLeast16 else t.extraArgs
    taskXArgsName = lambda t: 'getArgs' if atLeast16 else 'extraArgs'
    taskWakeT = lambda t: t.getDelay() if atLeast16 else t.wakeTime

    PRmsg = Messenger()
    IDE_ivalsName = 'IDE_IVALS_'
    IDE_tasksName = 'IDE_TASKS_'
    PAUSED_TASKCHAIN_NAME = 'YNJH paused tasks'
    isPaused = 0
    resumeLocked = 0

    # keeps the original C++ functions
    AnimControl__origPlay = AnimControl.play
    AnimControl__origLoop = AnimControl.loop
    AnimControl__origPingpong = AnimControl.pingpong
    AnimControl__origStop = AnimControl.stop
    AudioSound__origPlay = AudioSound.play
    AudioSound__origStop = AudioSound.stop
    MovieTexture__origPlay = MovieTexture.play
    MovieTexture__origStop = MovieTexture.stop


    # defines the new method wrappers for intercepting messages

    # ANIMATIONS ##############################################################
#     def newAnimPlay(self):
#         PRmsg.accept('pauseAllAnims',self,pauseAnim,[self,0])
#         PRmsg.accept('pauseNotTaggedAnims',self,pauseAnim,[self])
#         AnimControl__origPlay(self)
#     Dtool_funcToMethod(newAnimPlay,AnimControl,'play')
#     del newAnimPlay
#
#     def newAnimLoop(self,restart=1,_from=None,_to=None):
#         PRmsg.accept('pauseAllAnims',self,pauseAnim,[self,0])
#         PRmsg.accept('pauseNotTaggedAnims',self,pauseAnim,[self])
#         if _from is not None and _to is not None :
#             AnimControl__origLoop(self,restart,_from,_to)
#         else:
#             AnimControl__origLoop(self,restart)
#     Dtool_funcToMethod(newAnimLoop,AnimControl,'loop')
#     del newAnimLoop
#
#     def newAnimPingpong(self,restart=1,_from=None,_to=None):
#         PRmsg.accept('pauseAllAnims',self,pauseAnim,[self,0])
#         PRmsg.accept('pauseNotTaggedAnims',self,pauseAnim,[self])
#         if _from is not None and _to is not None :
#             AnimControl__origPingpong(self,restart,_from,_to)
#         else:
#             AnimControl__origPingpong(self,restart)
#     Dtool_funcToMethod(newAnimPingpong,AnimControl,'pingpong')
#     del newAnimPingpong
#
#     def newAnimStop(self):
#         for e in PRmsg.getAllAccepting(self):
#             PRmsg.ignore(e,self)
#         AnimControl__origStop(self)
#     Dtool_funcToMethod(newAnimStop,AnimControl,'stop')
#     del newAnimStop
#
#     def pauseAnim(self,respectTag=1):
#         if respectTag:
#             part=self.getPart()
#             for n in xrange(part.getNumNodes()):
#                 if NodePath(part.getNode(n)).hasNetTag('nopause'):
#                     return
#         PRmsg.ignore('pauseAllAnims',self)
#         PRmsg.ignore('pauseNotTaggedAnims',self)
#         PRmsg.accept('resumeAllAnims',self,resumeAnim,[self,
#                                                        self.getPlayRate()])
#         self.setPlayRate(0)
#
#     def resumeAnim(self,PR):
#         PRmsg.ignore('resumeAllAnims',self)
#         PRmsg.accept('pauseAllAnims',self,pauseAnim,[self,0])
#         PRmsg.accept('pauseNotTaggedAnims',self,pauseAnim,[self])
#         self.setPlayRate(PR)


    # AUDIO SOUNDS ############################################################
#     notPausableSounds = []
#     invulnerableSounds = []
#
#     def newAudioPlay(self):
#         PRmsg.accept('pauseAllSounds',self,pauseAudio,[self,0])
#         PRmsg.accept('pausePausableSounds',self,pauseAudio,[self])
#         AudioSound__origPlay(self)
#     newAudioPlay.__doc__=AudioSound__origPlay.__doc__
#     Dtool_funcToMethod(newAudioPlay,AudioSound,'play')
#     del newAudioPlay
#
#     def newAudioStop(self):
#         for e in PRmsg.getAllAccepting(self):
#             PRmsg.ignore(e,self)
#         AudioSound__origStop(self)
#     newAudioStop.__doc__=AudioSound__origStop.__doc__
#     Dtool_funcToMethod(newAudioStop,AudioSound,'stop')
#     del newAudioStop
#
#     def set_pausable(self,status):
#         if self in notPausableSounds:
#             notPausableSounds.remove(self)
#         if not status:
#             notPausableSounds.append(self)
#     Dtool_funcToMethod(set_pausable,AudioSound)
#     del set_pausable
#
#     def setInvulnerable(self,status):
#         if self in invulnerableSounds:
#             if status:
#                 return
#             else:
#                 invulnerableSounds.remove(self)
#         elif status:
#             invulnerableSounds.append(self)
#     Dtool_funcToMethod(setInvulnerable,AudioSound)
#     del setInvulnerable
#
#     def pauseAudio(self,respectTag=1):
#         if self in invulnerableSounds:
#             return
#         if respectTag:
#             if self in notPausableSounds:
#                 return
#         PRmsg.ignore('pauseAllSounds',self)
#         PRmsg.ignore('pausePausableSounds',self)
#         PRmsg.accept('resumeAllSounds',self,resumeAudio,[self])
#         AudioSound__origStop(self)
#         self.setTime(self.getTime())
#
#     def resumeAudio(self):
#         PRmsg.ignore('resumeAllSounds',self)
#         PRmsg.accept('pauseAllSounds',self,pauseAudio,[self,0])
#         PRmsg.accept('pausePausableSounds',self,pauseAudio,[self])
#         AudioSound__origPlay(self)

    # MOVIE TEXTURES ##########################################################
    notPausableMovies = []

    def new_movie_play(self):
        '''Playing of new movies.'''
        PRmsg.accept('pauseAllMovies', self, pause_movie, [self, 0])
        PRmsg.accept('pausePausableMovies', self, pause_movie, [self])
        MovieTexture__origPlay(self)
    new_movie_play.__doc__ = MovieTexture__origPlay.__doc__
    Dtool_funcToMethod(new_movie_play, MovieTexture, 'play')
    del new_movie_play

    def new_movie_stop(self):
        '''Stopping of new movies.'''
        for e in PRmsg.getAllAccepting(self):
            PRmsg.ignore(e, self)
        MovieTexture__origStop(self)
    new_movie_stop.__doc__ = MovieTexture__origStop.__doc__
    Dtool_funcToMethod(new_movie_stop, MovieTexture, 'stop')
    del new_movie_stop

    def set_pausable(self, status):
        '''Sets a movie pausable.'''
        if self in notPausableMovies:
            notPausableMovies.remove(self)
        if not status:
            notPausableMovies.append(self)
    Dtool_funcToMethod(set_pausable, MovieTexture)
    del set_pausable

    def pause_movie(self, respect_tag=1):
        '''Pauses a movie.'''
        if respect_tag:
            if self in notPausableMovies:
                return
        PRmsg.ignore('pauseAllMovies', self)
        PRmsg.ignore('pausePausableMovies', self)
        PRmsg.accept('resumeAllMovies', self, resume_movie, [self])
        MovieTexture__origStop(self)

    def resume_movie(self):
        '''Resumes a movie.'''
        PRmsg.ignore('resumeAllMovies', self)
        PRmsg.accept('pauseAllMovies', self, pause_movie, [self, 0])
        PRmsg.accept('pausePausableMovies', self, pause_movie, [self])
        self.restart()

    # INTERVALS ###############################################################
    def pause_ivals(exclude_name_prefix=''):
        '''Pauses an interval.'''
        global pausedIvals
        pausedIvals = ivalMgr.getIntervalsMatching('*')
        excluded = []
        for i in pausedIvals:
            if ((exclude_name_prefix and
                 i.getName().find(exclude_name_prefix) == 0) or
                 i.getName().find(IDE_ivalsName) == 0):
                excluded.append(i)
            else:
                #~ print 'PAUSED IVAL:',i.getName()
                i.pause()
        for e in excluded:
            pausedIvals.remove(e)

    def resume_ivals():
        '''Resumes an interval.'''
        for i in pausedIvals:
            i.resume()

    # TASKS ###################################################################
    def pause_tasks(excluded_task_name_prefix, no_collision):
        '''Pauses tasks.'''
        global unneededTasks
        if not AsyncTaskManager.getGlobalPtr().findTaskChain(
            PAUSED_TASKCHAIN_NAME):
            taskMgr.setupTaskChain(PAUSED_TASKCHAIN_NAME,
              frameBudget=0)  # frameBudget=0 doesn't allow any task to run
        unneeded_tasks_name = []
        # collects unneeded tasks
        if no_collision:
            unneeded_tasks_name += ['collisionLoop', 'resetPrevTransform']
        unneededTasks = [taskMgr.getTasksNamed(tn)[0]
                         for tn in unneeded_tasks_name]
        # collects all scene's tasks
        for t in taskMgr.getTasks():  # ordinary tasks
            if (t and hasattr(t, taskFuncNameQuery(t)) and
                t.name.find(IDE_tasksName) != 0 and
                 (not excluded_task_name_prefix or
                  (excluded_task_name_prefix and
                   t.name.find(excluded_task_name_prefix)))):
                func = taskFunc(t)
                mod = func.__module__
                # python-based intervals
                if mod.find('direct.interval') == 0:
                    if not (func.im_class.__name__ == 'ActorInterval' and
                           func.im_self.actor.hasNetTag('nopause')):
                        unneededTasks.append(t)
                        t.interval.pause()
                elif mod not in sys.modules or \
                    sys.modules[mod].__file__.find(directModulesDir) < 0:
                    unneededTasks.append(t)
        curr_t = globalClock.getFrameTime()
        for t in taskMgr.getDoLaters():  # doLater tasks
            if (t and hasattr(t, taskFuncNameQuery(t)) and
                 (not excluded_task_name_prefix or
                   (excluded_task_name_prefix and
                    t.name.find(excluded_task_name_prefix)))):
                unneededTasks.append(t)
                # I need to alter the wakeTime during task resume,
                # so I have to save the remaining time.
                # Just save it as its attribute, nobody would notice :D
                t.remainingTime = t.wakeTime - curr_t
        # "pauses" tasks
        for t in unneededTasks:
            t.ORIG_extraArgs = taskXArgs(t) if hasattr(t, taskXArgsName(t)) \
                else None
            if hasattr(t, taskFuncNameQuery(t)):
                t.ORIG_call = taskFunc(t)
            t.ORIG_priority = t._priority if hasattr(t, '_priority') \
                else t.getSort()
            # only active tasks can be moved to other chain, so removes doLater
            # tasks since they are in sleeping state
            if hasattr(t, 'remainingTime'):  # doLater tasks
                t.remove()
            else:  # ordinary tasks
                t.lastactivetime = -t.time if hasattr(t, 'time') else 0
                try:
                    t.setTaskChain(PAUSED_TASKCHAIN_NAME)
                except:
                    pass

    def resume_tasks():
        '''Resumes tasks.'''
        # restarts tasks
        for t in unneededTasks:
            if hasattr(t, 'interval'):  # it must be python-based intervals
                t.interval.resume()
                if hasattr(t, 'ORIG_call'):
                    if atLeast16:
                        t.setFunction(t.ORIG_call)
                    else:
                        t.__call__ = t.ORIG_call
            else:
                if hasattr(t, 'remainingTime'):  # doLater tasks
                    temp_delay = t.remainingTime - (globalClock.getRealTime() -
                                                    globalClock.getFrameTime())
                    if hasattr(t, 'uponDeath'):
                        upon_death = t.uponDeath
                    else:
                        upon_death = None
                    # no need to pass appendTask, since if it's already true,
                    # the task is already appended to extraArgs
                    new_task = taskMgr.doMethodLater(
                        temp_delay, t.ORIG_call, t.name,
                        priority=t.ORIG_priority, extraArgs=t.ORIG_extraArgs,
                        uponDeath=upon_death)
                    # restore the original delayTime
                    if hasattr(t, 'remainingTime'):
                        new_task.delayTime = t.delayTime
                else:  # ordinary tasks
                    t.setDelay(t.lastactivetime)
                    t.setTaskChain('default')
                    # very important to avoid assertion error on resume
                    t.clearDelay()

    def pause(all_anims=0, all_audios=0, all_movies=0, collision=1,
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
        global isPaused, resumeLocked
        if isPaused:
            print 'WARNING : SCENE IS ALREADY PAUSED !'
            return isPaused
        if all_anims:
            PRmsg.send('pauseAllAnims')
        else:
            PRmsg.send('pauseNotTaggedAnims')
        if all_audios:
            PRmsg.send('pauseAllSounds')
        else:
            PRmsg.send('pausePausableSounds')
        if all_movies:
            PRmsg.send('pauseAllMovies')
        else:
            PRmsg.send('pausePausableMovies')
        pause_ivals(excluded_ival_name_prefix)
        pause_tasks(excluded_task_name_prefix, collision)
        base.disableParticles()
        isPaused = 1
        resumeLocked = lower_level_operation
#        print 'PR:',isPaused
        return isPaused

    def resume(lower_level_operation=1):
        '''Resume.'''
        global isPaused, resumeLocked
        if resumeLocked and not lower_level_operation:
#           print 'WARNING : RESUME IS LOCKED'
            return 2
        if not isPaused:
            print 'WARNING : SCENE IS ALREADY RESUMED'
            return isPaused
        PRmsg.send('resumeAllAnims')  # resume all animations
        PRmsg.send('resumeAllSounds')  # resume all audio
        PRmsg.send('resumeAllMovies')  # resume all movie
        resume_ivals()
        resume_tasks()
        base.enableParticles()
        isPaused = 0
#        print 'PR:',isPaused
        return isPaused

    def get_is_paused():
        '''Is the application paused?'''
        global isPaused
        return isPaused
