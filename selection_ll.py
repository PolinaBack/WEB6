import requests

def selective(response):
    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    koords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["boundedBy"]["Envelope"]
    str_koords = (koords["upperCorner"] + '~' + koords["lowerCorner"]).replace(' ', ',')
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "bbox": str_koords,
        "l": "map",
        "pt": (",".join([toponym_longitude, toponym_lattitude]) + ',pm2rdm')
    }
    return map_params