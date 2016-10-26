from direct.gui.DirectButton import DirectButton
from racing.game.engine.gui.page import Page, PageGui
from .carpage import CarPage
from .netmsgs import NetMsgs


class TrackPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args

        def on_track(track):
            self.menu.track = track
            self.menu.logic.push_page(CarPage(self.menu))
            # TrackPageGuiServer
            if eng.server.is_active:
                eng.server.send([NetMsgs.track_selected, track])
        menu_data = [
            ('Desert', on_track, ['desert']),
            ('Prototype', on_track, ['prototype'])]
        self.widgets += [
            DirectButton(text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                         extraArgs=menu[2], **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        PageGui.build_page(self)

    def destroy(self):
        del self.menu.track
        PageGui.destroy(self)


class TrackPage(Page):
    gui_cls = TrackPageGui
