from direct.showbase.InputStateGlobal import inputState
from ya2.gameobject import Event


class _Event(Event):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        label_events = [('forward', 'arrow_up'),
                        ('left', 'arrow_left'),
                        ('reverse', 'z'),
                        ('right', 'arrow_right')]
        map(lambda (lab, evt): inputState.watchWithModifiers(lab, evt),
            label_events)
        self.accept('bullet-contact-added', self.on_collision)
        self.accept('f11', self.mdt.gui.toggle)
        self.__last_wall_time = None
        self.__last_goal_time = None
        self.__last_slow_time = None

    def on_collision(self, node1, node2):
        if node2.getName() == 'Wall':
            self.__last_wall_time = globalClock.getFrameTime()
        if node2.getName() == 'Goal':
            self.__last_goal_time = globalClock.getFrameTime()
        if node2.getName() == 'Slow':
            self.__last_slow_time = globalClock.getFrameTime()

    def evt_OnFrame(self, evt):
        '''This callback method is invoked on each frame.'''
        input_dct = {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}
        self.mdt.logic.update(input_dct)
        self.mdt.audio.update(input_dct)
        if self.__last_wall_time and \
                globalClock.getFrameTime() - self.__last_wall_time > .05:
            self.__last_wall_time = None
            print 'wall'
        if self.__last_goal_time and \
                globalClock.getFrameTime() - self.__last_goal_time > .05:
            self.__last_goal_time = None
            if not self.mdt.gui.best_txt.getText() or \
                    float(self.mdt.gui.best_txt.getText()) > \
                    float(self.mdt.gui.time_txt.getText()):
                self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
            self.mdt.logic.last_time_start = globalClock.getFrameTime()
            lap_number = int(self.mdt.gui.lap_txt.getText().split('/')[0])
            self.mdt.gui.lap_txt.setText(str(lap_number + 1)+'/10')
            #if lap_number > 3:
            #    game.fsm.demand('Menu')
            print 'goal'
        if self.__last_slow_time and \
                globalClock.getFrameTime() - self.__last_slow_time > .05:
            self.__last_slow_time = None
            print 'slow'
        eng.camera.setPos(self.mdt.gfx.nodepath.getPos())
