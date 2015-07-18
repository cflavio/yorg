from direct.showbase.InputStateGlobal import inputState
from ya2.gameobject import Event
from panda3d.core import AudioSound


class _Event(Event):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.has_just_started = True
        self.accept('f11', self.mdt.gui.toggle)
        self.accept('on_frame', self.__on_frame)
        self.accept('on_collision', self.__on_collision)
        label_events = [('forward', 'arrow_up'),
                        ('left', 'arrow_left'),
                        ('reverse', 'z'),
                        ('right', 'arrow_right')]
        map(lambda (lab, evt): inputState.watchWithModifiers(lab, evt),
            label_events)

    def __on_collision(self, obj_name):
        print 'collision with %s %s' % (obj_name, round(globalClock.getFrameTime(), 2))
        if obj_name == 'Wall':
            if self.mdt.audio.crash_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.crash_sfx.play()
        if obj_name == 'Road':
            if self.mdt.audio.landing_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.landing_sfx.play()
        if obj_name == 'Goal':
            lap_number = int(self.mdt.gui.lap_txt.getText().split('/')[0])
            if self.mdt.gui.time_txt.getText():
                lap_time = float(self.mdt.gui.time_txt.getText())
                self.mdt.logic.lap_times += [lap_time]
            if not self.has_just_started and (
                    not self.mdt.gui.best_txt.getText() or
                    float(self.mdt.gui.best_txt.getText()) > lap_time):
                self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
            self.mdt.logic.last_time_start = globalClock.getFrameTime()
            if not self.has_just_started:
                fwd = self.mdt.logic.direction > 0 and self.mdt.phys.speed > 0
                back = self.mdt.logic.direction < 0 and self.mdt.phys.speed < 0
                if fwd or back:
                    self.mdt.gui.lap_txt.setText(str(lap_number + 1)+'/3')
                    if self.mdt.audio.lap_sfx.status() != AudioSound.PLAYING:
                        self.mdt.audio.lap_sfx.play()
                else:
                    self.mdt.gui.lap_txt.setText(str(lap_number - 1)+'/3')
            self.has_just_started = False
            if lap_number >= 3:
                game.track.fsm.demand('Results')
                game.track.gui.show_results()
        #if evt.obj_name == 'Slow':

    def __on_frame(self):
        '''This callback method is invoked on each frame.'''
        input_dct = {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}
        if game.track.fsm.getCurrentOrNextState() != 'Race':
            input_dct = {key: False for key in input_dct}
            self.mdt.gfx.nodepath.set_pos(self.mdt.logic.start_pos)
            self.mdt.gfx.nodepath.set_hpr(self.mdt.logic.start_pos_hpr)
            wheels = self.mdt.phys.vehicle.get_wheels()
            map(lambda whl: whl.set_rotation(0), wheels)
        self.mdt.logic.update(input_dct)
        self.mdt.audio.update(input_dct)
        eng.camera.setPos(self.mdt.gfx.nodepath.getPos())
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)
