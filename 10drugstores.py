import json
import sys
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image

toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}
response1 = requests.get(geocoder_api_server, params=geocoder_params)

# Преобразуем ответ в json-объект
json_response1 = response1.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response1["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

koords = toponym["boundedBy"]["Envelope"]
str_koords = (koords["upperCorner"] + '~' + koords["lowerCorner"]).replace(' ', ',')

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = ','.join((toponym["Point"]["pos"]).split(' '))

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)


# Преобразуем ответ в json-объект
json_response = response.json()
with open('temp.json', 'w', encoding="utf-8") as temp_file:
    json.dump(json_response, temp_file, ensure_ascii=False)


markers = []
for i in range(10):
    organization = json_response["features"][i]
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    org_time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
    if 'круглосуточно' in org_time:
        a = "{0},pm2dgl".format(org_point)
    elif '-' in org_time or ':' in org_time:
        a = "{0},pm2dbl".format(org_point)
    else:
        a = "{0},pm2grl".format(org_point)
    markers.append(a)

delta = "0.015"

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "ll": address_ll,
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": '~'.join(markers)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()