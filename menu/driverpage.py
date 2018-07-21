from itertools import product
from random import shuffle
from sleekxmpp.jid import JID
from panda3d.core import TextureStage, Texture, PNMImage, TextNode
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.library.gui import Entry, Text, Img
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from yyagl.racing.driver.driver import DriverInfo
from yyagl.library.panda.shader import load_shader
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


frag = '''#version 120
varying vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;

void main() {
    float dist_l = texcoord.x;
    float dist_r = 1 - texcoord.x;
    float dist_u = texcoord.y;
    float dist_b = 1 - texcoord.y;
    float alpha = min(dist_l, min(dist_r, min(dist_u, dist_b))) * 30;
    vec4 pix_a = texture2D(p3d_Texture0, texcoord);
    vec4 pix_b = texture2D(p3d_Texture1, texcoord);
    vec4 tex_col = mix(pix_a, pix_b, pix_b.a);
    gl_FragColor = tex_col * vec4(1, 1, 1, alpha);
}'''


class DriverPageGui(ThanksPageGui):

    def __init__(self, mediator, driverpage_props, yorg_client):
        self.props = driverpage_props
        self.sel_drv_img = None
        self.driver = None
        self.yorg_client = yorg_client
        ThanksPageGui.__init__(self, mediator, driverpage_props.gameprops.menu_args)

    def build(self, exit_behav):
        self.drv_info = self.props.gameprops.drivers_info
        menu_args = self.menu_args
        widgets = [Text(_('Select the driver'), pos=(-.2, .8),
                                **menu_args.text_args)]
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        self.name = Text(_('Write your name:'), pos=(-.3, .6), scale=.06,
                            align='right', wordwrap=128, **t_a)
        self.drivers = []
        for row, col in product(range(2), range(4)):
            idx = col + row * 4
            drv_btn = ImgBtn(
                scale=.24, pos=(-.95 + col * .5, 1, .3 - row * .64),
                frameColor=(0, 0, 0, 0),
                image=self.props.gameprops.drivers_img.path % idx,
                command=self.on_click, extraArgs=[idx],
                **self.menu_args.imgbtn_args)
            name = Text(
                '',
                pos=(-.95 + col * .5, .01 - row * .64),
                scale=.046, **t_a)
            drv_btn._name_txt = name
            widgets += [drv_btn, name]
            self.drivers += [widgets[-2]]
            sign = lambda pos_x: '\1green\1+\2' if pos_x > 0 else ''
            psign = lambda pos_x, sgn=sign: '+' if pos_x == 0 else sgn(pos_x)

            def ppcol(x):
                return '\1green\1%s\2' % x if x > 0 else '\1red\1%s\2' % x
            pcol = lambda x: x if x == 0 else ppcol(x)
            lab_lst = [(_('adherence'), .09), (_('speed'), .21),
                       (_('stability'), .15)]
            widgets += map(
                lambda lab_def: self.__add_lab(*(lab_def + (row, col))),
                lab_lst)
            txt_lst = [(self.drv_info[idx - 1].adherence, .09),
                       (self.drv_info[idx - 1].speed, .21),
                       (self.drv_info[idx - 1].stability, .15)]
            widgets += map(
                lambda txt_def: self.__add_txt(
                    *txt_def + (psign, pcol, col, row)),
                txt_lst)
        self.sel_drv_img = Img(
            self.props.gameprops.cars_img % self.mediator.car,
            parent=base.a2dBottomLeft, pos=(.3, 1, .4), scale=.28)
        widgets += [self.sel_drv_img, self.name]
        self.add_widgets(widgets)
        ffilterpath = self.eng.curr_path + 'yyagl/assets/shaders/filter.vert'
        with open(ffilterpath) as ffilter:
            vert = ffilter.read()
        shader = load_shader(vert, frag)
        if shader:
            self.sel_drv_img.set_shader(shader)
        self.sel_drv_img.set_transparency(True)
        self.t_s = TextureStage('ts')
        self.t_s.set_mode(TextureStage.MDecal)
        empty_img = PNMImage(1, 1)
        empty_img.add_alpha()
        empty_img.alpha_fill(0)
        tex = Texture()
        tex.load(empty_img)
        self.sel_drv_img.set_texture(self.t_s, tex)
        ThanksPageGui.build(self, exit_behav=exit_behav)

    def __add_lab(self, txt, pos_z, row, col):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return Text(
            txt + ':', pos=(-1.15 + col * .5, pos_z - row * .64),
            scale=.046, align='left', **t_a)

    def __add_txt(self, val, pos_z, psign, pcol, col, row):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return Text(
            '%s%s%%' % (psign(val), pcol(val)),
            pos=(-.75 + col * .5, pos_z - row * .64), scale=.052,
            align='right', **t_a)

    def enable_buttons(self, enable):
        [(drv.enable if enable else drv.disable)() for drv in self.drivers]

    def on_click(self, i):
        self.eng.log('selected driver ' + str(i))
        gprops = self.props.gameprops
        txt_path = gprops.drivers_img.path_sel
        self.sel_drv_img.set_texture(self.t_s, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        cars = gprops.cars_names[:]
        car_idx = cars.index(self.mediator.car)
        cars.remove(self.mediator.car)
        shuffle(cars)
        drv_idx = range(8)
        drv_idx.remove(i)
        shuffle(drv_idx)
        prev_drv = gprops.drivers_info[car_idx]
        gprops.drivers_info[car_idx] = gprops.drivers_info[i]
        gprops.drivers_info[car_idx].img_idx = i
        nname = self.this_name()
        gprops.drivers_info[car_idx].name = nname
        gprops.drivers_info[i] = prev_drv
        self.eng.log('drivers: ' + str(gprops.drivers_info))
        self.notify('on_driver_selected', self.ent.get(), self.mediator.track,
                    self.mediator.car)

    def _buttons(self, idx):
        return [btn for btn in self.buttons if btn['extraArgs'] == [idx]]

    def destroy(self):
        self.sel_drv_img = None
        PageGui.destroy(self)


class DriverPageSinglePlayerGui(DriverPageGui):

    def build(self):
        DriverPageGui.build(self, exit_behav=False)
        menu_args = self.menu_args
        self.ent = Entry(
            scale=.08, pos=(-.2, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText=self.props.gameprops.player_name or _('your name'),
            text_fg=menu_args.text_active)
        self.add_widgets([self.ent])
        self.update_tsk = taskMgr.add(self.update_text, 'update text')
        self.enable_buttons(False)

    def update_text(self, task):
        has_name = self.ent.get() != _('your name')
        if has_name and self.ent.get().startswith(_('your name')):
            self.ent.enterText(self.ent.get()[len(_('your name')):])
            self.enable_buttons(True)
        elif self.ent.get() in [_('your name')[:-1], '']:
            self.ent.enterText('')
            self.enable_buttons(False)
        elif self.ent.get() not in [_('your name'), '']:
            self.enable_buttons(True)
        return task.cont  # don't do a task, attach to modifications events

    def this_name(self): return self.ent.get()

    def destroy(self):
        taskMgr.remove(self.update_tsk)
        DriverPageGui.destroy(self)


class DriverPageServerGui(DriverPageGui):

    def build(self):
        DriverPageGui.build(self, exit_behav=True)
        self.current_drivers = []
        self.current_drivers_dct = {}
        self.name['align'] = TextNode.ACenter
        self.name['pos'] = (-.2, .6)
        self.name['text'] += ' ' + self.yorg_client.myid
        #self.eng.xmpp.attach(self.on_presence_unavailable)
        self.yorg_client.attach(self.on_presence_unavailable_room)
        self.eng.server.register_rpc(self.drv_request)

    def on_click(self, i):
        self.eng.log('selected driver ' + str(i))
        name = JID(self.eng.xmpp.client.boundjid).bare
        self.eng.server.send([NetMsgs.driver_selection, i, name])
        for btn in self._buttons(i):
            btn.disable()
            btn._name_txt['text'] = name
        if self in self.current_drivers_dct:
            curr_drv = self.current_drivers_dct[self]
            self.eng.log_mgr.log('driver deselected: %s' % curr_drv)
            self.eng.server.send([NetMsgs.driver_deselection, curr_drv])
            for btn in self._buttons(curr_drv):
                btn.enable()
                btn._name_txt['text'] = ''
        self.current_drivers_dct[self] = i
        gprops = self.props.gameprops
        txt_path = gprops.drivers_img.path_sel
        self.sel_drv_img.set_texture(self.t_s, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        #self.enable_buttons(False)
        self.current_drivers += [self]
        cars = gprops.cars_names[:]
        car_idx = cars.index(self.mediator.car)
        cars.remove(self.mediator.car)
        prev_drv = gprops.drivers_info[car_idx]
        #gprops.drivers_info[car_idx] = gprops.drivers_info[i]
        gprops.drivers_info[car_idx].img_idx = i
        nname = self.this_name()
        gprops.drivers_info[car_idx].name = nname
        #gprops.drivers_info[i] = prev_drv
        self.evaluate_starting()

    def this_name(self): return self.eng.xmpp.client.boundjid.bare

    def evaluate_starting(self):
        connections = self.eng.server.connections[:]
        connections += [self]
        if not all(conn in self.current_drivers for conn in connections):
            return
        self.notify(
            'on_driver_selected_server', self.this_name(), self.mediator.track,
            self.mediator.car, self.eng.car_mapping.values())

    def drv_request(self, car, driver_name, drv, driver_speed,
                    driver_adherence, driver_stability, sender):
        self.eng.log_mgr.log('driver requested: %s' % drv)
        btn = self._buttons(drv)[0]
        if btn['state'] == DISABLED:
            self.eng.log_mgr.log('driver already selected: %s' % drv)
            return False
        elif btn['state'] == NORMAL:
            self.eng.log_mgr.log('driver selected: %s' % drv)
            if sender in self.current_drivers_dct:
                _btn = self._buttons(self.current_drivers_dct[sender])[0]
                _btn.enable()
                _btn._name_txt['text'] = ''
            self.current_drivers_dct[sender] = drv
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
            btn._name_txt['text'] = JID(username).bare
            self.eng.server.send([NetMsgs.driver_selection, drv, username])
            self.current_drivers += [sender]
            self.eng.log_mgr.log(
                'driver selected: %s (%s) ' % (driver_name, drv))
            gprops = self.props.gameprops
            cars = gprops.cars_names[:]
            car_idx = cars.index(car)
            prev_drv = gprops.drivers_info[car_idx]
            gprops.drivers_info[car_idx] = DriverInfo(drv, driver_name, driver_speed, driver_adherence, driver_stability)
            for i, drv_i in enumerate(gprops.drivers_info):
                if drv_i.img_idx == drv and i != car_idx:
                    gprops.drivers_info[i] = prev_drv
            self.evaluate_starting()
            return True

    #def on_presence_unavailable(self, msg):
    #    self.evaluate_starting()

    def on_presence_unavailable_room(self, uid, room_name):
        self.evaluate_starting()

    def destroy(self):
        #self.eng.xmpp.detach(self.on_presence_unavailable)
        self.yorg_client.detach(self.on_presence_unavailable_room)
        DriverPageGui.destroy(self)


class DriverPageClientGui(DriverPageGui):

    def build(self):
        DriverPageGui.build(self, exit_behav=True)
        self.name['align'] = TextNode.ACenter
        self.name['pos'] = (-.2, .6)
        self.name['text'] += ' ' + self.yorg_client.myid
        self.eng.client.register_rpc('drv_request')
        self.yorg_client.attach(self.on_drv_selection)
        self.yorg_client.attach(self.on_drv_deselection)
        self.yorg_client.attach(self.on_start_race)

    def this_name(self): return self.yorg_client.myid

    def on_click(self, i):
        self.eng.log_mgr.log('driver request: %s' % i)
        gprops = self.props.gameprops
        if self.eng.client.drv_request(self.mediator.car, i,
                gprops.drivers_info[i].speed, gprops.drivers_info[i].adherence,
                gprops.drivers_info[i].stability):
            if self.driver:
                _btn = self._buttons(self.driver)[0]
                _btn.enable()
                _btn._name_txt['text'] = ''
            self.driver = drv = i
            self.eng.log_mgr.log('driver confirmed: %s' % drv)
            btn = self._buttons(drv)[0]
            btn.disable()
            btn._name_txt['text'] = self.yorg_client.myid
            gprops = self.props.gameprops
            txt_path = gprops.drivers_img.path_sel
            self.sel_drv_img.set_texture(self.t_s, loader.loadTexture(txt_path % drv))
        else: self.eng.log_mgr.log('driver denied')

    def on_drv_selection(self, data_lst):
        drv = data_lst[0]
        name = data_lst[1]
        self.eng.log_mgr.log('driver selection: %s' % drv)
        btn = self._buttons(drv)[0]
        btn.disable()
        btn._name_txt['text'] = name

    def on_drv_deselection(self, data_lst):
        drv = data_lst[0]
        self.eng.log_mgr.log('driver deselection: %s' % drv)
        btn = self._buttons(drv)[0]
        btn.enable()
        btn._name_txt['text'] = ''

    def on_start_race(self, data_lst):
        self.eng.log_mgr.log('start_race: ' + str(data_lst))
        cars = data_lst[2::6]
        self.notify('on_car_start_client', self.mediator.track,
                    self.mediator.car, cars, data_lst)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, track, car, driverpage_props, yorg_client):
        self.track = track
        self.car = car
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, driverpage_props, yorg_client])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)


class DriverPageSinglePlayer(DriverPage):
    gui_cls = DriverPageSinglePlayerGui

class DriverPageServer(DriverPage):
    gui_cls = DriverPageServerGui


class DriverPageClient(DriverPage):
    gui_cls = DriverPageClientGui
