from itertools import product
from sleekxmpp.jid import JID
from yaml import load
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.library.gui import Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class CarPageGui(ThanksPageGui):

    def __init__(self, mediator, carpage_props, track_path):
        self.car = None
        self.current_cars = None
        self.track_path = track_path
        self.props = carpage_props
        ThanksPageGui.__init__(self, mediator, carpage_props.gameprops.menu_args)

    def build(self, exit_behav=False):
        gprops = self.props.gameprops
        widgets = [Text(
            _('Select the car'), pos=(-.2, .8),
            **self.menu_args.text_args)]
        cars_per_row = 4
        for row, col in product(range(2), range(cars_per_row)):
            if row * cars_per_row + col >= len(gprops.cars_names):
                break
            widgets += self.__bld_car(cars_per_row, row, col)
        self.add_widgets(widgets)
        self.current_cars = {}
        ThanksPageGui.build(self, exit_behav=exit_behav)

    def __bld_car(self, cars_per_row, row, col):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        gprops = self.props.gameprops
        z_offset = 0 if len(gprops.cars_names) > cars_per_row else .35
        num_car_row = len(gprops.cars_names) - cars_per_row if row == 1 else \
            min(cars_per_row, len(gprops.cars_names))
        x_offset = .4 * (cars_per_row - num_car_row)
        btn = ImgBtn(
            scale=.32,
            pos=(-1.4 + col * .64 + x_offset, 1, .4 - z_offset - row * .7),
            frameColor=(0, 0, 0, 0),
            image=gprops.car_path % gprops.cars_names[col + row*cars_per_row],
            command=self.on_car,
            extraArgs=[
                gprops.cars_names[col + row * cars_per_row]],
            **self.menu_args.imgbtn_args)
        widgets = [btn]
        txt = Text(
            gprops.cars_names[col + row * cars_per_row],
            pos=(-1.4 + col * .64 + x_offset, .64 - z_offset - row * .7),
            scale=.072, **t_a)
        name = Text(
            '',
            pos=(-1.4 + col * .64 + x_offset, .04 - z_offset - row * .7),
            scale=.046, **t_a)
        btn._name_txt = name
        widgets += [txt, name]
        car_name = gprops.cars_names[col + row * cars_per_row]
        cfg_fpath = gprops.phys_path % car_name
        with open(cfg_fpath) as phys_file:
            cfg = load(phys_file)
        speed = int(round((cfg['max_speed'] / 120.0 - 1) * 100))
        fric = int(round((cfg['friction_slip'][0] / 2.6 - 1) * 100))
        roll = -int(round((cfg['roll_influence'][0] / .21 - 1) * 100))
        sign = lambda x: '\1green\1+\2' if x > 0 else ''
        psign = lambda x, sgn=sign: '+' if x == 0 else sgn(x)
        __col_ = lambda x: '\1green\1%s\2' if x > 0 else '\1red\1%s\2'
        _col_ = lambda x, __col=__col_: __col(x) % x
        pcol = lambda x, _col=_col_: x if x == 0 else _col(x)
        txt_lst = [(_('adherence'), fric, .11), (_('speed'), speed, .27),
                   (_('stability'), roll, .19)]
        widgets += map(lambda txt_def: self.__add_txt(
            *txt_def + (psign, pcol, col, x_offset, z_offset, row)), txt_lst)
        return widgets

    def __add_txt(self, txt, val, pos_z, psign, pcol, col, x_offset, z_offset,
                  row):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return Text(
            '%s: %s%s%%' % (txt, psign(val), pcol(val)),
            pos=(-1.1 + col * .64 + x_offset, pos_z - z_offset - row * .7),
            scale=.052, align='right', **t_a)

    def _buttons(self, car):
        return [btn for btn in self.buttons if btn['extraArgs'] == [car]]

    def on_car(self, car):
        self.eng.log('selected ' + car)
        self.notify('on_car_selected', car)
        page_args = [self.track_path, car, self.props]
        self.notify('on_push_page', 'driver_page', page_args)


class CarPageGuiSeason(CarPageGui):

    def on_car(self, car):
        self.notify('on_car_selected_season', car)
        page_args = [self.track_path, car, self.props]
        self.notify('on_push_page', 'driver_page', page_args)


class CarPageGuiServer(CarPageGui):

    def build(self):
        CarPageGui.build(self, exit_behav=True)
        self.eng.server.register_cb(self.process_srv)
        self.eng.car_mapping = {}

    def on_car(self, car):
        self.eng.log_mgr.log('car selected: ' + car)
        name = JID(self.eng.xmpp.client.boundjid).bare
        self.eng.server.send([NetMsgs.car_selection, car, name])
        for btn in self._buttons(car):
            btn.disable()
            btn._name_txt['text'] = name
        if self in self.current_cars:
            curr_car = self.current_cars[self]
            self.eng.log_mgr.log('car deselected: ' + curr_car)
            self.eng.server.send([NetMsgs.car_deselection, curr_car])
            for btn in self._buttons(curr_car):
                btn.enable()
                btn._name_txt['text'] = ''
        self.current_cars[self] = car
        self.eng.car_mapping['self'] = car
        self.evaluate_starting()

    def evaluate_starting(self):
        connections = [conn[0]
                       for conn in self.eng.server.connections] + [self]
        if not all(conn in self.current_cars for conn in connections): return
        packet = [NetMsgs.start_drivers, len(self.current_cars)]

        def process(k):
            '''Processes a car.'''
            return 'server' if k == self else k.get_address().get_ip_string()
        for i, (k, val) in enumerate(self.current_cars.items()):
            packet += [process(k), val,
                       self.props.gameprops.drivers_info[i].name]
        self.eng.server.send(packet)
        self.eng.log_mgr.log('start drivers: ' + str(packet))
        curr_car = self.current_cars[self]
        page_args = [self.track_path, curr_car, self.props]
        self.notify('on_push_page', 'driverpageserver', page_args)

    def process_srv(self, data_lst, sender):
        if data_lst[0] != NetMsgs.car_request: return
        car = data_lst[1]
        self.eng.log_mgr.log('car requested: ' + car)
        btn = self._buttons(car)[0]
        if btn['state'] == DISABLED:
            self.eng.server.send([NetMsgs.car_deny], sender)
            self.eng.log_mgr.log('car already selected: ' + car)
        elif btn['state'] == NORMAL:
            self.eng.log_mgr.log('car selected: ' + car)
            if sender in self.current_cars:
                _btn = self._buttons(self.current_cars[sender])[0]
                _btn.enable()
                _btn._name_txt['text'] = ''
            self.current_cars[sender] = car
            btn.disable()
            for conn_info in self.eng.server.connections:
                conn, addr = conn_info
                if conn == sender:
                    curr_addr = addr
            username = ''
            for usr in self.eng.xmpp.users:
                if usr.local_addr == addr:
                    username = usr.name
            if not username:
                for usr in self.eng.xmpp.users:
                    if usr.public_addr == addr:
                        username = usr.name
            btn._name_txt['text'] = JID(username).bare
            self.eng.server.send([NetMsgs.car_confirm, car], sender)
            self.eng.server.send([NetMsgs.car_selection, car, username])
            ip_string = sender.get_address().get_ip_string()
            if ip_string.startswith('::ffff:'): ip_string = ip_string[7:]
            self.eng.car_mapping[ip_string] = car
            self.evaluate_starting()


class CarPageGuiClient(CarPageGui):

    def build(self):
        CarPageGui.build(self, exit_behav=True)
        self.eng.client.register_cb(self.process_client)

    def on_car(self, car):
        self.eng.log_mgr.log('car request: ' + car)
        self.eng.client.send(
            [NetMsgs.car_request, car, self.eng.client.my_addr])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_confirm:
            if self.car:
                _btn = self._buttons(self.car)[0]
                _btn.enable()
                _btn._name_txt['text'] = ''
            self.car = car = data_lst[1]
            self.eng.log_mgr.log('car confirmed: ' + car)
            btn = self._buttons(car)[0]
            btn.disable()
            btn._name_txt['text'] = JID(self.eng.xmpp.client.boundjid).bare
        if data_lst[0] == NetMsgs.car_deny:
            self.eng.log_mgr.log('car denied')
        if data_lst[0] == NetMsgs.car_selection:
            car = data_lst[1]
            name = data_lst[2]
            self.eng.log_mgr.log('car selection: ' + car)
            btn = self._buttons(car)[0]
            btn.disable()
            btn._name_txt['text'] = name
        if data_lst[0] == NetMsgs.car_deselection:
            car = data_lst[1]
            self.eng.log_mgr.log('car deselection: ' + car)
            btn = self._buttons(car)[0]
            btn.enable()
            btn._name_txt['text'] = ''
        if data_lst[0] == NetMsgs.start_drivers:
            self.eng.log_mgr.log('start_drivers: ' + str(data_lst))
            page_args = [self.track_path, self.car, self.props]
            self.notify('on_push_page', 'driverpageclient', page_args)


class CarPage(Page):
    gui_cls = CarPageGui

    def __init__(self, carpage_props, track_path):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, carpage_props, track_path])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)


class CarPageSeason(CarPage):
    gui_cls = CarPageGuiSeason


class CarPageServer(CarPage):
    gui_cls = CarPageGuiServer


class CarPageClient(CarPage):
    gui_cls = CarPageGuiClient
