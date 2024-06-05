import requests
import threading
import time
from flask import Flask, request, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Конфігурація API
API_URL = os.getenv('API_URL')
API_TOKEN = os.getenv('API_TOKEN')
API_HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Глобальна змінна для зберігання даних
data_cache = None
last_update_time = None  # змінна для зберігання часу останнього оновлення

# Мапінг областей англійською мовою
regions = [
    "Crimea", "Volyn", "Vinnytsia", "Dnipro", "Donetsk",
    "Zhytomyr", "Zakarpattia", "Zaporizhzhia", "Ivano-Frankivsk", "Kyiv City",
    "Kyiv", "Kirovohrad", "Luhansk", "Lviv", "Mykolaiv",
    "Odesa", "Poltava", "Rivne", "Sevastopol", "Sumy",
    "Ternopil", "Kharkiv", "Kherson", "Khmelnytskyi",
    "Cherkasy", "Chernivtsi", "Chernihiv"
]

def get_data_from_api():
    global data_cache, last_update_time
    try:
        response = requests.get(API_URL, headers=API_HEADERS)
        if response.status_code == 200:
            data_cache = response.text
            last_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Оновити час останнього оновлення
            print(f'[WEB] API request made at {last_update_time}')
        else:
            print(f'Failed to fetch data from API: {response.status_code}')
    except Exception as e:
        print(f'Exception while fetching data from API: {e}')

def periodic_data_update(interval):
    while True:
        get_data_from_api()
        time.sleep(interval)

@app.route('/get_value', methods=['GET'])
def get_value():
    device_id = request.args.get('id')
    if not device_id:
        return jsonify({'error': 'ID is required'}), 400

    if data_cache is None:
        return jsonify({'error': 'Data not available'}), 503

    try:
        device_id = int(device_id)
    except ValueError:
        return jsonify({'error': 'ID must be an integer'}), 400

    if device_id <= 0 or device_id > len(data_cache):
        return jsonify({'error': 'Invalid data or ID out of range'}), 400

    # Отримати відповідний символ
    value = data_cache[device_id]
    region = regions[device_id - 1]

    return jsonify({'value': value, 'obl': region, 'updateTime': last_update_time})

if __name__ == '__main__':
    # Запуск фонового потоку для оновлення даних
    update_interval = 10  # інтервал у секундах
    data_update_thread = threading.Thread(target=periodic_data_update, args=(update_interval,))
    data_update_thread.daemon = True
    data_update_thread.start()

    app.run(host='0.0.0.0', port=80)
