from direct.showbase.InputStateGlobal import inputState
from ya2.gameobject import Event
from panda3d.core import AudioSound


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
        self.accept('f11', self.mdt.gui.toggle)


    def evt_OnCollision(self, evt):
        print 'collision with %s %s' % (evt.obj_name, round(globalClock.getFrameTime(), 2))
        if evt.obj_name == 'Wall':
            if self.mdt.audio.crash_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.crash_sfx.play()
        if evt.obj_name == 'Road':
            if self.mdt.audio.landing_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.landing_sfx.play()
        if evt.obj_name == 'Goal':
            if not self.mdt.gui.best_txt.getText() or \
                    float(self.mdt.gui.best_txt.getText()) > \
                    float(self.mdt.gui.time_txt.getText()):
                self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
            self.mdt.logic.last_time_start = globalClock.getFrameTime()
            lap_number = int(self.mdt.gui.lap_txt.getText().split('/')[0])
            self.mdt.gui.lap_txt.setText(str(lap_number + 1)+'/10')
            if self.mdt.audio.lap_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.lap_sfx.play()
            #if lap_number > 3:
            #    game.fsm.demand('Menu')
        #if evt.obj_name == 'Slow':

    def evt_OnFrame(self, evt):
        '''This callback method is invoked on each frame.'''
        input_dct = {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}
        self.mdt.logic.update(input_dct)
        self.mdt.audio.update(input_dct)
        eng.camera.setPos(self.mdt.gfx.nodepath.getPos())
