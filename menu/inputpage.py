from string import ascii_lowercase
from itertools import product
from panda3d.core import TextNode
from yyagl.lib.gui import Btn, Label
from yyagl.engine.gui.page import Page
from yyagl.engine.gui.menu import NavInfo, NavInfoPerPlayer
from yyagl.dictfile import DctFile
from .thankspage import ThanksPageGui
from .already_dlg import AlreadyUsedDlg, AlreadyUsedJoystickDlg


class AbsInputPageGui(ThanksPageGui):

    joyp_idx = None

    def __init__(self, mediator, menu_props, opt_file, keys):
        self.keys = keys
        self.opt_file = opt_file
        self.ibuttons = []
        ThanksPageGui.__init__(self, mediator, menu_props)

    def build(self):  # parameters differ from overridden
        menu_props = self.menu_props
        suff = str(self.joyp_idx + 1)
        player_lab = Label(
            text=_('Player') + ' ' + suff, pos=(0, .9),
            tra_src='Player' + ' ' + suff,
            tra_tra=_('Player') + ' ' + suff,
            **menu_props.label_args)
        widgets = self.create_buttons()
        l_a = menu_props.label_args.copy()
        l_a['scale'] = .065
        l_a['text_fg'] = menu_props.text_err_col
        self.hint_lab = Label(
            text=_('Press the key to record it'), pos=(0, .74), **l_a)
        self.hint_lab.hide()
        widgets += [player_lab, self.hint_lab]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def create_buttons(self): return []

    def start_rec(self): pass

    def update_values(self): return {}

    def _add_lab(self, text, pos_z):
        return Label(
            text=text, pos=(-.1, pos_z), text_align=TextNode.ARight,
            **self.menu_props.label_args)

    def _add_btn(self, text, pos_z):
        btn = Btn(pos=(.46, pos_z), text=text, cmd=self.start_rec,
                  **self.menu_props.btn_args)
        btn['extraArgs'] = [btn]
        self.ibuttons += [btn]
        return btn

    def _on_back(self, player=0):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page' + suff, [dct])

    def make_player_btn(self, tra_src, tra_tra):
        pbtn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player,
            tra_src=tra_src, tra_tra=tra_tra,
            **self.menu_props.btn_args)
        self.add_widgets([pbtn])

    def on_player(self, code):
        dct = self.update_values()
        # num = str(self.joyp_idx + 2)
        self.notify('on_push_page', code, [self.keys, dct])


class InputPageGui4Keyboard(AbsInputPageGui):

    joyp_idx = 3

    def create_buttons(self):
        widgets = []
        suff = str(self.joyp_idx + 1)
        buttons_data = [
            (_('Accelerate'), 'forward' + suff, .5),
            (_('Brake/Reverse'), 'rear' + suff, .32),
            (_('Left'), 'left' + suff, .14),
            (_('Right'), 'right' + suff, -.04),
            (_('Weapon'), 'fire' + suff, -.22),
            (_('Respawn'), 'respawn' + suff, -.38)]
        for btn_data in buttons_data:
            widgets += [self._add_lab(btn_data[0], btn_data[2])]
            widgets += [self._add_btn(self.eng.event.key2desc(
                self.keys[btn_data[1]]), btn_data[2])]
        return widgets

    def start_rec(self, btn):  # parameters differ from overridden
        numbers = [str(n) for n in range(10)]
        self._keys = list(ascii_lowercase) + numbers + [
            'backspace', 'insert', 'home', 'page_up', 'num_lock', 'tab',
            'delete', 'end', 'page_down', 'caps_lock', 'enter', 'arrow_left',
            'arrow_up', 'arrow_down', 'arrow_right', 'lshift', 'rshift',
            'lcontrol', 'lalt', 'space', 'ralt', 'rcontrol']
        self.hint_lab.show()
        acc = lambda key: self.mediator.event.accept(key, self.rec, [btn, key])
        list(map(acc, self._keys))

    def on_player(self):  # parameters differ from overridden
        num = str(self.joyp_idx + 2)
        AbsInputPageGui.on_player(self, 'input%skeyboard' % num)

    def rec(self, btn, val):
        used = self.already_used(val)
        if used:
            self.dial = AlreadyUsedDlg(self.menu_props, val, *used)
            self.dial.attach(self.on_already_dlg)
        else:
            btn['text'] = val
            dct = self.update_values()
            self.opt_file['settings'] = DctFile.deepupdate(
                self.opt_file['settings'], dct)
            self.opt_file.store()

            keys = self.opt_file['settings']['keys']
            nav1 = NavInfoPerPlayer(
                keys['left1'], keys['right1'], keys['forward1'], keys['rear1'],
                keys['fire1'])
            nav2 = NavInfoPerPlayer(
                keys['left2'], keys['right2'], keys['forward2'], keys['rear2'],
                keys['fire2'])
            nav3 = NavInfoPerPlayer(
                keys['left3'], keys['right3'], keys['forward3'], keys['rear3'],
                keys['fire3'])
            nav4 = NavInfoPerPlayer(
                keys['left4'], keys['right4'], keys['forward4'], keys['rear4'],
                keys['fire4'])
            nav = NavInfo([nav1, nav2, nav3, nav4])
            self.menu_props.nav = nav

        self.hint_lab.hide()
        events = list(self.keys.values()) + self._keys
        list(map(self.mediator.event.ignore, events))
        self.enable_navigation([0])

    def on_already_dlg(self): self.dial = self.dial.destroy()

    def already_used(self, val):
        if self.eng.event.key2desc(self.keys['pause']) == val:
            return '1', 'pause'
        labels = ['forward', 'rear', 'left', 'right', 'fire', 'respawn',
                  'pause']
        for lab, player in product(labels[:-1], ['1', '2', '3', '4']):
            if self.eng.event.key2desc(self.keys[lab + player]) == val:
                return player, lab

    def update_keys(self): self.keys = self.opt_file['settings']['keys']

    def update_values(self, idx=0):  # parameters differ from overridden
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['keys'] = self.keys
        dct['keys']['forward' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[idx]['text'])
        dct['keys']['rear' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[idx + 1]['text'])
        dct['keys']['left' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[idx + 2]['text'])
        dct['keys']['right' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[idx + 3]['text'])
        dct['keys']['fire' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[idx + 4]['text'])
        dct['keys']['respawn' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[idx + 5]['text'])
        return dct


class InputPageGui1Keyboard(InputPageGui4Keyboard):

    joyp_idx = 0

    def build(self):
        self.make_player_btn('Player',
                             _('Player') + " " + str(self.joyp_idx + 2))
        self.add_widgets([self._add_lab(_('Pause'), -.56)])
        self.add_widgets([self._add_btn(
            self.eng.event.key2desc(self.keys['pause']), -.56)])
        InputPageGui4Keyboard.build(self)

    def update_values(self, idx=0):
        dct = InputPageGui4Keyboard.update_values(self, 1)
        dct['keys']['pause'] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[0]['text'])
        return dct


class InputPageGui2Keyboard(InputPageGui4Keyboard):

    joyp_idx = 1

    def build(self):
        self.make_player_btn('Player',
                             _('Player') + " " + str(self.joyp_idx + 2))
        InputPageGui4Keyboard.build(self)


class InputPageGui3Keyboard(InputPageGui4Keyboard):

    joyp_idx = 2

    def build(self):
        self.make_player_btn('Player',
                             _('Player') + " " + str(self.joyp_idx + 2))
        InputPageGui4Keyboard.build(self)


class InputPage4Keyboard(Page):
    gui_cls = InputPageGui4Keyboard

    def __init__(self, menu_props, opt_file, keys):
        self.menu_props = menu_props
        self.keys = keys
        self.opt_file = opt_file
        Page.__init__(self, menu_props)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.menu_props, self.opt_file,
                                self.keys)

    def destroy(self):
        Page.destroy(self)


class InputPage2Keyboard(InputPage4Keyboard):
    gui_cls = InputPageGui2Keyboard


class InputPage3Keyboard(InputPage4Keyboard):
    gui_cls = InputPageGui3Keyboard


class InputPageKeyboard(InputPage4Keyboard):
    gui_cls = InputPageGui1Keyboard


class InputPageGui4Joystick(AbsInputPageGui):

    joyp_idx = 3

    def create_buttons(self):
        widgets = []
        suff = str(self.joyp_idx + 1)
        buttons_data = [
            (_('Accelerate'), 'forward' + suff, .5),
            (_('Brake/Reverse'), 'rear' + suff, .32),
            (_('Weapon'), 'fire' + suff, .14),
            (_('Respawn'), 'respawn' + suff, -.04)]
        for btn_data in buttons_data:
            widgets += [self._add_lab(btn_data[0], btn_data[2])]
            widgets += [self._add_btn(self.keys[btn_data[1]], btn_data[2])]
        return widgets

    def start_rec(self, btn):  # parameters differ from overridden
        taskMgr.doMethodLater(.01, self.start_rec_aux, 'start rec aux', [btn])

    def start_rec_aux(self, btn):
        self.eng.joystick_mgr.is_recording = True
        keys = [
            'face_x', 'face_y', 'face_a', 'face_b', 'trigger_l', 'trigger_r',
            'shoulder_l', 'shoulder_r', 'stick_l', 'stick_r']
        self._keys = ['joypad%s_%s' % (self.joyp_idx, i) for i in keys]
        self.hint_lab.show()
        acc = lambda key: self.mediator.event.accept(key, self.rec, [btn, key])
        list(map(acc, self._keys))

    def _on_back(self, player=0):
        self.eng.joystick_mgr.is_recording = False
        AbsInputPageGui._on_back(self, player)

    def on_player(self):  # parameters differ from overridden
        AbsInputPageGui.on_player(self,
                                  'input%sjoystick' % (self.joyp_idx + 1))
        self.eng.joystick_mgr.is_recording = False

    def rec(self, btn, val):
        self.eng.joystick_mgr.is_recording = False
        used = self.already_used(val)
        if used:
            self.dial = AlreadyUsedJoystickDlg(self.menu_props, val, used)
            self.dial.attach(self.on_already_joystick_dlg)
        else:
            btn['text'] = val.split('_', 1)[1:][0]
            dct = self.update_values()
            self.opt_file['settings'] = DctFile.deepupdate(
                self.opt_file['settings'], dct)
            self.opt_file.store()
        self.hint_lab.hide()
        list(map(self.mediator.event.ignore, self._keys))
        self.enable_navigation([0])

    def on_already_joystick_dlg(self): self.dial = self.dial.destroy()

    def already_used(self, val):
        val = ''.join(val.split('_', 1)[1:])
        for lab in ['forward', 'rear', 'fire', 'respawn']:
            if self.keys[lab + str(self.joyp_idx + 1)] == val: return lab

    def update_keys(self): self.keys = self.opt_file['settings']['joystick']

    def update_values(self):
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['joystick'] = self.keys
        dct['joystick']['forward' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[0]['text'])
        dct['joystick']['rear' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[1]['text'])
        dct['joystick']['fire' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[2]['text'])
        dct['joystick']['respawn' + suff] = self.eng.event.desc2key(
            self.mediator.gui.ibuttons[3]['text'])
        return dct


class InputPageGui1Joystick(InputPageGui4Joystick):

    joyp_idx = 0

    def build(self):
        self.make_player_btn('Player',
                             _('Player') + " " + str(self.joyp_idx + 2))
        InputPageGui4Joystick.build(self)
        (self.widgets[0].enable
         if self.eng.joystick_mgr.joystick_lib.num_joysticks >= 2
         else self.widgets[0].disable)()


class InputPageGui2Joystick(InputPageGui4Joystick):

    joyp_idx = 1

    def build(self):
        self.make_player_btn('Player',
                             _('Player') + " " + str(self.joyp_idx + 2))
        InputPageGui4Joystick.build(self)
        (self.widgets[0].enable
         if self.eng.joystick_mgr.joystick_lib.num_joysticks >= 3
         else self.widgets[0].disable)()


class InputPageGui3Joystick(InputPageGui4Joystick):

    joyp_idx = 2

    def build(self):
        self.make_player_btn('Player',
                             _('Player') + " " + str(self.joyp_idx + 2))
        InputPageGui4Joystick.build(self)
        (self.widgets[0].enable
         if self.eng.joystick_mgr.joystick_lib.num_joysticks >= 4
         else self.widgets[0].disable)()


class InputPage4Joystick(Page):
    gui_cls = InputPageGui4Joystick

    def __init__(self, menu_props, opt_file, keys):
        self.menu_props = menu_props
        self.keys = keys
        self.opt_file = opt_file
        Page.__init__(self, menu_props)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls,
          [self, self.menu_props, self.opt_file, self.keys])]]

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.menu_props, self.opt_file, self.keys)

    def destroy(self):
        Page.destroy(self)


class InputPage2Joystick(InputPage4Joystick):
    gui_cls = InputPageGui2Joystick


class InputPage3Joystick(InputPage4Joystick):
    gui_cls = InputPageGui3Joystick


class InputPageJoystick(InputPage4Joystick):
    gui_cls = InputPageGui1Joystick
