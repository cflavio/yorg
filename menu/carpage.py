from logging import info
from itertools import product
from yaml import load
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.lib.gui import Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class CarPageGui(ThanksPageGui):

    def __init__(self, mediator, carpage_props, track_path, nplayers=1):
        self.car = None
        self.current_cars = None
        self.track_path = track_path
        self.props = carpage_props
        nplayers = list(range(nplayers))
        ThanksPageGui.__init__(self, mediator, carpage_props.gameprops.menu_props, nplayers)

    def build(self, exit_behav=False):
        gprops = self.props.gameprops
        widgets = [Text(
            _('Select the car'), pos=(0, .8),
            **self.menu_props.text_args)]
        cars_per_row = 4
        for row, col in product(range(2), range(cars_per_row)):
            if row * cars_per_row + col >= len(gprops.cars_names):
                break
            widgets += self.__bld_car(cars_per_row, row, col)
        self.add_widgets(widgets)
        self.current_cars = {}
        ThanksPageGui.build(self, exit_behav=exit_behav)

    def __bld_car(self, cars_per_row, row, col):
        t_a = self.menu_props.text_args.copy()
        del t_a['scale']
        gprops = self.props.gameprops
        z_offset = 0 if len(gprops.cars_names) > cars_per_row else .35
        num_car_row = len(gprops.cars_names) - cars_per_row if row == 1 else \
            min(cars_per_row, len(gprops.cars_names))
        x_offset = .4 * (cars_per_row - num_car_row)
        btn = ImgBtn(
            scale=(.32, .32),
            pos=(-.96 + col * .64 + x_offset, .4 - z_offset - row * .7),
            frame_col=(0, 0, 0, 0),
            img=gprops.car_path % gprops.cars_names[col + row*cars_per_row],
            cmd=self.on_car,
            extra_args=[
                gprops.cars_names[col + row * cars_per_row]],
            **self.menu_props.imgbtn_args)
        widgets = [btn]
        txt = Text(
            gprops.cars_names[col + row * cars_per_row],
            pos=(-.96 + col * .64 + x_offset, .64 - z_offset - row * .7),
            scale=.072, **t_a)
        name = Text(
            '',
            pos=(-.96 + col * .64 + x_offset, .04 - z_offset - row * .7),
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
        widgets += list(map(lambda txt_def: self.__add_txt(
            *txt_def + (psign, pcol, col, x_offset, z_offset, row)), txt_lst))
        return widgets

    def __add_txt(self, txt, val, pos_z, psign, pcol, col, x_offset, z_offset,
                  row):
        t_a = self.menu_props.text_args.copy()
        del t_a['scale']
        return Text(
            '%s: %s%s%%' % (txt, psign(val), pcol(val)),
            pos=(-.68 + col * .64 + x_offset, pos_z - z_offset - row * .7),
            scale=.052, align='right', **t_a)

    def _buttons(self, car):
        return [btn for btn in self.buttons if btn['extraArgs'] == [car]]

    def on_car(self, car):
        info('selected ' + car)
        self.notify('on_car_selected', car)
        page_args = [self.track_path, car, self.props]
        self.notify('on_push_page', 'driver_page', page_args)


class CarPageGuiSeason(CarPageGui):

    def on_car(self, car):
        self.notify('on_car_selected_season', car)
        page_args = [self.track_path, car, self.props]
        self.notify('on_push_page', 'driver_page', page_args)


class CarPageLocalMPGui(CarPageGui):

    def __init__(self, mediator, carpage_props, track_path, players):
        CarPageGui.__init__(self, mediator, carpage_props, track_path, players)
        self.selected_cars = {}
        for i in range(players): self.selected_cars[i] = None

    def on_car(self, car, player=0):
        if self.selected_cars[player]:
            self._buttons(self.selected_cars[player])[0].enable()
        self._buttons(car)[0].disable()
        self.disable_navigation([player])
        self.selected_cars[player] = car
        info('selected %s (player %s)' % (car, player))
        self.notify('on_car_selected_mp', car, player)
        self.evaluate_start()

    def evaluate_start(self):
        nplayers = len(self.selected_cars.keys())
        if len([btn for btn in self.buttons if btn['state'] == DISABLED]) < nplayers: return
        cars = [self.selected_cars[i] for i in range(nplayers)]
        page_args = [self.track_path, cars, self.props]
        self.notify('on_push_page', 'driver_page_mp', page_args)


class CarPageGuiServer(CarPageGui):

    def build(self):
        CarPageGui.build(self, exit_behav=True)
        self.eng.car_mapping = {}
        self.eng.xmpp.attach(self.on_presence_unavailable)
        self.eng.client.attach(self.on_presence_unavailable_room)
        self.eng.server.register_rpc(self.car_request)

    def on_car(self, car):
        info('car selected: ' + car)
        #name = JID(self.eng.xmpp.client.boundjid).bare
        #self.eng.server.send([NetMsgs.car_selection, car, name])
        self.eng.client.register_rpc('car_request')
        ret = self.eng.client.car_request(car)
        if ret != 'ok': return
        for btn in self._buttons(car):
            btn.disable()
            btn._name_txt['text'] = self.eng.client.myid
        if self in self.current_cars:
            curr_car = self.current_cars[self]
            info('car deselected: ' + curr_car)
            self.eng.server.send([NetMsgs.car_deselection, curr_car])
            for btn in self._buttons(curr_car):
                btn.enable()
                btn._name_txt['text'] = ''
        self.current_cars[self] = car
        self.eng.car_mapping['self'] = car
        self.notify('on_car_selected_omp_srv', car)
        #self.evaluate_starting()

    #def evaluate_starting(self):
    #    connections = [conn for conn in self.eng.server.connections] + [self]
    #    if not all(conn in self.current_cars for conn in connections): return
    #    packet = [NetMsgs.start_drivers, len(self.current_cars)]

    #    def process(k):
    #        '''Processes a car.'''
    #        return 'server' if k == self else k.getpeername()
    #    for i, (k, val) in enumerate(self.current_cars.items()):
    #        packet += [process(k), val,
    #                   self.props.gameprops.drivers_info[i].name]
    #    self.eng.server.send(packet)
    #    self.eng.log_mgr.log('start drivers: ' + str(packet))
    #    curr_car = self.current_cars[self]
    #    page_args = [self.track_path, curr_car, self.props]
    #    self.notify('on_push_page', 'driverpageserver', page_args)

    def car_request(self, car, sender):
        info('car requested: ' + car)
        btn = self._buttons(car)[0]
        if btn['state'] == DISABLED:
            info('car already selected: ' + car)
            return False
        elif btn['state'] == NORMAL:
            info('car selected: ' + car)
            if sender in self.current_cars:
                _btn = self._buttons(self.current_cars[sender])[0]
                _btn.enable()
                _btn._name_txt['text'] = ''
            self.current_cars[sender] = car
            btn.disable()
            for conn in self.eng.server.connections:
                if conn == sender:
                    curr_addr = conn.getpeername()
            username = ''
            for usr in self.eng.xmpp.users:
                if usr.local_addr == curr_addr:
                    username = usr.name
            if not username:
                for usr in self.eng.xmpp.users:
                    if usr.public_addr == curr_addr:
                        username = usr.name
            #btn._name_txt['text'] = JID(username).bare
            self.eng.server.send([NetMsgs.car_selection, car, username])
            ip_string = sender.getpeername()[0]
            if ip_string.startswith('::ffff:'): ip_string = ip_string[7:]
            self.eng.car_mapping[ip_string] = car
            self.evaluate_starting()
            return True

    def on_presence_unavailable(self, msg):
        self.evaluate_starting()

    def on_presence_unavailable_room(self, uid, room_name):
        self.evaluate_starting()

    def destroy(self):
        self.eng.xmpp.detach(self.on_presence_unavailable)
        self.eng.client.detach(self.on_presence_unavailable_room)
        CarPageGui.destroy(self)


class CarPageGuiClient(CarPageGui):

    def __init__(self, mediator, carpage_props, track_path, uid_srv):
        CarPageGui.__init__(self, mediator, carpage_props, track_path)
        self.srv_usr = uid_srv

    def build(self):
        CarPageGui.build(self, exit_behav=True)
        self.eng.car_mapping = {}
        #self.eng.client.register_cb(self.process_client)
        self.eng.client.register_rpc('car_request')
        self.eng.client.attach(self.on_car_selection)
        self.eng.client.attach(self.on_car_deselection)
        self.eng.client.attach(self.on_start_drivers)
        self.eng.client.attach(self.on_presence_unavailable_room)

    def on_presence_unavailable_room(self, uid, room):
        if uid == self.srv_usr:
            self._back_btn.disable()

    def on_car(self, car):
        info('car request: ' + car)
        if self.eng.client.car_request(car):
            if self.car:
                _btn = self._buttons(self.car)[0]
                _btn.enable()
                _btn._name_txt['text'] = ''
            self.car = car
            info('car confirmed: ' + car)
            btn = self._buttons(car)[0]
            btn.disable()
            btn._name_txt['text'] = self.eng.client.myid
            self.notify('on_car_selected_omp_client', car)
        else: info('car denied')

    def on_car_selection(self, data_lst):
        car = data_lst[0]
        name = data_lst[1]
        info('car selection: ' + car)
        btn = self._buttons(car)[0]
        btn.disable()
        btn._name_txt['text'] = name
        self.eng.car_mapping[name] = car

    def on_car_deselection(self, data_lst):
        car = data_lst[0]
        info('car deselection: ' + car)
        btn = self._buttons(car)[0]
        btn.enable()
        btn._name_txt['text'] = ''

    def on_start_drivers(self, data_lst):
        info('start_drivers: ' + str(data_lst))
        page_args = [self.track_path, self.car, self.props]
        self.notify('on_push_page', 'driverpageclient', page_args)

    def _on_quit(self):
        if self.eng.server.is_active: self.eng.server.stop()
        self.eng.client.register_rpc('leave_curr_room')
        self.eng.client.leave_curr_room()
        CarPageGui._on_quit(self)

    def destroy(self):
        self.eng.client.detach(self.on_car_selection)
        self.eng.client.detach(self.on_car_deselection)
        self.eng.client.detach(self.on_start_drivers)
        self.eng.client.detach(self.on_presence_unavailable_room)
        CarPageGui.destroy(self)


class CarPage(Page):
    gui_cls = CarPageGui

    def __init__(self, carpage_props, track_path):
        self.carpage_props = carpage_props
        self.track_path = track_path
        Page.__init__(self, carpage_props)
        PageFacade.__init__(self)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.carpage_props, self.track_path)

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)


class CarPageSeason(CarPage):
    gui_cls = CarPageGuiSeason


class CarPageServer(CarPage):
    gui_cls = CarPageGuiServer


class CarPageClient(CarPage):
    gui_cls = CarPageGuiClient

    def __init__(self, carpage_props, track_path, uid_srv):
        self.__uid_srv = uid_srv
        CarPage.__init__(self, carpage_props, track_path)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.carpage_props, self.track_path, self.__uid_srv)


class CarPageLocalMP(CarPage, PageFacade):
    gui_cls = CarPageLocalMPGui

    def __init__(self, carpage_props, track_path, nplayers):
        self.carpage_props = carpage_props
        self.track_path = track_path
        self.nplayers = nplayers
        Page.__init__(self, carpage_props)
        PageFacade.__init__(self)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.carpage_props, self.track_path, self.nplayers)
