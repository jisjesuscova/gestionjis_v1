import streamlit as st
import pandas as pd
from mitosheet.public.v3 import *; register_analysis("id-zzfutnjppm");

# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def eerr():
    df_eerr = conn.query("SELECT Grupo,Cuentas,Supervisor,Sucursal, Meses, Monto FROM QRY_TP_EERR WHERE `Año` = 2023 and Grupo <> '90 - Extras' and Sucursal <>  'Ajuste COQUIMBO'", ttl=600)
    return df_eerr

# Obtener el DataFrame original
df_original = eerr()

# Crear un contenedor para todo el contenido
container = st.container()

with container:
    resultado = df_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
    resultado.loc['Resultado Operacional'] = resultado.sum()
    ingresos = resultado.loc['10 - INGRESOS']

    # Calcular el porcentaje de cada grupo respecto a los ingresos y agregarlo como nuevas columnas
    for mes in ingresos.index:
        resultado[mes + ' %'] = round((resultado[mes] / ingresos[mes]) * 100, 2).apply(lambda x: f'{x:.2f}%')

    # Reordenar las columnas
    column_order = []
    for mes in ingresos.index:
        column_order.append(mes)
        column_order.append(mes + ' %')
    resultado = resultado[column_order]
    resultado = resultado.sort_index()

   

    st.dataframe(resultado, width=0)









