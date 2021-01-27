import urllib.request
import xml.etree.ElementTree as ET

class CurrencyParser:

    def __init__(self, code='USD'):
        self.code = code

    def value_parser(self, url):
        contents = urllib.request.urlopen(url)
        root = ET.fromstringlist(contents.read().decode('ISO-8859-4'))
        parser = lambda tag: [child.text for child in root.iter(tag)]
        codes, values = parser("CharCode"), parser("Value")
        return float(dict(zip(codes,values))[self.code].replace(',','.'))