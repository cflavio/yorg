'''This module contains utilies for managing translations.'''
from gettext import install, translation


class LangMgr(object):
    '''This class defines the manager of translations.'''

    def __init__(self, domain, path, languages, lang_code=None):
        self.domain = domain
        self.path = path
        self.languages = languages
        install(domain, path, unicode=1)
        lang = lang_code if lang_code else self.languages[0][:2].lower()
        self.curr_lang = lang
        self.set_lang(lang)

    @property
    def lang_codes(self):
        '''The codes of the supported languages.'''
        return [lang[:2].lower() for lang in self.languages]

    def set_lang(self, lang):
        '''Setting the current language.'''
        self.curr_lang = lang
        try:
            lang = translation(self.domain, self.path, languages=[lang])
            lang.install(unicode=1)
        except IOError:
            install(self.domain, self.path, unicode=1)
