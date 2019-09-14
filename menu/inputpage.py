from string import ascii_lowercase
from itertools import product
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectLabel import DirectLabel
from yyagl.lib.gui import Btn, P3dCheckBtn, Label
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.engine.joystick import JoystickMgr
from yyagl.engine.gui.menu import NavInfo, NavInfoPerPlayer
from yyagl.gameobject import GameObject
from yyagl.dictfile import DctFile
from .thankspage import ThanksPageGui
from .already_dlg import AlreadyUsedDlg, AlreadyUsedJoystickDlg


class InputPageGui4Keyboard(ThanksPageGui):

    joyp_idx = 3

    def __init__(self, mediator, menu_props, opt_file, keys):
        self.keys = keys
        self.opt_file = opt_file
        self.ibuttons = []
        ThanksPageGui.__init__(self, mediator, menu_props)

    def build(self):
        menu_props = self.menu_props
        widgets = []

        suff = str(self.joyp_idx + 1)
        player_lab = Label(
            text=_('Player') + ' ' + suff, pos=(0, .9),
            tra_src='Player' + ' ' + suff,
            tra_tra=_('Player') + ' ' + suff,
            **menu_props.label_args)
        buttons_data = [
            (_('Accelerate'), 'forward' + suff, .5),
            (_('Brake/Reverse'), 'rear' + suff, .32),
            (_('Left'), 'left' + suff, .14),
            (_('Right'), 'right' + suff, -.04),
            (_('Weapon'), 'fire' + suff, -.22),
            (_('Respawn'), 'respawn' + suff, -.38)]
        for btn_data in buttons_data:
            widgets += [self._add_lab(btn_data[0], btn_data[2])]
            widgets += [self._add_btn(self.eng.event.key2desc(self.keys[btn_data[1]]), btn_data[2])]
        l_a = menu_props.label_args.copy()
        l_a['scale'] = .065
        self.hint_lab = Label(
            text=_('Press the key to record it'), pos=(-.2, -.6), **l_a)
        self.hint_lab.hide()
        widgets += [player_lab, self.hint_lab]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

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

    def start_rec(self, btn):
        numbers = [str(n) for n in range(10)]
        self._keys = list(ascii_lowercase) + numbers + [
            'backspace', 'insert', 'home', 'page_up', 'num_lock', 'tab',
            'delete', 'end', 'page_down', 'caps_lock', 'enter', 'arrow_left',
            'arrow_up', 'arrow_down', 'arrow_right', 'lshift', 'rshift',
            'lcontrol', 'lalt', 'space', 'ralt', 'rcontrol']
        self.hint_lab.show()
        acc = lambda key: self.mediator.event.accept(key, self.rec, [btn, key])
        list(map(acc, self._keys))

    def _on_back(self, player=0):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page2', [dct])

    def rec(self, btn, val):
        used = self.already_used(val)
        if used:
            self.dial = AlreadyUsedDlg(self.menu_props, val, *used)
            self.dial.attach(self.on_already_dlg)
        else:
            btn['text'] = val
            dct = self.update_values()
            self.opt_file['settings'] = DctFile.deepupdate(self.opt_file['settings'], dct)
            self.opt_file.store()

            keys = self.opt_file['settings']['keys']
            nav1 = NavInfoPerPlayer(keys['left1'], keys['right1'], keys['forward1'],
                                    keys['rear1'], keys['fire1'])
            nav2 = NavInfoPerPlayer(keys['left2'], keys['right2'], keys['forward2'],
                                    keys['rear2'], keys['fire2'])
            nav3 = NavInfoPerPlayer(keys['left3'], keys['right3'], keys['forward3'],
                                    keys['rear3'], keys['fire3'])
            nav4 = NavInfoPerPlayer(keys['left4'], keys['right4'], keys['forward4'],
                                    keys['rear4'], keys['fire4'])
            nav = NavInfo([nav1, nav2, nav3, nav4])
            self.menu_props.nav = nav

        self.hint_lab.hide()
        events = list(self.keys.values()) + self._keys
        list(map(self.mediator.event.ignore, events))
        self.enable_navigation([0])

    def on_already_dlg(self): self.dial = self.dial.destroy()

    def already_used(self, val):
        if self.eng.event.key2desc(self.keys['pause']) == val: return '1', 'pause'
        labels = ['forward', 'rear', 'left', 'right', 'fire', 'respawn', 'pause']
        for lab, player in product(labels[:-1], ['1', '2', '3', '4']):
            if self.eng.event.key2desc(self.keys[lab + player]) == val: return player, lab

    def update_keys(self): self.keys = self.opt_file['settings']['keys']

    def update_values(self):
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['keys'] = self.keys
        dct['keys']['forward' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[0]['text'])
        dct['keys']['rear' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[1]['text'])
        dct['keys']['left' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[2]['text'])
        dct['keys']['right' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[3]['text'])
        dct['keys']['fire' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[4]['text'])
        dct['keys']['respawn' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[5]['text'])
        return dct


class InputPageGui1Keyboard(InputPageGui4Keyboard):

    joyp_idx = 0

    def build(self):
        p2_btn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player2,
            tra_src='Player 2', tra_tra=_('Player 2'),
            **self.menu_props.btn_args)
        self.add_widgets([p2_btn])
        self.add_widgets([self._add_lab(_('Pause'), -.56)])
        self.add_widgets([self._add_btn(self.eng.event.key2desc(self.keys['pause']), -.56)])
        InputPageGui4Keyboard.build(self)

    def on_player2(self):
        dct = self.update_values()
        self.notify('on_push_page', 'input2keyboard', [self.keys, dct])

    def _on_back(self, player=0):
        dct = self.update_values()
        self.mediator.event.on_back()
        self.notify('on_back', 'input_page1', [dct])

    def update_values(self):
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['keys'] = self.keys
        dct['keys']['forward' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[1]['text'])
        dct['keys']['rear' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[2]['text'])
        dct['keys']['left' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[3]['text'])
        dct['keys']['right' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[4]['text'])
        dct['keys']['fire' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[5]['text'])
        dct['keys']['respawn' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[6]['text'])
        dct['keys']['pause'] = self.eng.event.desc2key(self.mediator.gui.ibuttons[0]['text'])
        return dct


class InputPageGui2Keyboard(InputPageGui4Keyboard):

    joyp_idx = 1

    def build(self):
        p_btn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player3,
            tra_src='Player 3', tra_tra=_('Player 3'),
            **self.menu_props.btn_args)
        self.add_widgets([p_btn])
        InputPageGui4Keyboard.build(self)

    def on_player3(self):
        dct = self.update_values()
        self.notify('on_push_page', 'input3keyboard', [self.keys, dct])

    def _on_back(self, player=0):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page2', [dct])


class InputPageGui3Keyboard(InputPageGui4Keyboard):

    joyp_idx = 2

    def build(self):
        p_btn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player3,
            tra_src='Player 4', tra_tra=_('Player 4'),
            **self.menu_props.btn_args)
        self.add_widgets([p_btn])
        InputPageGui4Keyboard.build(self)

    def on_player3(self):
        dct = self.update_values()
        self.notify('on_push_page', 'input4keyboard', [self.keys, dct])

    def _on_back(self, player=0):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page3', [dct])


class InputPage4Keyboard(Page):
    gui_cls = InputPageGui4Keyboard

    def __init__(self, menu_props, opt_file, keys):
        self.menu_props = menu_props
        self.keys = keys
        self.opt_file = opt_file
        Page.__init__(self, menu_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls,
          [self, self.menu_props, self.opt_file, self.keys])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)


class InputPage2Keyboard(InputPage4Keyboard):
    gui_cls = InputPageGui2Keyboard


class InputPage3Keyboard(InputPage4Keyboard):
    gui_cls = InputPageGui3Keyboard


class InputPageKeyboard(InputPage4Keyboard):
    gui_cls = InputPageGui1Keyboard


class InputPageGui4Joystick(ThanksPageGui):

    joyp_idx = 3

    def __init__(self, mediator, menu_props, opt_file, keys):
        self.keys = keys
        self.opt_file = opt_file
        self.ibuttons = []
        ThanksPageGui.__init__(self, mediator, menu_props)

    def build(self):
        menu_props = self.menu_props
        widgets = []

        suff = str(self.joyp_idx + 1)
        player_lab = Label(
            text=_('Player') + ' ' + suff, pos=(0, .9),
            tra_src='Player' + ' ' + suff,
            tra_tra=_('Player') + ' ' + suff,
            **menu_props.label_args)
        buttons_data = [
            (_('Accelerate'), 'forward' + suff, .5),
            (_('Brake/Reverse'), 'rear' + suff, .32),
            (_('Weapon'), 'fire' + suff, .14),
            (_('Respawn'), 'respawn' + suff, -.04)]
        for btn_data in buttons_data:
            widgets += [self._add_lab(btn_data[0], btn_data[2])]
            widgets += [self._add_btn(self.keys[btn_data[1]], btn_data[2])]
        l_a = menu_props.label_args.copy()
        l_a['scale'] = .065
        self.hint_lab = Label(
            text=_('Press the key to record it'), pos=(-.2, -.6), **l_a)
        self.hint_lab.hide()
        widgets += [player_lab, self.hint_lab]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

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

    def start_rec(self, btn):
        #messenger.toggleVerbose()
        taskMgr.doMethodLater(.01, self.start_rec_aux, 'start rec aux', [btn])

    def start_rec_aux(self, btn):
        self.eng.joystick_mgr.is_recording = True
        self._keys = ['joypad%s_b%s' % (self.joyp_idx, i) for i in range(4)]
        keys = ['trigger_l', 'trigger_r', 'shoulder_l', 'shoulder_r', 'stick_l', 'stick_r']
        self._keys += ['joypad%s_%s' % (self.joyp_idx, i) for i in keys]
        self.hint_lab.show()
        acc = lambda key: self.mediator.event.accept(key, self.rec, [btn, key])
        list(map(acc, self._keys))

    def _on_back(self, player=0):
        self.eng.joystick_mgr.is_recording = False
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page2', [dct])

    def rec(self, btn, val):
        self.eng.joystick_mgr.is_recording = False
        used = self.already_used(val)
        if used:
            self.dial = AlreadyUsedJoystickDlg(self.menu_props, val, used)
            self.dial.attach(self.on_already_joystick_dlg)
        else:
            btn['text'] = val.split('_', 1)[1:]
            dct = self.update_values()
            self.opt_file['settings'] = DctFile.deepupdate(self.opt_file['settings'], dct)
            self.opt_file.store()

            #keys = self.opt_file['settings']['joystick']
            #nav1 = NavInfoPerPlayer(keys['left1'], keys['right1'], keys['forward1'],
            #                        keys['rear1'], keys['fire1'])
            #nav2 = NavInfoPerPlayer(keys['left2'], keys['right2'], keys['forward2'],
            #                        keys['rear2'], keys['fire2'])
            #nav3 = NavInfoPerPlayer(keys['left3'], keys['right3'], keys['forward3'],
            #                        keys['rear3'], keys['fire3'])
            #nav4 = NavInfoPerPlayer(keys['left4'], keys['right4'], keys['forward4'],
            #                        keys['rear4'], keys['fire4'])
            #nav = NavInfo([nav1, nav2, nav3, nav4])
            #self.menu_props.nav = nav

        self.hint_lab.hide()
        list(map(self.mediator.event.ignore, self._keys))
        self.enable_navigation([0])

    def on_already_joystick_dlg(self): self.dial = self.dial.destroy()

    def already_used(self, val):
        val = val.split('_', 1)[1:]
        for lab in ['forward', 'rear', 'fire', 'respawn']:
            if self.keys[lab + str(self.joyp_idx + 1)] == val: return lab

    def update_keys(self): self.keys = self.opt_file['settings']['joystick']

    def update_values(self):
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['joystick'] = self.keys
        dct['joystick']['forward' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[0]['text'])
        dct['joystick']['rear' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[1]['text'])
        dct['joystick']['fire' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[2]['text'])
        dct['joystick']['respawn' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[3]['text'])
        return dct


class InputPageGui1Joystick(InputPageGui4Joystick):

    joyp_idx = 0

    def build(self):
        p2_btn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player2,
            tra_src='Player 2', tra_tra=_('Player 2'),
            **self.menu_props.btn_args)
        self.add_widgets([p2_btn])
        InputPageGui4Joystick.build(self)

    def on_player2(self):
        dct = self.update_values()
        self.notify('on_push_page', 'input2joystick', [self.keys, dct])
        self.eng.joystick_mgr.is_recording = False

    def _on_back(self, player=0):
        dct = self.update_values()
        self.mediator.event.on_back()
        self.notify('on_back', 'input_page1', [dct])
        self.eng.joystick_mgr.is_recording = False

    def update_values(self):
        suff = str(self.joyp_idx + 1)
        dct = {}
        dct['joystick'] = self.keys
        dct['joystick']['forward' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[0]['text'])
        dct['joystick']['rear' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[1]['text'])
        dct['joystick']['fire' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[2]['text'])
        dct['joystick']['respawn' + suff] = self.eng.event.desc2key(self.mediator.gui.ibuttons[3]['text'])
        return dct


class InputPageGui2Joystick(InputPageGui4Joystick):

    joyp_idx = 1

    def build(self):
        p_btn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player3,
            tra_src='Player 3', tra_tra=_('Player 3'),
            **self.menu_props.btn_args)
        self.add_widgets([p_btn])
        InputPageGui4Joystick.build(self)

    def on_player3(self):
        dct = self.update_values()
        self.notify('on_push_page', 'input3joystick', [self.keys, dct])
        self.eng.joystick_mgr.is_recording = False

    def _on_back(self, player=0):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page2', [dct])
        self.eng.joystick_mgr.is_recording = False


class InputPageGui3Joystick(InputPageGui4Joystick):

    joyp_idx = 2

    def build(self):
        p_btn = Btn(
            text='', pos=(0, -.74), cmd=self.on_player3,
            tra_src='Player 4', tra_tra=_('Player 4'),
            **self.menu_props.btn_args)
        self.add_widgets([p_btn])
        InputPageGui4Joystick.build(self)

    def on_player3(self):
        dct = self.update_values()
        self.notify('on_push_page', 'input4joystick', [self.keys, dct])
        self.eng.joystick_mgr.is_recording = False

    def _on_back(self, player=0):
        self.mediator.event.on_back()
        suff = str(self.joyp_idx + 1)
        dct = self.update_values()
        self.notify('on_back', 'input_page3', [dct])
        self.eng.joystick_mgr.is_recording = False


class InputPage4Joystick(Page):
    gui_cls = InputPageGui4Joystick

    def __init__(self, menu_props, opt_file, keys):
        self.menu_props = menu_props
        self.keys = keys
        self.opt_file = opt_file
        Page.__init__(self, menu_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls,
          [self, self.menu_props, self.opt_file, self.keys])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)


class InputPage2Joystick(InputPage4Joystick):
    gui_cls = InputPageGui2Joystick


class InputPage3Joystick(InputPage4Joystick):
    gui_cls = InputPageGui3Joystick


class InputPageJoystick(InputPage4Joystick):
    gui_cls = InputPageGui1Joystick
