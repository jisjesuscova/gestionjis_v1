import requests

# Crear una sesión
session = requests.Session()

url = 'https://apijis.azurewebsites.net/login_users/token'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'grant_type': '',
    'username': '27141399',
    'password': '123456',
    'scope': '',
    'client_id': '',
    'client_secret': ''
}

response = session.post(url, headers=headers, data=data)

if response.status_code == 200:
    # Cargar la respuesta en una variable de sesión
    session_response = response.json()
    print("Solicitud exitosa:")
    print(session_response)
    
    # Ahora, puedes almacenar cada valor en una variable separada
    access_token = session_response.get('access_token', '')
    rut = session_response.get('rut', 0)
    visual_rut = session_response.get('visual_rut', '')
    rol_id = session_response.get('rol_id', 0)
    nickname = session_response.get('nickname', '')
    token_type = session_response.get('token_type', '')
    
    # Puedes acceder a estas variables en cualquier momento durante la sesión.

else:
    print(f"Error en la solicitud: {response.status_code} - {response.text}")

# Cierra la sesión al final, si es necesario
session.close()