from string import ascii_lowercase
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectLabel import DirectLabel
from yyagl.library.gui import Btn, PandaCheckBtn, Label
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.engine.joystick import JoystickMgr
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class InputPageGui2(ThanksPageGui):

    joyp_idx = 1

    def __init__(self, mediator, menu_args, joysticks, keys):
        self.joypad_cb = None
        self.joysticks = joysticks
        self.keys = keys
        self.ibuttons = []
        ThanksPageGui.__init__(self, mediator, menu_args)

    def build(self):
        menu_args = self.menu_args
        widgets = []

        suff = str(self.joyp_idx + 1)
        player_lab = Label(
            text=_('Player') + ' ' + suff, pos=(-.2, 1, .9),
            tra_src='Player' + ' ' + suff,
            tra_tra=_('Player') + ' ' + suff,
            **menu_args.label_args)
        joypad_lab = Label(
            text=_('Use the joypad when present'), pos=(-.3, 1, .7),
            text_align=TextNode.ARight,
            tra_src='Use the joypad when present',
            tra_tra=_('Use the joypad when present'),
            **menu_args.label_args)
        self.joypad_cb = PandaCheckBtn(
            pos=(-.11, 1, .72), text='',
            indicatorValue=self.joysticks[self.joyp_idx],
            indicator_frameColor=menu_args.text_active,
            **menu_args.checkbtn_args)
        if not JoystickMgr.has_support():
            self.joypad_cb['state'] = DISABLED
        buttons_data = [
            (_('Accelerate'), 'forward' + suff, .5),
            (_('Brake/Reverse'), 'rear' + suff, .32),
            (_('Left'), 'left' + suff, .14),
            (_('Right'), 'right' + suff, -.04),
            (_('Weapon'), 'fire' + suff, -.22),
            (_('Respawn'), 'respawn' + suff, -.38)]
        for btn_data in buttons_data:
            widgets += [self._add_lab(btn_data[0], btn_data[2])]
            widgets += [self._add_btn(self.keys[btn_data[1]], btn_data[2])]
        l_a = menu_args.label_args.copy()
        l_a['scale'] = .065
        self.hint_lab = Label(
            text=_('Press the key to record it'), pos=(-.2, 1, -.6), **l_a)
        self.hint_lab.hide()
        widgets += [player_lab, joypad_lab, self.joypad_cb, self.hint_lab]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def _add_lab(self, text, pos_z):
        return Label(
            text=text, pos=(-.3, 1, pos_z), text_align=TextNode.ARight,
            **self.menu_args.label_args)

    def _add_btn(self, text, pos_z):
        btn = Btn(pos=(.26, 1, pos_z), text=text, command=self.start_rec,
                  **self.menu_args.btn_args)
        btn['extraArgs'] = [btn]
        self.ibuttons += [btn]
        return btn

    def start_rec(self, btn):
        numbers = [str(n) for n in range(10)]
        self.keys = list(ascii_lowercase) + numbers + [
            'backspace', 'insert', 'home', 'page_up', 'num_lock', 'tab',
            'delete', 'end', 'page_down', 'caps_lock', 'enter', 'arrow_left',
            'arrow_up', 'arrow_down', 'arrow_right', 'lshift', 'rshift',
            'lcontrol', 'lalt', 'space', 'ralt', 'rcontrol']
        self.hint_lab.show()
        acc = lambda key: self.mediator.event.accept(key, self.rec, [btn, key])
        map(acc, self.keys)

    def _on_back(self):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['keys'] = {
            'forward' + suff: self.mediator.gui.ibuttons[0]['text'],
            'rear' + suff: self.mediator.gui.ibuttons[1]['text'],
            'left' + suff: self.mediator.gui.ibuttons[2]['text'],
            'right' + suff: self.mediator.gui.ibuttons[3]['text'],
            'fire' + suff: self.mediator.gui.ibuttons[4]['text'],
            'respawn' + suff: self.mediator.gui.ibuttons[5]['text']}
        dct['joystick' + suff] = self.mediator.gui.joypad_cb['indicatorValue']
        self.notify('on_back', 'input_page2', [dct])

    def rec(self, btn, val):
        btn['text'] = val
        self.hint_lab.hide()
        map(self.mediator.event.ignore, self.keys)


class InputPageGui1(InputPageGui2):

    joyp_idx = 0

    def build(self):
        p2_btn = Btn(
            text='', pos=(-.2, 1, -.74), command=self.on_player2,
            tra_src='Player 2', tra_tra=_('Player 2'),
            **self.menu_args.btn_args)
        self.add_widgets([p2_btn])
        self.add_widgets([self._add_lab(_('Pause'), -.56)])
        self.add_widgets([self._add_btn(self.keys['pause'], -.56)])
        InputPageGui2.build(self)

    def on_player2(self):
        self.notify('on_push_page', 'input2', [self.joysticks, self.keys])

    def _on_back(self):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['keys'] = {
            'forward' + suff: self.mediator.gui.ibuttons[0]['text'],
            'rear' + suff: self.mediator.gui.ibuttons[1]['text'],
            'left' + suff: self.mediator.gui.ibuttons[2]['text'],
            'right' + suff: self.mediator.gui.ibuttons[3]['text'],
            'fire' + suff: self.mediator.gui.ibuttons[4]['text'],
            'respawn' + suff: self.mediator.gui.ibuttons[5]['text'],
            'pause': self.mediator.gui.ibuttons[6]['text']}
        dct['joystick' + suff] = self.mediator.gui.joypad_cb['indicatorValue']
        self.notify('on_back', 'input_page1', [dct])


class InputPage2(Page):
    gui_cls = InputPageGui2

    def __init__(self, menu_args, joysticks, keys):
        self.menu_args = menu_args
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, joysticks, keys])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)


class InputPage(InputPage2):
    gui_cls = InputPageGui1

