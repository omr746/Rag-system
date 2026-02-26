import os

class TemplateParser:
    def __init__(self,lang:str=None,default_lang='en'):
        self.current_path=os.path.dirname(os.path.abspath(__file__))
        self.default_lang=default_lang
        self.lang=None
        self.set_lang(lang=lang)
    def set_lang(self,lang:str):
        lang_path=os.path.join(self.current_path,"locales",lang)
        if lang and os.path.exists(lang_path):
            self.lang=lang
        else:
            self.lang=self.default_lang
    def get(self,group:str,key:str,vars:dict={}):
        if not group or not key:
            return None


