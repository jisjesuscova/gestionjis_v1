import streamlit as st
import requests
import json

BASE_URL = 'https://apijis.com/login_users/token'

def obtener_usuarios(rut, contrasena):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': '',
        'username': rut,
        'password': contrasena,
        'scope': '',
        'client_id': '',
        'client_secret': ''
    }
    response = requests.post(BASE_URL,headers=headers, data= data)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def validar_credenciales(rut, contrasena):
    usuarios = obtener_usuarios(rut, contrasena)

    if str(usuarios['rut']) == rut:
        return usuarios
    else:
        return None

def main():
    st.title("Inicio de Sesión")

    rut = st.text_input("RUT")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if rut and contrasena:
            usuario = validar_credenciales(rut, contrasena)
            if usuario is not None and "access_token" in usuario:
                st.success("Inicio de sesión exitoso!")
                st.write(f"Bienvenido, {usuario['rol_id']}")

                import app2
                app2.main()


                # Simulamos guardar el token en la sesión
                st.session_state.token = usuario['access_token']

                st.write("Página de bienvenida:")
                st.write("Aquí puedes mostrar contenido exclusivo para usuarios autenticados.")
            else:
                st.error("Credenciales inválidas. No tienes permiso para ingresar.")

if __name__ == "__main__":
    main()



