from string import ascii_lowercase
from panda3d.core import TextNode
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageEvent, PageGui
from yyagl.engine.joystick import has_pygame
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class InputEvent(PageEvent):

    def on_back(self):
        dct = {}
        dct['keys'] = {
            'forward': self.mdt.gui.buttons[0]['text'],
            'rear': self.mdt.gui.buttons[1]['text'],
            'left': self.mdt.gui.buttons[2]['text'],
            'right': self.mdt.gui.buttons[3]['text'],
            'button': self.mdt.gui.buttons[4]['text'],
            'respawn': self.mdt.gui.buttons[5]['text']}
        dct['joystick'] = self.mdt.gui._joypad_cb['indicatorValue']
        self.mdt.menu.gui.notify('on_input_back', dct)


class InputPageGui(ThanksPageGui):

    def __init__(self, mdt, menu_args, joystick, keys):
        self._joypad_cb = None
        self.joystick = joystick
        self.keys = keys
        ThanksPageGui.__init__(self, mdt, menu_args)

    def bld_page(self):
        menu_args = self.menu_args
        self.pagewidgets = []
        self.buttons = []

        joypad_lab = DirectLabel(
            text=_('Use the joypad when present'), pos=(-.1, 1, .8),
            text_align=TextNode.ARight, **menu_args.label_args)
        PageGui.transl_text(joypad_lab, 'Use the joypad when present',
                            _('Use the joypad when present'))
        self._joypad_cb = DirectCheckButton(
            pos=(.09, 1, .82), text='',
            indicatorValue=self.joystick,
            indicator_frameColor=menu_args.text_fg,
            **menu_args.checkbtn_args)
        if not has_pygame():
            self._joypad_cb['state'] = DISABLED

        def add_lab(text, pos_z):
            self.pagewidgets += [DirectLabel(
                text=text, pos=(-.1, 1, pos_z), text_align=TextNode.ARight,
                **menu_args.label_args)]

        def add_btn(text, pos_z):
            btn = DirectButton(pos=(.46, 1, pos_z), text=text,
                               command=self.start_rec, **menu_args.btn_args)
            btn['extraArgs'] = [btn]
            self.pagewidgets += [btn]
            self.buttons += [btn]
        buttons_data = [
            (_('Accelerate'), 'forward', .6),
            (_('Brake/Reverse'), 'rear', .4),
            (_('Left'), 'left', .2),
            (_('Right'), 'right', 0),
            (_('Weapon'), 'button', -.2),
            (_('Respawn'), 'respawn', -.4)]
        for btn_data in buttons_data:
            add_lab(btn_data[0], btn_data[2])
            add_btn(self.keys[btn_data[1]], btn_data[2])

        l_a = menu_args.label_args.copy()
        l_a['scale'] = .065
        self.hint_lab = DirectLabel(
            text=_('Press the key to record it'), pos=(0, 1, -.6), **l_a)
        self.hint_lab.hide()
        self.pagewidgets += [joypad_lab, self._joypad_cb, self.hint_lab]
        map(self.add_widget, self.pagewidgets)
        ThanksPageGui.bld_page(self)

    def start_rec(self, btn):
        numbers = [str(n) for n in range(10)]
        self.keys = list(ascii_lowercase) + numbers + [
            'backspace', 'insert', 'home', 'page_up', 'num_lock', 'tab',
            'delete', 'end', 'page_down', 'caps_lock', 'enter', 'arrow_left',
            'arrow_up', 'arrow_down', 'arrow_right', 'lshift', 'rshift',
            'lcontrol', 'lalt', 'space', 'ralt', 'rcontrol']
        self.hint_lab.show()
        acc = lambda key: self.mdt.event.accept(key, self.rec, [btn, key])
        map(acc, self.keys)

    def rec(self, btn, val):
        btn['text'] = val
        self.hint_lab.hide()
        map(self.mdt.event.ignore, self.keys)


class InputPage(Page):
    gui_cls = InputPageGui
    event_cls = InputEvent

    def __init__(self, menu_args, joystick, keys, menu):
        self.menu_args = menu_args
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, joystick, keys])]]
        GameObject.__init__(self, init_lst)
