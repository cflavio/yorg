from gettext import install, translation


class LangMgr(object):

    lang_list = ['en', 'it']
    languages = ['English', 'Italiano']

    def __init__(self, domain, path, lang_index):
        self.__domain = domain
        self.__path = path
        install(domain, path, unicode=1)
        self.set_lang(self.lang_list[lang_index])

    def set_lang(self, lang):
        self.curr_lang = lang
        try:
            lang = translation(self.__domain, self.__path, languages=[lang])
            lang.install(unicode=1)
        except IOError:
            install(self.__domain, self.__path, unicode=1)
