from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.mainpage import MainPage, MainPageGui
from yyagl.engine.gui.page import PageGui
from .singleplayerpage import SingleplayerPage
from .multiplayerpage import MultiplayerPage
from .optionpage import OptionPage
from .creditpage import CreditPage
from direct.gui.OnscreenImage import OnscreenImage
import feedparser
from datetime import datetime, date
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


class YorgMainPageGui(MainPageGui):

    def build_page(self):
        menu_data = [
            ('Single Player', _('Single Player'),
             lambda: self.menu.logic.push_page(SingleplayerPage(self.menu))),
            ('Multiplayer', _('Multiplayer'),
             lambda: self.menu.logic.push_page(MultiplayerPage(self.menu))),
            ('Options', _('Options'),
             lambda: self.menu.logic.push_page(OptionPage(self.menu))),
            ('Credits', _('Credits'),
             lambda: self.menu.logic.push_page(CreditPage(self.menu))),
            ('Quit', _('Quit'),
             lambda: game.fsm.demand('Exit'))]
        menu_gui = self.menu.gui
        self.widgets += [
            DirectButton(text='', pos=(0, 1, .4-i*.28), command=menu[2],
                         **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(self.widgets):
            PageGui.transl_text(wdg, menu_data[i][0], menu_data[i][1])
        if not game.options['development']['multiplayer']:
            self.widgets[-4]['state'] = DISABLED
            _fg = menu_gui.btn_args['text_fg']
            _fc = self.widgets[-4]['frameColor']
            clc = lambda val: max(0, val)
            self.widgets[-4]['text_fg'] = (_fg[0] - .3, _fg[1] - .3, _fg[2] - .3, _fg[3])
            self.widgets[-4]['frameColor'] = (clc(_fc[0] - .3), clc(_fc[1] - .3), clc(_fc[2] - .3), _fc[3])
        self.widgets += [OnscreenImage(
            'assets/images/gui/yorg_title.png',
            scale=(.8, 1, .8 * (380.0 / 772)), parent=base.a2dTopRight,
            pos=(-.8, 1, -.4))]
        self.widgets[-1].setTransparency(True)
        self.set_news()
        MainPageGui.build_page(self)

    def set_news(self):
        feeds = feedparser.parse('http://feeds.feedburner.com/ya2tech?format=xml')
        entries = []
        for feed in feeds['entries']:
            entries += [feed]
        def conv(datestr):
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                      'Sep', 'Oct', 'Nov', 'Dec']
            date_el = datestr.split()[1:-2]
            day, month, year = date_el[0], months.index(date_el[1]) + 1, date_el[2]
            return datetime(int(year), month, int(day))
        rss = sorted(entries, key=lambda entry: conv(entry['published']))
        rss = [(datetime.strftime(conv(ent['published']), '%b %d'), ent['title']) for ent in rss]
        rss.reverse()
        rss = rss[:5]
        def conv_str(_str):
            if len(_str) <=20:
                return _str
            else:
                return _str[:20] + '...'
        if not rss:
            return
        rss = [(_rss[0], conv_str(_rss[1])) for _rss in rss]
        frm = DirectFrame(frameSize=(0, 1.0, 0, .75), frameColor=(.2, .2, .2, .5), pos=(.05, 1, .1), parent=base.a2dBottomLeft)
        texts = []
        txt = OnscreenText(_('Last news:'), pos=(.55, .75), scale=.055, wordwrap=32, parent=base.a2dBottomLeft,
            fg=(.75, .75, .75, 1), font=eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'))
        texts += [txt]
        for i in range(5):
            txt = OnscreenText(': '.join(rss[i]), pos=(.1, .65 - i*.1), scale=.055, wordwrap=32, parent=base.a2dBottomLeft, align=TextNode.A_left,
                fg=(.75, .75, .75, 1), font=eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'))
            texts += [txt]
        menu_gui = self.menu.gui
        btn_args = menu_gui.btn_args.copy()
        btn_args['scale'] = .055
        btn = DirectButton(text=_('show'), pos=(.55, 1, .15), command=eng.gui.open_browser, extraArgs=['http://www.ya2.it'],
                           parent=base.a2dBottomLeft, **btn_args)
        self.widgets += [frm] + texts + [btn]


class YorgMainPage(MainPage):
    gui_cls = YorgMainPageGui
