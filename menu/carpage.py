from itertools import product
from yaml import load
from panda3d.core import TextNode
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.engine.network.server import Server
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.engine.network.client import Client
from yyagl.racing.season.season import SingleRaceSeason
from yyagl.gameobject import GameObject
from .netmsgs import NetMsgs
from .driverpage import DriverPageProps
from .thankspage import ThanksPageGui


class CarPageProps(object):

    def __init__(self, cars, car_path, phys_path, player_name, drivers_img,
                 cars_img, drivers):
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        self.drivers = drivers


class CarPageGui(ThanksPageGui):

    def __init__(self, mdt, menu_args, carpage_props, track_path):
        self.car = None
        self.current_cars = None
        self.track_path = track_path
        self.props = carpage_props
        ThanksPageGui.__init__(self, mdt, menu_args)

    def bld_page(self):
        if game.logic.curr_cars:
            self.props.cars = game.logic.curr_cars
        widgets = [OnscreenText(
            text=_('Select the car'), pos=(0, .8),
            **self.menu_args.text_args)]
        cars_per_row = 4
        for row, col in product(range(2), range(cars_per_row)):
            if row * cars_per_row + col >= len(self.props.cars):
                break
            widgets += self.__bld_car(cars_per_row, row, col)
        map(self.add_widget, widgets)
        self.current_cars = {}
        ThanksPageGui.bld_page(self)

    def __bld_car(self, cars_per_row, row, col):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        z_offset = 0 if len(self.props.cars) > cars_per_row else .35
        num_car_row = len(self.props.cars) - cars_per_row if row == 1 else \
            min(cars_per_row, len(self.props.cars))
        x_offset = .4 * (cars_per_row - num_car_row)
        btn = ImgBtn(
            scale=.32,
            pos=(-1.2 + col * .8 + x_offset, 1, .4 - z_offset - row * .7),
            frameColor=(0, 0, 0, 0),
            image=self.props.car_path % self.props.cars[col + row * cars_per_row],
            command=self.on_car,
            extraArgs=[self.props.cars[col + row * cars_per_row]],
            **self.menu_args.imgbtn_args)
        widgets = [btn]
        txt = OnscreenText(
            self.props.cars[col + row * cars_per_row],
            pos=(-1.2 + col * .8 + x_offset, .64 - z_offset - row * .7),
            scale=.072, **t_a)
        widgets += [txt]
        car_name = self.props.cars[col + row * cars_per_row]
        cfg_fpath = self.props.phys_path % car_name
        with open(cfg_fpath) as phys_file:
            cfg = load(phys_file)
        speed = int(round((cfg['max_speed'] / 140.0 - 1) * 100))
        fric = int(round((cfg['friction_slip'] / 3.0 - 1) * 100))
        roll = -int(round((cfg['roll_influence'] / .2 - 1) * 100))
        sign = lambda x: '\1green\1+\2' if x > 0 else ''
        psign = lambda x, sgn=sign: '+' if x == 0 else sgn(x)
        __col_ = lambda x: '\1green\1%s\2' if x > 0 else '\1red\1%s\2'
        _col_ = lambda x, __col=__col_: __col(x) % x
        pcol = lambda x, _col=_col_: x if x == 0 else _col(x)
        txt_lst = [(_('adherence'), fric, .11), (_('speed'), speed, .27),
                   (_('stability'), roll, .19)]
        widgets += map(lambda txt_def: self.__add_txt(*txt_def + (psign, pcol, col, x_offset, z_offset, row)), txt_lst)
        return widgets

    def __add_txt(self, txt, val, pos_z, psign, pcol, col, x_offset, z_offset,
                  row):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return OnscreenText(
            '%s: %s%s%%' % (txt, psign(val), pcol(val)),
            pos=(-.9 + col * .8 + x_offset, pos_z - z_offset - row * .7),
            scale=.052, align=TextNode.A_right, **t_a)

    def _buttons(self, car):
        return [btn for btn in self.buttons if btn['extraArgs'] == [car]]

    def on_car(self, car):
        self.notify('on_car_selected', car)
        driverpage_props = DriverPageProps(
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.cars, self.props.drivers)
        page_args = [self.track_path, car, driverpage_props]
        self.notify('on_push_page', 'driver_page', page_args)


class CarPageGuiSeason(CarPageGui):

    def on_car(self, car):
        self.notify('on_car_selected_season', car)
        driverpage_props = DriverPageProps(
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.cars, self.props.drivers)
        page_args = [self.track_path, car, driverpage_props]
        self.notify('on_push_page', 'driver_page', page_args)


class CarPageGuiServer(CarPageGui):

    def bld_page(self):
        CarPageGui.bld_page(self)
        self.eng.register_server_cb(self.process_srv)
        self.eng.car_mapping = {}

    def on_car(self, car):
        self.eng.log('car selected: ' + car)
        self.eng.server.send([NetMsgs.car_selection, car])
        for btn in self._buttons(car):
            btn.disable()
        if self in self.current_cars:
            curr_car = self.current_cars[self]
            self.eng.log('car deselected: ' + curr_car)
            self.eng.server.send([NetMsgs.car_deselection, curr_car])
            for btn in self._buttons(curr_car):
                btn.enable()
        self.current_cars[self] = car
        self.eng.car_mapping['self'] = car
        self.evaluate_starting()

    def evaluate_starting(self):
        connections = self.eng.connections + [self]
        if not all(conn in self.current_cars for conn in connections): return
        packet = [NetMsgs.start_race, len(self.current_cars)]

        def process(k):
            '''Processes a car.'''
            return 'server' if k == self else k.get_address().get_ip_string()
        for k, val in self.current_cars.items():
            packet += [process(k), val]
        self.eng.server.send(packet)
        self.eng.log('start race: ' + str(packet))
        curr_car = self.current_cars[self]
        # manage as event
        game.logic.season = SingleRaceSeason()
        game.fsm.demand('Race', self.track_path, curr_car, packet[2:])

    def process_srv(self, data_lst, sender):
        if data_lst[0] != NetMsgs.car_request: return
        car = data_lst[1]
        self.eng.log('car requested: ' + car)
        btn = self._buttons(car)[0]
        if btn['state'] == DISABLED:
            self.eng.server.send([NetMsgs.car_deny], sender)
            self.eng.log('car already selected: ' + car)
        elif btn['state'] == NORMAL:
            self.eng.log('car selected: ' + car)
            if sender in self.current_cars:
                _btn = self._buttons(self.current_cars[sender])[0]
                _btn.enable()
            self.current_cars[sender] = car
            btn.disable()
            self.eng.server.send([NetMsgs.car_confirm, car], sender)
            self.eng.server.send([NetMsgs.car_selection, car])
            self.eng.car_mapping[sender] = car
            self.evaluate_starting()


class CarPageGuiClient(CarPageGui):

    def bld_page(self):
        CarPageGui.bld_page(self)
        self.eng.register_client_cb(self.process_client)

    def on_car(self, car):
        self.eng.log('car request: ' + car)
        self.eng.client.send([NetMsgs.car_request, car])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_confirm:
            if self.car:
                _btn = self._buttons(self.car)[0]
                _btn.enable()
            self.car = car = data_lst[1]
            self.eng.log('car confirmed: ' + car)
            btn = self._buttons(car)[0]
            btn.disable()
        if data_lst[0] == NetMsgs.car_deny:
            self.eng.log('car denied')
        if data_lst[0] == NetMsgs.car_selection:
            car = data_lst[1]
            self.eng.log('car selection: ' + car)
            btn = self._buttons(car)[0]
            btn.disable()
        if data_lst[0] == NetMsgs.car_deselection:
            car = data_lst[1]
            self.eng.log('car deselection: ' + car)
            btn = self._buttons(car)[0]
            btn.enable()
        if data_lst[0] == NetMsgs.start_race:
            self.eng.log('start_race: ' + str(data_lst))
            # manage as event
            game.logic.season = SingleRaceSeason()
            game.fsm.demand('Race', self.track_path, self.car, data_lst[2:])


class CarPage(Page):
    gui_cls = CarPageGui

    def __init__(self, menu_args, carpage_props, track_path):
        self.menu_args = menu_args
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, carpage_props,
                                    track_path])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)


class CarPageSeason(CarPage):
    gui_cls = CarPageGuiSeason


class CarPageServer(CarPage):
    gui_cls = CarPageGuiServer


class CarPageClient(CarPage):
    gui_cls = CarPageGuiClient
