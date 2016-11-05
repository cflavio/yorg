from direct.gui.OnscreenText import OnscreenText
from racing.game.gameobject import Gui


class RankingGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.ranking_texts = []

    def show(self):
        items = self.mdt.logic.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        font = eng.font_mgr.load_font('assets/fonts/zekton rg.ttf')
        self.ranking_texts = []
        for i, (name, score) in enumerate(sorted_ranking):
            txt = OnscreenText(
                '%s %s' % (name, score), pos=(0, .5 - .2 * i), font=font,
                fg=(.75, .75, .75, 1), scale=.12)
            self.ranking_texts += [txt]
        taskMgr.doMethodLater(10, lambda task: self.mdt.logic.step(), 'step')

    def destroy(self):
        Gui.destroy(self)
        map(lambda txt: txt.destroy(), self.ranking_texts)
