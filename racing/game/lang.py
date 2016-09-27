'''This module contains utilies for managing translations.'''
from gettext import install, translation


class LangMgr(object):
    '''This class defines the manager of translations.'''

    lang_list = ['en', 'it']
    languages = ['English', 'Italiano']

    def __init__(self, domain, path, lang_index):
        self.__domain = domain
        self.__path = path
        install(domain, path, unicode=1)
        lang = self.lang_list[lang_index]
        self.curr_lang = lang
        self.set_lang(lang)

    def set_lang(self, lang):
        '''Setting the current language.'''
        self.curr_lang = lang
        try:
            lang = translation(self.__domain, self.__path, languages=[lang])
            lang.install(unicode=1)
        except IOError:
            install(self.__domain, self.__path, unicode=1)
