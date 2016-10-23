from gettext import install, translation
from ..gameobject.gameobject import Colleague


class LangMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.domain = eng.logic.conf.lang_domain
        self.path = eng.logic.conf.lang_path
        self.languages = eng.logic.conf.languages
        self.curr_lang = eng.logic.conf.lang
        self.set_lang(eng.logic.conf.lang)

    @property
    def lang_codes(self):
        return [lang[:2].lower() for lang in self.languages]

    def set_lang(self, lang):
        self.curr_lang = lang
        try:
            lang = translation(self.domain, self.path, languages=[lang])
            lang.install(unicode=1)
        except IOError:
            install(self.domain, self.path, unicode=1)
