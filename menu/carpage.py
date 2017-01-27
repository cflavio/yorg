from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui
from yyagl.racing.season.season import SingleRaceSeason
from yyagl.engine.gui.imgbtn import ImageButton
from .netmsgs import NetMsgs
from .driverpage import DriverPage
from direct.gui.OnscreenText import OnscreenText


class CarPageGui(PageGui):

    def __init__(self, mdt, menu):
        self.car = None
        self.current_cars = None
        self.track_path = None
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui

        txt = OnscreenText(text=_('Select the car'), pos=(0, .8), **menu_gui.text_args)
        self.widgets += [txt]

        self.track_path = 'tracks/' + self.menu.track
        menu_data = ['kronos', 'themis', 'diones', 'iapeto']
        names = ['Quartero', 'Calva', 'Murgia', 'Baronio']
        t_a = self.menu.gui.text_args.copy()
        del t_a['scale']
        for i in range(len(menu_data)):
            img = ImageButton(
                scale=.38, pos=(-1.2 + i * .8, 1, .1), frameColor=(0, 0, 0, 0),
                image='assets/images/cars/%s.png' % menu_data[i],
                command=self.on_car, extraArgs=[menu_data[i]],
                **self.menu.gui.imgbtn_args)
            name = OnscreenText(' '.join([names[i], menu_data[i].capitalize()]), pos=(-1.2 + i * .8, -.25), scale=.065, **t_a)
            self.widgets += [img, name]
        self.current_cars = {}
        PageGui.build_page(self)

    def _buttons(self, car):
        is_btn = lambda wdg: wdg.__class__ == DirectButton
        buttons = [wdg for wdg in self.widgets if is_btn(wdg)]
        return [btn for btn in buttons if btn['extraArgs'] == [car]]

    def on_car(self, car):
        self.menu.logic.push_page(DriverPage(self.menu, self.track_path, car))


class CarPageGuiServer(CarPageGui):

    def build_page(self):
        CarPageGui.build_page(self)
        eng.server.register_cb(self.process_srv)
        eng.server.car_mapping = {}

    def on_car(self, car):
        eng.log_mgr.log('car selected: ' + car)
        eng.server.send([NetMsgs.car_selection, car])
        for btn in self._buttons(car):
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if self in self.current_cars:
            curr_car = self.current_cars[self]
            eng.log_mgr.log('car deselected: ' + curr_car)
            eng.server.send([NetMsgs.car_deselection, curr_car])
            for btn in self._buttons(curr_car):
                btn['state'] = NORMAL
                btn.setAlphaScale(1)
        self.current_cars[self] = car
        eng.server.car_mapping['self'] = car
        self.evaluate_starting()

    def evaluate_starting(self):
        connections = eng.server.connections + [self]
        if all(conn in self.current_cars for conn in connections):
            packet = [NetMsgs.start_race]
            packet += [len(self.current_cars)]

            def process(k):
                '''Processes a car.'''
                return 'server' if k == self else k.getAddress().getIpString()
            for k, val in self.current_cars.items():
                packet += [process(k), val]
            eng.server.send(packet)
            eng.log_mgr.log('start race: ' + str(packet))
            curr_car = self.current_cars[self]
            game.logic.season = SingleRaceSeason()
            game.fsm.demand('Race', self.track_path, curr_car, packet[2:])

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_request:
            car = data_lst[1]
            eng.log_mgr.log('car requested: ' + car)
            btn = self._buttons(car)[0]
            if btn['state'] == DISABLED:
                eng.server.send([NetMsgs.car_deny], sender)
                eng.log_mgr.log('car already selected: ' + car)
            elif btn['state'] == NORMAL:
                eng.log_mgr.log('car selected: ' + car)
                if sender in self.current_cars:
                    _btn = self._buttons(self.current_cars[sender])[0]
                    _btn['state'] = NORMAL
                    _btn.setAlphaScale(1)
                self.current_cars[sender] = car
                btn['state'] = DISABLED
                btn.setAlphaScale(.25)
                eng.server.send([NetMsgs.car_confirm, car], sender)
                eng.server.send([NetMsgs.car_selection, car])
                eng.server.car_mapping[sender] = car
                self.evaluate_starting()


class CarPageGuiClient(CarPageGui):

    def build_page(self):
        CarPageGui.build_page(self)
        eng.client.register_cb(self.process_client)

    def on_car(self, car):
        eng.log_mgr.log('car request: ' + car)
        eng.client.send([NetMsgs.car_request, car])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_confirm:
            if self.car:
                _btn = self._buttons(self.car)[0]
                _btn['state'] = NORMAL
                _btn.setAlphaScale(1)
            self.car = car = data_lst[1]
            eng.log_mgr.log('car confirmed: ' + car)
            btn = self._buttons(car)[0]
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if data_lst[0] == NetMsgs.car_deny:
            eng.log_mgr.log('car denied')
        if data_lst[0] == NetMsgs.car_selection:
            car = data_lst[1]
            eng.log_mgr.log('car selection: ' + car)
            btn = self._buttons(car)[0]
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if data_lst[0] == NetMsgs.car_deselection:
            car = data_lst[1]
            eng.log_mgr.log('car deselection: ' + car)
            btn = self._buttons(car)[0]
            btn['state'] = NORMAL
            btn.setAlphaScale(1)
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start_race: ' + str(data_lst))
            game.logic.season = SingleRaceSeason()
            game.fsm.demand('Race', self.track_path, self.car, data_lst[2:])


class CarPage(Page):
    gui_cls = CarPageGui


class CarPageServer(Page):
    gui_cls = CarPageGuiServer

class CarPageClient(Page):
    gui_cls = CarPageGuiClient
