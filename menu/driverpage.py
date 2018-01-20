from itertools import product
from random import shuffle
from panda3d.core import TextureStage, Texture, PNMImage, TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectEntry import DirectEntry
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGuiGlobals import DISABLED
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
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

    def __init__(self, mdt, driverpage_props):
        self.props = driverpage_props
        self.sel_drv_img = None
        ThanksPageGui.__init__(self, mdt, driverpage_props.gameprops.menu_args)

    def bld_page(self):
        self.drv_info = self.props.gameprops.drivers_info
        menu_args = self.menu_args
        widgets = [OnscreenText(text=_('Select the driver'), pos=(-.2, .8),
                                **menu_args.text_args)]
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        name = OnscreenText(_('Write your name:'), pos=(-.3, .6), scale=.06,
                            align=TextNode.A_right, **t_a)
        self.ent = DirectEntry(
            scale=.08, pos=(-.2, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText=self.props.gameprops.player_name or _('your name'))
        self.ent.onscreenText['fg'] = menu_args.text_active
        self.drivers = []
        for row, col in product(range(2), range(4)):
            idx = col + row * 4
            drv_btn = ImgBtn(
                scale=.24, pos=(-.95 + col * .5, 1, .25 - row * .5),
                frameColor=(0, 0, 0, 0),
                image=self.props.gameprops.drivers_img[0] % idx,
                command=self.on_click, extraArgs=[idx],
                **self.menu_args.imgbtn_args)
            widgets += [drv_btn]
            self.drivers += [widgets[-1]]
            sign = lambda pos_x: '\1green\1+\2' if pos_x > 0 else ''
            psign = lambda pos_x, sgn=sign: '+' if pos_x == 0 else sgn(pos_x)

            def ppcol(x):
                return '\1green\1%s\2' % x if x > 0 else '\1red\1%s\2' % x
            pcol = lambda x: x if x == 0 else ppcol(x)
            lab_lst = [(_('adherence'), .04), (_('speed'), .16),
                       (_('stability'), .1)]
            widgets += map(
                lambda lab_def: self.__add_lab(*(lab_def + (row, col))),
                lab_lst)
            txt_lst = [(self.drv_info[idx - 1].adherence, .04),
                       (self.drv_info[idx - 1].speed, .16),
                       (self.drv_info[idx - 1].stability, .1)]
            widgets += map(
                lambda txt_def: self.__add_txt(
                    *txt_def + (psign, pcol, col, row)),
                txt_lst)
        self.sel_drv_img = OnscreenImage(
            self.props.gameprops.cars_img % self.mdt.car,
            parent=base.a2dBottomRight, pos=(-.38, 1, .38), scale=.32)
        widgets += [self.sel_drv_img, name, self.ent]
        map(self.add_widget, widgets)
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
        ThanksPageGui.bld_page(self)
        self.update_tsk = taskMgr.add(self.update_text, 'update text')
        self.enable_buttons(False)

    def __add_lab(self, txt, pos_z, row, col):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return OnscreenText(
            txt + ':', pos=(-1.15 + col * .5, pos_z - row * .5),
            scale=.046, align=TextNode.A_left, **t_a)

    def __add_txt(self, val, pos_z, psign, pcol, col, row):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return OnscreenText(
            '%s%s%%' % (psign(val), pcol(val)),
            pos=(-.75 + col * .5, pos_z - row * .5), scale=.052,
            align=TextNode.A_right, **t_a)

    def enable_buttons(self, enable):
        [(drv.enable if enable else drv.disable)() for drv in self.drivers]

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

    def on_click(self, i):
        self.eng.log('selected driver ' + str(i))
        gprops = self.props.gameprops
        txt_path = gprops.drivers_img.path_sel
        self.sel_drv_img.setTexture(self.t_s, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        cars = gprops.cars_names[:]
        car_idx = cars.index(self.mdt.car)
        cars.remove(self.mdt.car)
        shuffle(cars)
        drv_idx = range(8)
        drv_idx.remove(i)
        shuffle(drv_idx)
        gprops.drivers_info[car_idx] = gprops.drivers_info[i]._replace(
            img_idx=i)
        nname = self.ent.get()
        gprops.drivers_info[car_idx] = gprops.drivers_info[i]._replace(
            name=nname)
        gprops.drivers_info[i] = gprops.drivers_info[i]._replace(
            img_idx=car_idx)
        self.eng.log('drivers: ' + str(gprops.drivers_info))
        self.notify('on_driver_selected', self.ent.get(), self.mdt.track,
                    self.mdt.car)

    def destroy(self):
        self.sel_drv_img = None
        taskMgr.remove(self.update_tsk)
        PageGui.destroy(self)


class DriverPageServerGui(DriverPageGui):

    def bld_page(self):
        DriverPageGui.bld_page(self)
        self.eng.server.register_cb(self.process_srv)
        self.current_drivers = []

    def on_click(self, i):
        self.eng.log('selected driver ' + str(i))
        gprops = self.props.gameprops
        txt_path = gprops.drivers_img.path_sel
        self.sel_drv_img.setTexture(self.t_s, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        self.current_drivers += [self]
        cars = gprops.cars_names[:]
        car_idx = cars.index(self.mdt.car)
        cars.remove(self.mdt.car)
        shuffle(cars)
        drv_idx = range(8)
        drv_idx.remove(i)
        shuffle(drv_idx)
        gprops.drivers_info[car_idx] = gprops.drivers_info[i]._replace(
            img_idx=i)
        nname = self.ent.get()
        gprops.drivers_info[car_idx] = gprops.drivers_info[i]._replace(
            name=nname)
        gprops.drivers_info[i] = gprops.drivers_info[i]._replace(
            img_idx=car_idx)
        self.evaluate_starting()

    def evaluate_starting(self):
        connections = [conn[0] for conn in self.eng.server.connections]
        connections += [self]
        if not all(conn in self.current_drivers for conn in connections):
            return
        packet = [NetMsgs.start_race, len(self.current_drivers)]

        def process(k):
            '''Processes a car.'''
            return 'server' if k == self else k.get_address().get_ip_string()
        gprops = self.props.gameprops
        for i, k in enumerate(self.current_drivers):
            packet += [process(k), gprops.cars_names[i],
                       self.props.gameprops.drivers_info[i].name]
        self.eng.server.send(packet)
        self.eng.log_mgr.log('start race: ' + str(packet))
        self.eng.log('drivers: ' + str(gprops.drivers_info))
        self.notify(
            'on_driver_selected_server', self.ent.get(), self.mdt.track,
            self.mdt.car, gprops.cars_names[:len(self.current_drivers)],
            packet)

    def process_srv(self, data_lst, sender):
        if data_lst[0] != NetMsgs.driver_selection: return
        self.current_drivers += [sender]
        car = data_lst[1]
        driver_name = data_lst[2]
        driver_id = data_lst[3]
        driver_speed = data_lst[4]
        driver_adherence = data_lst[5]
        driver_stability = data_lst[6]
        self.eng.log_mgr.log(
            'driver selected: %s (%s, %s) ' % (driver_name, driver_id, car))
        gprops = self.props.gameprops
        cars = gprops.cars_names[:]
        car_idx = cars.index(car)
        gprops.drivers_info[car_idx] = gprops.drivers_info[car_idx]._replace(
            img_idx=driver_id)
        gprops.drivers_info[car_idx] = gprops.drivers_info[car_idx]._replace(
            name=driver_name)
        gprops.drivers_info[car_idx] = gprops.drivers_info[car_idx]._replace(
            speed=driver_speed)
        gprops.drivers_info[car_idx] = gprops.drivers_info[car_idx]._replace(
            adherence=driver_adherence)
        gprops.drivers_info[car_idx] = gprops.drivers_info[car_idx]._replace(
            stability=driver_stability)
        self.evaluate_starting()


class DriverPageClientGui(DriverPageGui):

    def bld_page(self):
        DriverPageGui.bld_page(self)
        self.eng.client.register_cb(self.process_client)

    def on_click(self, i):
        self.eng.log('selected driver ' + str(i))
        gprops = self.props.gameprops
        txt_path = gprops.drivers_img.path_sel
        self.sel_drv_img.setTexture(self.t_s, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        self.eng.client.send([
            NetMsgs.driver_selection, self.mdt.car, self.ent.get(), i,
            gprops.drivers_info[i].speed, gprops.drivers_info[i].adherence,
            gprops.drivers_info[i].stability, self.eng.client.my_addr])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            self.eng.log_mgr.log('start_race: ' + str(data_lst))
            self.notify('on_car_start_client', self.mdt.track, self.mdt.car,
                        [self.mdt.car], data_lst)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, track, car, driverpage_props):
        self.track = track
        self.car = car
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, driverpage_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)


class DriverPageServer(DriverPage):
    gui_cls = DriverPageServerGui


class DriverPageClient(DriverPage):
    gui_cls = DriverPageClientGui
