import sys
from io import BytesIO
from selection_ll import selective

import requests
from PIL import Image

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}
response = requests.get(geocoder_api_server, params=geocoder_params)
if not response:
    print("Ошибка выполнения запроса:")
    print(geocoder_api_server, geocoder_params)
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)

map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=selective(response))
Image.open(BytesIO(
    response.content)).show()