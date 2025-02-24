import requests
from config import API_TOKEN

def fazerRequisicao(endPoint: str):

    headers = {
        'X-ApiToken': '$2y$10$HELXifyUP8qwr5NbVLF6.OyZun7GyQaq22Np/bodOYp3iKVvTCVia',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url=endPoint, headers=headers)

    # Verifica se a responta foi bem sucedida
    if response.status_code == 200:
        print('Requisição bem-sucedida!')
        return response.json()
    else:
        print(f'Falha na requisição. Status-code: {response.status_code}')
        print(response.text)
        return None