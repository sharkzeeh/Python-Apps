from pymongo import MongoClient, GEO2D
import re
import json
import urllib.request
import pprint
from last_name_search import last_name_search
from bson.objectid import ObjectId

client = MongoClient()
db = client.gc
mus = db.subj

printer = pprint.PrettyPrinter(indent=4)

class Tourist:

    CONTACT = "https://goskatalog.ru/muzfo-rest/rest/museums/"
    ALL_COOR = {}

    def __init__(self, pattern):
        self.pattern = last_name_search(pattern)
        self.EXH, self.COOR = {}, {}

    @classmethod
    def build_missing_coors(cls, file="geo.txt"):
        """
        дополняет словарь координат
        отстуствующему на госкаталоге данными
        о локации музеев
        """
        with open(file) as fh:
            for row in fh:
                row = row.split(':')
                id, (lat, long) = int(row[0]), [float(val) for val in row[1].split()]
                cls.ALL_COOR[id] = (lat, long)

    def coor_parser(self, museum_id, address):
        """
        находит координаты музея
        """
        lat, long = None, None
        try:
            lat, long = address["latitude"], address["longitude"]
            if museum_id not in self.COOR:
                self.COOR[museum_id] = (lat, long)
                self.__class__.ALL_COOR[museum_id] = (lat, long)
        except:
            Tourist.build_missing_coors()
            self.COOR[museum_id] = Tourist.ALL_COOR[id]

    def town_parser(self, address):
        """
        находит в каком городе находится музей
        возвращает: объект, который затем проверяется нулевой ли он
        """
        town_pattern = re.compile(r'(?<=,)?([а-я\s])*[а-я-]+(?= ([пгс]|рп))', re.I)
        search_1 = lambda x, n: re.search(town_pattern, address["contacts"][n][x])
        search_2 = lambda x, y, n: re.search(town_pattern, address["contacts"][n][x][y])
        loc = search_1('contactValue', 0) or search_1('contactValue', 1) or \
                search_2('contactDetails', 'townName', 0) or search_2('contactDetails', 'townName', 1)
        return loc

    def mus_exhib(self):
        """
        построение словаря следующей структуры:
        { город / поселок / село: { музеи: [экспонаты] }}

        где кол-во экспонатов не более 3х

        таким образом релевантная нужная пользователю тема
        классифицируется по регионам, и можно из этой структуры
        доставать, например, музеи А.С. Пушкина конкретно в Москве
        """
        cursor = mus.find({"$text": {"$search": self.pattern}})

        for item in cursor:
            exh = item["data"]
            exh_name = exh["name"]
            mus_data = exh["museum"]
            mus_id = mus_data["id"]
            mus_name = mus_data["name"]
            address = json.loads(urllib.request.urlopen(Tourist.CONTACT + str(mus_id)).read().decode('utf-8'))

            self.coor_parser(mus_id, address)
            loc = self.town_parser(address)
            if not loc: continue
            loc = loc.group(0).strip()

            if loc not in self.EXH:
                self.EXH[loc] = {mus_id: (mus_name, [exh_name])}
            else:
                if mus_id not in self.EXH[loc]:
                    self.EXH[loc][mus_id] = (mus_name, [exh_name])
                else:
                    cur_mus_exhibits = self.EXH[loc][mus_id][1]
                    if len(cur_mus_exhibits) < 3:
                        cur_mus_exhibits.append(exh_name)
        return self

    @staticmethod
    def build_geo_index():
        mus.create_index([("loc", GEO2D)])

    def fill_geo(self):
        """
        заполнение релевантных мест для посещения
        """
        result = mus.insert_many([{"loc": list(self.COOR[key])} for key in self.COOR])
        self.MATCH = dict(zip(result.inserted_ids, self.COOR.keys()))
        print(self.MATCH)


    def find_nearby_helper(self, cur_loc):
        for k in self.EXH:
            try:
                place = self.EXH[k]
                mus_name_to_visit = place[Tourist.swap_coor_dict()[tuple(cur_loc)]][0]
                print(f"Музей: {mus_name_to_visit}. Место нахождения: {k}")
            except KeyError:
                ...

    def find_nearby(self, max_places_to_visit=100):
        """
        находит ближайшие координаты релеватных экспонатов
        """
        first = tuple(self.COOR.values())[0] # рандомный музей из найденных
        print(f"По запросу {self.pattern} найдены следующие результаты:")
        
        seen_first = False
        for doc in mus.find({"loc": {"$near": first}}).limit(max_places_to_visit):
            str_obj = doc["_id"]
            cur_loc = tuple(mus.find_one({"_id": ObjectId(str_obj)})["loc"])
            if not seen_first:
                self.find_nearby_helper(cur_loc)
                seen_first = True
            elif cur_loc != first: # не хотим выдавать тот же музей несколько раз
                self.find_nearby_helper(cur_loc)

    @classmethod
    def swap_coor_dict(cls):
        return dict(zip(cls.ALL_COOR.values(), cls.ALL_COOR.keys()))