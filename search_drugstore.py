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

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]
org_time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
delta = "0.005"

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "ll": address_ll,
    "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": ",".join([toponym_longitude, toponym_lattitude]) +
          ',pm2rdm' + '~' + "{0},pm2dgl".format(org_point)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

print(f"{org_name} - {org_address}")
print(f"Режим работы: {org_time}")
path = ((((float(toponym_lattitude) - point[1]) * 111.33) ** 2)
        + ((float(toponym_longitude) - point[0]) * 111) ** 2) ** 0.5
print(f"Расстояние от заданного объекта до ближайшей аптеки - {round(path * 1000, 2)}м")

Image.open(BytesIO(
    response.content)).show()
