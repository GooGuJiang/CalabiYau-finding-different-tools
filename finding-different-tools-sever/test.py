import requests

process_url = 'http://127.0.0.1:5000/process'

files = {'file': open('./test.png', 'rb')}
response = requests.post(process_url, files=files)

if response.status_code == 200:
    print(response.json())
else:
    print("Failed to process image.")
