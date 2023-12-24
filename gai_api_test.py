import json
import os
import time
import base64
import requests

API_KEY = '062D3C684821E0A1E590ACEEE994B87B'
SECRET_KEY = '0880617EF1F81E43312434FBFF7376E3'

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)




def save_as_image(data: str, filename: str):
    data_64b = data.encode("ascii")
    data_b = base64.b64decode(data_64b)

    with open(filename+'.png', 'wb') as f:
        f.write(data_b)
        print('Saved to file')

    # sample_string = sample_string_bytes.decode("ascii")
    # print(f"Decoded string: {sample_string}")


def get_image(prompt: str):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', API_KEY, SECRET_KEY)
    model_id = api.get_model()
    # print('Start generation')
    uuid = api.generate(prompt, model_id)
    images = api.check_generation(uuid)
    filename = prompt

    # print('Get data, saving to file')
    save_as_image(images[0], filename)


if __name__ == '__main__':
    loc_str = 'Отель, Университет, Банк, Больница, Посольство, Киностудия, Цирк-шапито, Театр, Церковь, Овощебаза, Супермаркет, Полицейский участок, Корпоративная вечеринка, Океанский лайнер, Подводная лодка, Станция техобслуживания, Полярная станция, Пляж, Воинская часть, Войско крестоносцев, Пассажирский поезд, Школа, База террористов, Партизанский отряд, Казино, Пиратский корабль, Орбитальная станция, Самолёт'
    loc_filename = 'Hotel, University, Bank, Hospital, Embassy, Studio, Shapito circus, Theater, Church, Vegetable base, Supermarket, Police station, Corporate party, Ocean liner, Submarine, Service station, Polar station, Beach, Military unit, Crusader army, Passenger train, School, Terrorist base, Partisan detachment, Casino, Pirate ship, Orbital station, Airplane'
    loc_list = loc_str.split(', ')
    file_list = loc_filename.split(', ')
    i = -1
    for loc in loc_list:
        i += 1
        progress = int(i/len(loc_list)*100)
        print(f'{i} {progress}% {loc} -> {file_list[i]}')
        # get_image(loc)

        os.rename('pics\\'+loc+'.png', 'pics\\'+file_list[i].lower()+'.png')


#Не забудьте указать именно ваш YOUR_KEY и YOUR_SECRET.