import streamlit as st
import pandas as pd
import os

st.title("CARGA TARIFAS DE TRANSBANK")
st.markdown("---")

# Lista para almacenar los DataFrames de cada archivo CSV
dataframes = []

# Ruta a la carpeta que contiene los archivos CSV
folder_path = "data/transbank/"

# Obtener la lista de archivos CSV en la carpeta
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
for csv_file in csv_files:
    csv_path = os.path.join(folder_path, csv_file)
    df = pd.read_csv(csv_path, sep=",")
    dataframes.append(df)

# Unir los DataFrames en uno solo
merged_df = pd.concat(dataframes, ignore_index=True)

# Mostrar el DataFrame combinado
st.write(merged_df)


