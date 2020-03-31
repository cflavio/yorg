from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class InputSelPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props, opt_file, keys, joystick):
        self.props = mp_props
        self.opt_file = opt_file
        self.keys = keys
        self.joystick = joystick
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    def build(self):
        lmp_cb = lambda: self.notify('on_push_page', 'input1keyboard',
                                     [self.keys])
        omp_cb = lambda: self.notify('on_push_page', 'input1joystick',
                                     [self.joystick])
        menu_data = [
            ('Keyboard', _('Keyboard'), lmp_cb),
            ('Joystick', _('Joystick'), omp_cb)]
        widgets = [
            Btn(text=menu[0], pos=(0, .3-i*.28), cmd=menu[2],
                **self.props.gameprops.menu_props.btn_args)
            for i, menu in enumerate(menu_data)]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def enable(self, players):
        ThanksPageGui.enable(self, players)
        (self.widgets[1].enable if self.eng.joystick_mgr.joystick_lib.num_joysticks else self.widgets[1].disable)()

    def update_keys(self): self.keys = self.opt_file['settings']['keys']

    def _on_back(self, player=0): self.notify('on_back', 'input_sel', [self.keys])


class InputSelPage(Page):
    gui_cls = InputSelPageGui

    def __init__(self, mp_props, opt_file, keys, joystick):
        self.__mp_props = mp_props
        self.__opt_file = opt_file
        self.__keys = keys
        self.__joystick = joystick
        GameObject.__init__(self)
        self.event = self.event_cls(self)
        self.gui = self.gui_cls(self, self.__mp_props, self.__opt_file, self.__keys, self.__joystick)
        # invoke Page's __init__

    def destroy(self):
        self.event.destroy()
        self.gui.destroy()
        GameObject.destroy(self)
