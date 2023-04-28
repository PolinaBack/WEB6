import json
import sys
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт
from selection_ll import selective
from distance import lonlat_distance

import requests
from PIL import Image

toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}
response1 = requests.get(geocoder_api_server, params=geocoder_params)

select_map_params = selective(response1)

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": select_map_params['ll'],
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
    "ll": select_map_params['ll'],
    "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": select_map_params['pt'] + '~' + "{0},pm2dgl".format(org_point)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

print(f"{org_name} - {org_address}")
print(f"Режим работы: {org_time}")

print(f"Расстояние от заданного объекта до ближайшей аптеки - "
      f"{lonlat_distance((float(select_map_params['ll'].split(',')[0]), (float(select_map_params['ll'].split(',')[1]))), point)}м")

Image.open(BytesIO(
    response.content)).show()
