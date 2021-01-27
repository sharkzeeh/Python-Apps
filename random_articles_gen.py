from reporter import Reporter
from currency_parser import CurrencyParser
import random

def random_articles():
    for _ in range(10):
        d, m, y = random.randint(1, 31), random.randint(1,12), random.randint(2000, 2020)

        try:
            r = Reporter(day=d, month=m, year=y)
            r.currency_value_finder("USD")
            r.article("доллар")
        except ValueError:
            d = random.randint(1,28)
            r = Reporter(day=d, month=m, year=y)
            r.currency_value_finder("USD")
            r.article("доллар")