from itertools import product
from random import shuffle
from panda3d.core import TextureStage, Texture, PNMImage, TextNode
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.lib.gui import Entry, Text, Img
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from yyagl.racing.driver.driver import DriverInfo
from yyagl.lib.p3d.shader import load_shader
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

    def __init__(self, mediator, driverpage_props, nplayers=1):
        self.props = driverpage_props
        self.sel_drv_img = None
        self.driver = None
        nplayers = list(range(nplayers))
        ThanksPageGui.__init__(self, mediator, driverpage_props.gameprops.menu_props, nplayers)

    def build(self, exit_behav):
        self.drv_info = self.props.gameprops.drivers_info
        menu_props = self.menu_props
        widgets = [Text(_('Select the driver'), pos=(0, .8),
                                **menu_props.text_args)]
        t_a = self.menu_props.text_args.copy()
        del t_a['scale']
        self.name = Text(_('Write your name:'), pos=(-.1, .6), scale=.06,
                            align='right', wordwrap=128, **t_a)
        self.drivers = []
        for row, col in product(range(2), range(4)):
            idx = col + row * 4
            drv_btn = ImgBtn(
                scale=(.24, .24), pos=(-.75 + col * .5, .3 - row * .64),
                frame_col=(0, 0, 0, 0),
                img=self.props.gameprops.drivers_img.path % idx,
                cmd=self.on_click, extra_args=[idx],
                **self.menu_props.imgbtn_args)
            name = Text(
                '',
                pos=(-.75 + col * .5, .01 - row * .64),
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
            widgets += list(map(
                lambda lab_def: self._add_lab(*(lab_def + (row, col))),
                lab_lst))
            txt_lst = [(self.drv_info[idx - 1].adherence, .09),
                       (self.drv_info[idx - 1].speed, .21),
                       (self.drv_info[idx - 1].stability, .15)]
            widgets += list(map(
                lambda txt_def: self._add_txt(
                    *txt_def + (psign, pcol, col, row)),
                txt_lst))
        self.sel_drv_img = Img(
            self.props.gameprops.cars_img % self.mediator.car,
            parent=base.a2dBottomLeft, pos=(.3, .4), scale=.28)
        instr_txt = _(
            'If you use the keyboard, press FIRE to edit the field, then '
            "ENTER when you're done")
        instr = Text(instr_txt, pos=(1.4, .6), scale=.042, wordwrap=16, **t_a)
        widgets += [self.sel_drv_img, self.name, instr]
        self.add_widgets(widgets)
        ffilterpath = self.eng.curr_path + 'yyagl/assets/shaders/filter.vert'
        with open(ffilterpath) as ffilter:
            vert = ffilter.read()
        shader = load_shader(vert, frag)
        if shader:
            self.sel_drv_img.set_shader(shader)
        self.sel_drv_img.set_transparent()
        self.t_s = TextureStage('ts')
        self.t_s.set_mode(TextureStage.MDecal)
        empty_img = PNMImage(1, 1)
        empty_img.add_alpha()
        empty_img.alpha_fill(0)
        tex = Texture()
        tex.load(empty_img)
        self.sel_drv_img.set_texture(self.t_s, tex)
        ThanksPageGui.build(self, exit_behav=exit_behav)

    def _add_lab(self, txt, pos_z, row, col):
        t_a = self.menu_props.text_args.copy()
        del t_a['scale']
        return Text(
            txt + ':', pos=(-.95 + col * .5, pos_z - row * .64),
            scale=.046, align='left', **t_a)

    def _add_txt(self, val, pos_z, psign, pcol, col, row):
        t_a = self.menu_props.text_args.copy()
        del t_a['scale']
        return Text(
            '%s%s%%' % (psign(val), pcol(val)),
            pos=(-.55 + col * .5, pos_z - row * .64), scale=.052,
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
        nname = self.this_name()
        gprops.drivers_info[i].name = nname
        self.eng.log('drivers: ' + str(gprops.drivers_info))
        self.notify('on_driver_selected', self.ent.text, self.mediator.track,
                    self.mediator.car)

    def _buttons(self, idx):
        return [btn for btn in self.buttons if btn['extraArgs'] == [idx]]

    def destroy(self):
        self.sel_drv_img = None
        PageGui.destroy(self)


class DriverPageSinglePlayerGui(DriverPageGui):

    def build(self):
        menu_props = self.menu_props
        all_names = self.props.gameprops.player_names + self.props.gameprops.stored_player_names[len(self.props.gameprops.player_names):]
        self.ent = Entry(
            scale=.08, pos=(0, .6), entry_font=menu_props.font, width=12,
            frame_col=menu_props.btn_col,
            initial_text=all_names[0] if all_names else _('your name'),
            text_fg=menu_props.text_active_col)
        self.add_widgets([self.ent])
        self.update_tsk = taskMgr.add(self.update_text, 'update text')
        DriverPageGui.build(self, exit_behav=False)
        self.enable_buttons(False)

    def update_text(self, task):
        has_name = self.ent.text != _('your name')
        if has_name and self.ent.text.startswith(_('your name')):
            self.ent.enter_text(self.ent.text[len(_('your name')):])
            self.enable_buttons(True)
        elif self.ent.text in [_('your name')[:-1], '']:
            self.ent.enter_text('')
            self.enable_buttons(False)
        elif self.ent.text not in [_('your name'), '']:
            self.enable_buttons(True)
        return task.cont  # don't do a task, attach to modifications events

    def this_name(self): return self.ent.text

    def destroy(self):
        taskMgr.remove(self.update_tsk)
        DriverPageGui.destroy(self)


class DriverPageMPGui(DriverPageGui):

    def __init__(self, mediator, driverpage_props, players):
        DriverPageGui.__init__(self, mediator, driverpage_props, players)
        self.selected_drivers = {}
        for i in range(players): self.selected_drivers[i] = None
        self.enabled = False

    def build(self):
        self.drv_info = self.props.gameprops.drivers_info
        menu_props = self.menu_props
        widgets = [Text(_('Select the drivers'), pos=(0, .91),
                                **menu_props.text_args)]
        t_a = self.menu_props.text_args.copy()
        del t_a['scale']
        self.name = Text(_('Write your names:'), pos=(-.1, .7), scale=.06,
                            align='right', wordwrap=128, **t_a)
        self.drivers = []
        for row, col in product(range(2), range(4)):
            idx = col + row * 4
            drv_btn = ImgBtn(
                scale=(.24, .24), pos=(-.75 + col * .5, .1 - row * .64),
                frame_col=(0, 0, 0, 0),
                img=self.props.gameprops.drivers_img.path % idx,
                cmd=self.on_click, extra_args=[idx],
                **self.menu_props.imgbtn_args)
            name = Text(
                '',
                pos=(-.75 + col * .5, -.19 - row * .64),
                scale=.046, **t_a)
            drv_btn._name_txt = name
            widgets += [drv_btn, name]
            self.drivers += [widgets[-2]]
            sign = lambda pos_x: '\1green\1+\2' if pos_x > 0 else ''
            psign = lambda pos_x, sgn=sign: '+' if pos_x == 0 else sgn(pos_x)

            def ppcol(x):
                return '\1green\1%s\2' % x if x > 0 else '\1red\1%s\2' % x
            pcol = lambda x: x if x == 0 else ppcol(x)
            lab_lst = [(_('adherence'), -.11), (_('speed'), .01),
                       (_('stability'), -.05)]
            widgets += list(map(
                lambda lab_def: self._add_lab(*(lab_def + (row, col))),
                lab_lst))
            txt_lst = [(self.drv_info[idx - 1].adherence, -.11),
                       (self.drv_info[idx - 1].speed, .01),
                       (self.drv_info[idx - 1].stability, -.05)]
            widgets += list(map(
                lambda txt_def: self._add_txt(
                    *txt_def + (psign, pcol, col, row)),
                txt_lst))
        self.sel_drv_img = []
        self.tss = []
        instr_txt = _(
            'If you use the keyboard, press FIRE to edit the field, then '
            "ENTER when you're done. Other players can't move while someone"
            'is writing (since, with keyboards, some letters may be bound to '
            'movements).')
        instr = Text(instr_txt, pos=(1.28, .8), scale=.042, wordwrap=24, **t_a)
        widgets += [self.name, instr]
        for i, car in enumerate(self.mediator.cars):
            self.sel_drv_img += [Img(
                self.props.gameprops.cars_img % car,
                parent=base.a2dBottomLeft, pos=(.3, 1.74 - i * .46), scale=.22)]
            widgets += [self.sel_drv_img[-1]]
            ffilterpath = self.eng.curr_path + 'yyagl/assets/shaders/filter.vert'
            with open(ffilterpath) as ffilter:
                vert = ffilter.read()
            shader = load_shader(vert, frag)
            if shader:
                self.sel_drv_img[-1].set_shader(shader)
            self.sel_drv_img[-1].set_transparent()
            self.tss += [TextureStage('ts')]
            self.tss[-1].set_mode(TextureStage.MDecal)
            empty_img = PNMImage(1, 1)
            empty_img.add_alpha()
            empty_img.alpha_fill(0)
            tex = Texture()
            tex.load(empty_img)
            self.sel_drv_img[-1].set_texture(self.tss[-1], tex)
        all_names = self.props.gameprops.player_names + self.props.gameprops.stored_player_names[len(self.props.gameprops.player_names):]
        self.ents = [Entry(
            scale=.06, pos=(0, .8 - .12 * i), entry_font=menu_props.font, width=12,
            frame_col=menu_props.btn_col,
            initial_text=all_names[i] if i < len(all_names) else _('your name'),
            text_fg=menu_props.text_active_col) for i in range(len(self.mediator.cars))]
        self.add_widgets(self.ents)
        self.add_widgets(widgets)
        ThanksPageGui.build(self, exit_behav=False)
        self.update_tsk = taskMgr.add(self.update_text, 'update text')
        self.enable_buttons(False)

    def on_click(self, drv, player=0):
        if self.selected_drivers[player] is not None:
            self._buttons(self.selected_drivers[player])[0].enable()
            self.drivers += [self._buttons(drv)[0]]
        self._buttons(drv)[0].disable()
        self.disable_navigation([player])
        self.selected_drivers[player] = drv
        self.eng.log('selected %s (player %s)' % (drv, player))
        gprops = self.props.gameprops
        txt_path = gprops.drivers_img.path_sel
        self.sel_drv_img[player].set_texture(self.tss[player], loader.loadTexture(txt_path % drv))
        nname = self.this_name(player)
        gprops.drivers_info[drv].name = nname
        self.eng.log('drivers: ' + str(gprops.drivers_info))
        self.drivers.remove(self._buttons(drv)[0])
        self.evaluate_start()

    def evaluate_start(self):
        nplayers = len(self.selected_drivers.keys())
        if len([btn for btn in self.buttons if btn['state'] == DISABLED]) < nplayers: return
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        drivers = [self.selected_drivers[i] for i in range(nplayers)]
        self.props.opt_file['settings']['player_names'] = [ent.text for ent in self.ents]
        stored_player_names = self.props.gameprops.stored_player_names
        for i, name in enumerate(self.props.opt_file['settings']['player_names']):
            if i < len(stored_player_names): stored_player_names[i] = name
            else: stored_player_names += [name]
        self.props.opt_file['settings']['stored_player_names'] = stored_player_names
        self.props.opt_file.store()
        self.notify('on_driver_selected_mp', [ent.text for ent in self.ents], self.mediator.track,
                    self.mediator.cars, drivers)

    def update_text(self, task):
        for ent in self.ents:
            if ent.text != _('your name') and ent.text.startswith(_('your name')):
                ent.enter_text(ent.text[len(_('your name')):])
            elif ent.text in [_('your name')[:-1], '']:
                ent.enter_text('')
        has_name = all(ent.text not in ['', _('your name')] for ent in self.ents)
        if has_name and not self.enabled:
            self.enabled = True
            self.enable_buttons(True)
        if any(ent.text in ['', _('your name')] for ent in self.ents):
            self.enable_buttons(False)
        return task.cont  # don't do a task, attach to modifications events

    def this_name(self, player): return self.ents[player].text

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
        self.name['text'] += ' ' + self.eng.client.myid
        #self.eng.xmpp.attach(self.on_presence_unavailable)
        self.eng.client.attach(self.on_presence_unavailable_room)
        self.eng.server.register_rpc(self.drv_request)

    def on_click(self, i):
        self.eng.log('selected driver ' + str(i))
        #name = JID(self.eng.xmpp.client.boundjid).bare
        #self.eng.server.send([NetMsgs.driver_selection, i, name])
        #for btn in self._buttons(i):
        #    btn.disable()
        #    btn._name_txt['text'] = name
        #if self in self.current_drivers_dct:
        #    curr_drv = self.current_drivers_dct[self]
        #    self.eng.log_mgr.log('driver deselected: %s' % curr_drv)
        #    self.eng.server.send([NetMsgs.driver_deselection, curr_drv])
        #    for btn in self._buttons(curr_drv):
        #        btn.enable()
        #        btn._name_txt['text'] = ''
        #self.current_drivers_dct[self] = i
        #gprops = self.props.gameprops
        #txt_path = gprops.drivers_img.path_sel
        #self.sel_drv_img.set_texture(self.t_s, loader.loadTexture(txt_path % i))
        #self.widgets[-1]['state'] = DISABLED
        ##self.enable_buttons(False)
        #self.current_drivers += [self]
        #cars = gprops.cars_names[:]
        #car_idx = cars.index(self.mediator.car)
        #cars.remove(self.mediator.car)
        #prev_drv = gprops.drivers_info[car_idx]
        ##gprops.drivers_info[car_idx] = gprops.drivers_info[i]
        #gprops.drivers_info[car_idx].img_idx = i
        ##nname = self.this_name()
        #gprops.drivers_info[car_idx].name = nname
        ##gprops.drivers_info[i] = prev_drv
        #self.evaluate_starting()

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
            #btn._name_txt['text'] = JID(username).bare
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
        self.eng.client.detach(self.on_presence_unavailable_room)
        DriverPageGui.destroy(self)


class DriverPageClientGui(DriverPageGui):

    def __init__(self, mediator, driverpage_props, uid_srv):
        DriverPageGui.__init__(self, mediator, driverpage_props)
        self.srv_usr = uid_srv

    def build(self):
        DriverPageGui.build(self, exit_behav=True)
        self.name['align'] = TextNode.ACenter
        self.name['pos'] = (-.2, .6)
        self.name['text'] += ' ' + self.eng.client.myid
        self.eng.client.register_rpc('drv_request')
        self.eng.client.attach(self.on_drv_selection)
        self.eng.client.attach(self.on_drv_deselection)
        self.eng.client.attach(self.on_start_race)
        self.eng.client.attach(self.on_presence_unavailable_room)

    def this_name(self): return self.eng.client.myid

    def on_presence_unavailable_room(self, uid, room):
        if uid == self.srv_usr:
            self._back_btn.disable()

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
            btn._name_txt['text'] = self.eng.client.myid
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

    def _on_quit(self):
        if self.eng.server.is_active: self.eng.server.stop()
        self.eng.client.register_rpc('leave_curr_room')
        self.eng.client.leave_curr_room()
        DriverPageGui._on_quit(self)

    def destroy(self):
        self.eng.client.detach(self.on_drv_selection)
        self.eng.client.detach(self.on_drv_deselection)
        self.eng.client.detach(self.on_start_race)
        DriverPageGui.destroy(self)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, track, car, driverpage_props):
        self.track = track
        self.car = car
        self.driverpage_props = driverpage_props
        Page.__init__(self, driverpage_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.driverpage_props])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)


class DriverPageSinglePlayer(DriverPage):
    gui_cls = DriverPageSinglePlayerGui


class DriverPageMP(DriverPage):
    gui_cls = DriverPageMPGui

    def __init__(self, track, cars, driverpage_props, nplayers):
        self.track = track
        self.cars = cars
        self.driverpage_props = driverpage_props
        self.nplayers = nplayers
        DriverPage.__init__(self, track, cars, driverpage_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.driverpage_props, self.nplayers])]]


class DriverPageServer(DriverPage):
    gui_cls = DriverPageServerGui


class DriverPageClient(DriverPage):
    gui_cls = DriverPageClientGui

    def __init__(self, track, car, driverpage_props, uid_srv):
        self.__uid_srv = uid_srv
        DriverPage.__init__(self, track, car, driverpage_props)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.driverpage_props, self.__uid_srv])]]
