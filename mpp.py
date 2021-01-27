from utils.msdocx import *
from utils.web import *
from sly import Lexer, Parser

class LLexer(Lexer):

    def __init__(self):
        self.doc = Docx(doc_name=None)
        self.insta = InstaLoad()

    tokens = {PLUS, ALL, IMAGE, FOLDER, COLON, URL, A4, SAVE, FILENAME, MODULE, LANDSCAPE}
    ignore = '\t '

    ALL = r'ALL'
    URL = r"https://[^\s]+"


    FILENAME=  r"\w+\.docx$"
    @_(r'FILENAME')
    def FILENAME(self, t):
        self.doc.doc_name = t.value
        return t

    FOLDER = r'[a-z_0-9.]{1,30}'
    @_(r'FOLDER')
    def FOLDER(self, t):
        self.doc.user_folder = t.value
        self.doc.insert_images()
        ...
        
    MODULE = rf"\[{Docx.MNAME}\]"

    LANDSCAPE = r'LANDSCAPE'
    @_(r'LANDSCAPE')
    def LANDSCAPE(self, t):
        self.doc.change_to_landscape()
        return t
    
    @_(r'MODULE')
    def MODULE(self, t):
        return t

    @_(r'URL')
    def URL(self, t):
        obj = InstaLoad(url=t.value)
        asyncio.run(obj.downloader())
        return t

    COLON = r":"
    @_(r'COLON')
    def COLON(self, t):
        return t

    @_(r'LANDSCAPE')
    def LANDSCAPE(self, t):
        return t

    @_(r"A4")
    def A4(self, t):
        self.doc.add_single_page()
        return t

    @_("SAVE")
    def SAVE(self, t):
        self.doc.save_as()
        return t

    @_(r'#.*')
    def COMMENT(self, t):
        pass

    PLUS = r"\+"
    @_(r'PLUS')
    def PLUS(self, t):
        return t

    IMAGE = r'IMAGE'

    def error(self, t):
        print(f"illegal character {t.value[0]}")
        self.index += 1

class PParser(Parser):

    tokens = LLexer.tokens
    
    def __init__(self):
        self.env = {}

    @_('')
    def statement(self, p):
        pass

    @_(r'URL')
    def statement(self, p):
        ...
    
    @_(r'MODULE')
    def statement(self, p):            
        return p
        
    @_(r'A4')
    def statement(self, p):
        return p
    
    @_(r'SAVE')
    def statement(self, p):
        ...
    
    @_(r'FOLDER')
    def statement(self, p):
        ...

    @_(r'FILENAME')
    def statement(self, p):
        ...
    
    @_(r'LANDSCAPE')
    def statement(self, p):
        return p.LANDSCAPE
    
    @_(r'ALL')
    def statement(self, p):
        ...

    @_(r'PLUS')
    def statement(self, p):
        ...
    @_(r'IMAGE')
    def statement(self, p):
        ...
    @_(r'COLON')
    def statement(self, p):
        ...  

    @_(r'MODULE PLUS FILENAME')
    def statement(self, p):
        return p.FILENAME
    
    @_(r'MODULE PLUS A4')
    def statement(self, p):
        return p.A4
    
    @_(r'MODULE SAVE')
    def statement(self, p):
        return p.SAVE

    @_(r'ALL FOLDER COLON MODULE PLUS IMAGE')
    def statement(self, p):
        return p.FOLDER

        
if __name__ == '__main__':
    lexer = LLexer()
    parser = PParser()
    while True:
        try:
            text = input('mpp ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))
