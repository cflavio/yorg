from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.imgbtn import ImageButton


class Results(object):

    def __init__(self):
        self.__res_txts = None
        self.__buttons = None
        self.result_img = None

    def show(self, race_ranking):
        track = game.track.path
        self.result_img = OnscreenImage(image='assets/images/gui/results.png',
                                        scale=(.8, 1, .8))
        self.result_img.setTransparency(True)
        # race object invokes this
        laps = len(game.player_car.logic.lap_times)
        pars = {'scale': .1, 'fg': (.75, .75, .75, 1),
                'font': eng.font_mgr.load_font('assets/fonts/zekton rg.ttf')}
        self.__res_txts = [OnscreenText(
            str(game.player_car.logic.lap_times[i]),
            pos=(.3, - .2 * i), **pars)
            for i in range(laps)]
        self.__res_txts += [OnscreenText(_('LAP'), pos=(-.3, .35), **pars)
                            for i in range(4)]
        self.__res_txts += [
            OnscreenText(str(i), pos=(-.3, .2 - .2 * i), **pars)
            for i in range(1, 4)]
        self.__res_txts += [
            OnscreenText(_('share:'), pos=(-.1, -.65), align=TextNode.A_right,
                         **pars)]
        self.__buttons = []

        curr_time = min(game.player_car.logic.lap_times or [0])
        facebook_url = \
            'https://www.facebook.com/sharer/sharer.php?u=ya2.it/yorg'
        #TODO: find a way to share the time on Facebook
        twitter_url = 'https://twitter.com/share?text=' + \
            'I%27ve%20achieved%20{time}%20in%20the%20{track}%20track%20on' + \
            '%20Yorg%20by%20%40ya2tech%21&hashtags=yorg'
        twitter_url = twitter_url.format(time=curr_time, track=track)
        plus_url = 'https://plus.google.com/share?url=ya2.it/yorg'
        #TODO: find a way to share the time on Google Plus
        tumblr_url = 'https://www.tumblr.com/widgets/share/tool?url=ya2.it'
        #TODO: find a way to share the time on Tumblr
        sites = [('facebook', facebook_url), ('twitter', twitter_url),
                 ('google_plus', plus_url), ('tumblr', tumblr_url)]
        self.__buttons += [
            ImageButton(
                scale=.1,
                pos=(.02 + i*.15, 1, -.62), frameColor=(0, 0, 0, 0),
                image='assets/images/icons/%s_png.png' % site[0],
                command=eng.gui.open_browser, extraArgs=[site[1]],
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, site in enumerate(sites)]

        def step():
            map(lambda txt: txt.destroy(), self.__res_txts)
            map(lambda btn: btn.destroy(), self.__buttons)
            self.result_img.destroy()
            #TODO: notify and manage into yorg's fsm
            ranking = game.logic.season.logic.ranking
            from racing.season.season import SingleRaceSeason
            if game.logic.season.__class__ != SingleRaceSeason:
                for car in ranking.logic.ranking:
                    ranking.logic.ranking[car] += race_ranking[car]
                game.options['save']['ranking'] = ranking.logic.ranking
                game.options.store()
                game.fsm.demand('Ranking')
            else:
                game.fsm.demand('Menu')
        taskMgr.doMethodLater(10.0, lambda tsk: step(), 'step')

    def destroy(self):
        pass
