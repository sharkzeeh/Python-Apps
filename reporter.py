import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
import datetime
import pickle
import random
from helper import build_dict
from currency_parser import CurrencyParser
from random_articles_gen import random_articles


class Reporter:
    """
    Сравнивает курс нужной валюты какой-то даты с последним завершенным операционным днем
    """

    ARTICLE_DICT = build_dict()
    TODAY = datetime.date.today()

    def __init__(self, day, month, year):
        self.date = datetime.date(year, month, day)
        self.yesterday = Reporter.TODAY - datetime.timedelta(days=1)
        self.same_day = Reporter.TODAY == self.date        

        if self.date >= self.yesterday:
            self.date = self.yesterday
            print("День был изменен на вчерашний. Причина: данных о сегодняшних (и будущих) еще нет...")
            print(f"Данные приведены за {self.yesterday:%d-%m-%Y}")
            
        self.URL = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={self.date:%d/%m/%Y}"
        self.TODAY_URL = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={Reporter.TODAY:%d/%m/%Y}"


    def currency_value_finder(self, code = "USD"):
        self.code = code
        cur_parser = CurrencyParser(self.code)
        self.value = cur_parser.value_parser(self.URL)
        self.value_TODAY = cur_parser.value_parser(self.TODAY_URL)
        return self.value, self.value_TODAY

    def text_builder(self, key, s=''):
        if key not in Reporter.ARTICLE_DICT.keys():
            return s.strip() + "."
        value = Reporter.ARTICLE_DICT[key]
        x = random.randint(1, len(value))
        expr = Counter(value).most_common(x)[x - 1][0]
        s += expr + ' '
        return self.text_builder(expr, s)


    def article(self, key):
        if self.same_day:
            print(f"Для сравнения был выбран текущий день. Последняя стоимость валюты {self.code}: {self.value}")
        else:
            prepositions = ["из-за", "по причине", "в связи", "потому что", "благодаря тому, что", "благодаря"]
            random_prep = random.choice(random.choice(prepositions))
            diff = round(self.value_TODAY - self.value, 4)
            very_beginning = ["Курс ", ""]
            very_end = [f"по сравнению с {self.date}", f"за последние {(self.TODAY - self.date).days} дней"]
            text_gen = lambda ps: f"{random.choice(very_beginning)}{self.code} {random.choice(ps)} на {abs(diff)} {random.choice(very_end)}: {self.text_builder(key)}"
            if diff > 0:
                possible_starts = ["вырос", "увеличился", "поднялся", "взлетел до небес", "укрепился", "повысился"]
                print(text_gen(possible_starts))
            elif not diff:
                print(f"Забавно, но факт: курс {self.code} на {self.date} и {self.TODAY} одинаковый!")
            else:
                possible_starts = ["упал", "уменьшился", "понизился", "скатился", "ослабел", "пошел на убыль"]
                print(text_gen(possible_starts))


def main():
    random_articles()


if __name__ == "__main__":
    main()