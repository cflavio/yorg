from yaml import load
from random import shuffle
from panda3d.core import TextNode, TextPropertiesManager, TextProperties
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from yyagl.racing.season.season import SeasonProps, Season, SingleRaceSeason
from yyagl.engine.gui.imgbtn import ImageButton
from yyagl.gameobject import GameObjectMdt
from .netmsgs import NetMsgs
from .driverpage import DriverPage


class CarPageGui(PageGui):

    def __init__(self, mdt, menu, cars, car_path, phys_path, player_name,
                 drivers_img, cars_img):
        self.car = None
        self.current_cars = None
        self.track_path = None
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui

        txt = OnscreenText(text=_('Select the car'), pos=(0, .8),
                           **menu_gui.text_args)
        widgets = [txt]

        self.track_path = self.menu.track
        self.cars = ['kronos', 'themis', 'diones', 'iapeto']
        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        names = names[:5]
        t_a = self.menu.gui.text_args.copy()
        del t_a['scale']
        for i in range(len(self.cars)):
            img = ImageButton(
                scale=.38, pos=(-1.2 + i * .8, 1, .1), frameColor=(0, 0, 0, 0),
                image=self.car_path % self.cars[i],
                command=self.on_car, extraArgs=[self.cars[i]],
                **self.menu.gui.imgbtn_args)
            txt = OnscreenText(self.cars[i], pos=(-1.2 + i * .8, .38),
                               scale=.072, **t_a)
            thanks = OnscreenText(_('thanks to:'), pos=(-1.2 + i * .8, -.14),
                                  scale=.052, **t_a)
            name = OnscreenText(names[i], pos=(-1.2 + i * .8, -.24),
                                scale=.072, **t_a)
            ppath = self.phys_path % self.cars[i]
            with open(ppath) as phys_file:
                cfg = load(phys_file)
            speed = cfg['max_speed'] / 140.0
            fric = cfg['friction_slip'] / 3.0
            roll = cfg['roll_influence'] / .2
            speed = int(round((speed - 1) * 100))
            fric = int(round((fric - 1) * 100))
            roll = -int(round((roll - 1) * 100))
            tp_mgr = TextPropertiesManager.getGlobalPtr()
            colors = [(.75, .25, .25, 1), (.25, .75, .25, 1)]
            for namecol, col in zip(['red', 'green'], colors):
                _tp = TextProperties()
                _tp.setTextColor(col)
                tp_mgr.setProperties(namecol, _tp)
            sign = lambda x: '\1green\1+\2' if x > 0 else ''
            psign = lambda x: '+' if x == 0 else sign(x)
            col = lambda x: '\1green\1%s\2' % x if x > 0 else '\1red\1%s\2' % x
            pcol = lambda x: x if x == 0 else col(x)
            fric_txt = OnscreenText(
                '%s: %s%s%%' % (_('adherence'), psign(fric), pcol(fric)),
                pos=(-.87 + i * .8, .28), scale=.052, align=TextNode.A_right,
                **t_a)
            speed_txt = OnscreenText(
                '%s: %s%s%%' % (_('speed'), psign(speed), pcol(speed)),
                pos=(-.87 + i * .8, .18), scale=.052, align=TextNode.A_right,
                **t_a)
            roll_txt = OnscreenText(
                '%s: %s%s%%' % (_('stability'), psign(roll), pcol(roll)),
                pos=(-.87 + i * .8, .08), scale=.052, align=TextNode.A_right,
                **t_a)
            widgets += [img, txt, name, thanks, speed_txt, fric_txt, roll_txt]
        map(self.add_widget, widgets)
        self.current_cars = {}
        PageGui.build_page(self)

    def _buttons(self, car):
        is_btn = lambda wdg: wdg.__class__ == DirectButton
        buttons = [wdg for wdg in self.widgets if is_btn(wdg)]
        return [btn for btn in buttons if btn['extraArgs'] == [car]]

    def on_car(self, car):
        self.mdt.menu.gui.notify('on_car_selected', car)
        self.menu.push_page(DriverPage(
            self.menu, self.track_path, car, self.player_name,
            self.drivers_img, self.cars_img, self.cars))


class CarPageGuiSeason(CarPageGui):

    def on_car(self, car):
        self.mdt.menu.gui.notify('on_car_selected_season', car)
        self.menu.push_page(DriverPage(
            self.menu, self.track_path, car, self.player_name,
            self.drivers_img, self.cars_img, self.cars))


class CarPageGuiServer(CarPageGui):

    def build_page(self):
        CarPageGui.build_page(self)
        eng.register_server_cb(self.process_srv)
        eng.car_mapping = {}

    def on_car(self, car):
        eng.log('car selected: ' + car)
        eng.server_send([NetMsgs.car_selection, car])
        for btn in self._buttons(car):
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if self in self.current_cars:
            curr_car = self.current_cars[self]
            eng.log('car deselected: ' + curr_car)
            eng.server_send([NetMsgs.car_deselection, curr_car])
            for btn in self._buttons(curr_car):
                btn['state'] = NORMAL
                btn.setAlphaScale(1)
        self.current_cars[self] = car
        eng.car_mapping['self'] = car
        self.evaluate_starting()

    def evaluate_starting(self):
        connections = eng.connections + [self]
        if all(conn in self.current_cars for conn in connections):
            packet = [NetMsgs.start_race]
            packet += [len(self.current_cars)]

            def process(k):
                '''Processes a car.'''
                return 'server' if k == self else k.getAddress().getIpString()
            for k, val in self.current_cars.items():
                packet += [process(k), val]
            eng.server_send(packet)
            eng.log('start race: ' + str(packet))
            curr_car = self.current_cars[self]
            # manage as event
            game.logic.season = SingleRaceSeason()
            game.fsm.demand('Race', self.track_path, curr_car, packet[2:])

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_request:
            car = data_lst[1]
            eng.log('car requested: ' + car)
            btn = self._buttons(car)[0]
            if btn['state'] == DISABLED:
                eng.server_send([NetMsgs.car_deny], sender)
                eng.log('car already selected: ' + car)
            elif btn['state'] == NORMAL:
                eng.log('car selected: ' + car)
                if sender in self.current_cars:
                    _btn = self._buttons(self.current_cars[sender])[0]
                    _btn['state'] = NORMAL
                    _btn.setAlphaScale(1)
                self.current_cars[sender] = car
                btn['state'] = DISABLED
                btn.setAlphaScale(.25)
                eng.server_send([NetMsgs.car_confirm, car], sender)
                eng.server_send([NetMsgs.car_selection, car])
                eng.car_mapping[sender] = car
                self.evaluate_starting()


class CarPageGuiClient(CarPageGui):

    def build_page(self):
        CarPageGui.build_page(self)
        eng.register_client_cb(self.process_client)

    def on_car(self, car):
        eng.log('car request: ' + car)
        eng.client_send([NetMsgs.car_request, car])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_confirm:
            if self.car:
                _btn = self._buttons(self.car)[0]
                _btn['state'] = NORMAL
                _btn.setAlphaScale(1)
            self.car = car = data_lst[1]
            eng.log('car confirmed: ' + car)
            btn = self._buttons(car)[0]
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if data_lst[0] == NetMsgs.car_deny:
            eng.log('car denied')
        if data_lst[0] == NetMsgs.car_selection:
            car = data_lst[1]
            eng.log('car selection: ' + car)
            btn = self._buttons(car)[0]
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if data_lst[0] == NetMsgs.car_deselection:
            car = data_lst[1]
            eng.log('car deselection: ' + car)
            btn = self._buttons(car)[0]
            btn['state'] = NORMAL
            btn.setAlphaScale(1)
        if data_lst[0] == NetMsgs.start_race:
            eng.log('start_race: ' + str(data_lst))
            # manage as event
            game.logic.season = SingleRaceSeason()
            game.fsm.demand('Race', self.track_path, self.car, data_lst[2:])


class CarPage(Page):
    gui_cls = CarPageGui

    def __init__(self, menu, cars, car_path, phys_path, player_name,
                 drivers_img, cars_img):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, cars, car_path,
                                    phys_path, player_name, drivers_img,
                                    cars_img])]]
        GameObjectMdt.__init__(self, init_lst)


class CarPageSeason(CarPage):
    gui_cls = CarPageGuiSeason


class CarPageServer(Page):
    gui_cls = CarPageGuiServer


class CarPageClient(Page):
    gui_cls = CarPageGuiClient
