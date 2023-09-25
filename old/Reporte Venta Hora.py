import streamlit as st
import pandas as pd
import numpy as np
import locale
from sqlalchemy import create_engine, text
import datetime
import plotly.graph_objs as go
import plotly.express as px


# Configuración de la conexión a la base de datos utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://jysparki_jis:Jis2020!@103.72.78.28/jysparki_jis') 

st.header("Reporte de Venta por Hora") 

# Crear la consulta con la sintaxis de SQLAlchemy y obtener los resultados como un DataFrame de Pandas
query_actual = text("""
SELECT
	api_transactions.branch_office_id, 
	api_transactions.cashier_id, 
	cashiers.cashier, 
	QRY_BRANCH_OFFICES.branch_office,  
	api_transactions.folio, 
	api_transactions.total*1 as total, 
	api_transactions.entrance_hour, 
	api_transactions.exit_hour,
	HOUR(api_transactions.exit_hour) AS hora,
	DATE_FORMAT(api_transactions.created_at,'%Y-%m-%d') AS fecha 
FROM
	api_transactions
	LEFT JOIN
	cashiers
	ON 
		api_transactions.cashier_id = cashiers.cashier_id
	LEFT JOIN
	QRY_BRANCH_OFFICES
	ON 
		api_transactions.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
	WHERE api_transactions.created_at > '2023-04-01 00:00:00' 
	AND QRY_BRANCH_OFFICES.status_id = 15 and cashiers.is_electronic_id = 1
	
	ORDER BY cashier_id, exit_hour 
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_actual = pd.read_sql(query_actual, conn)
    # Calcular la sumatoria de la columna "Ingresos_actual"
    ingresos_actual_sum = df_actual["total"].sum()
    
    # Aplicar locale.currency a la suma
    #ingresos_actual_sum = locale.currency(ingresos_actual_sum, grouping=True)
   
 
# Cerrar la conexión a la base de datos
engine.dispose()

# Obtener las fechas únicas del DataFrame
fechas_unicas = df_actual['fecha'].unique()

# Ordenar las fechas de forma ascendente
fechas_unicas = np.sort(fechas_unicas)

# Crear un filtro st.selectbox para el campo "fecha"
fecha_seleccionada = st.selectbox("Selecciona una fecha:", fechas_unicas)

# Filtrar el DataFrame "df_actual" según la fecha seleccionada
df_actual_filtrado = df_actual[df_actual['fecha'] == fecha_seleccionada]

# Filtrar las horas en el rango de 9 a 22 antes de crear la tabla pivot
df_actual_filtrado = df_actual_filtrado[(df_actual_filtrado['hora'] >= 9) & (df_actual_filtrado['hora'] <= 22)]

# Definir la función para generar colores de filas
def generate_row_colors(pivot_table, even_color, odd_color, total_color):
    row_colors = []
    for i, (_, row) in enumerate(pivot_table.iterrows()):
        if row.name == 'All':
            row_colors.append(total_color)
        elif i % 2 == 0:
            row_colors.append(even_color)
        else:
            row_colors.append(odd_color)
    return row_colors


# Calcular la suma total de los valores en la columna 'total'
total_sum = df_actual_filtrado['total'].sum()

# Agregar una nueva fila a df_actual_filtrado con la suma total en la columna 'All'
df_actual_filtrado = df_actual_filtrado.assign(All=total_sum)

# Crear una tabla pivot con los campos de "df_actual_filtrado"
table_pivot_agregado = pd.pivot_table(df_actual_filtrado, values='total', index='hora', columns='All', aggfunc='sum', fill_value=0)


# Crear figura de plotly
fig_bar = go.Figure()
for column in table_pivot_agregado.columns:
    formatted_values = [f"${value:,.0f}" for value in table_pivot_agregado[column]]
    fig_bar.add_trace(go.Bar(
        x=table_pivot_agregado.index,
        y=table_pivot_agregado[column],
        name=column,
        text=formatted_values,
        textposition='auto'
    ))



# Agregar título y etiquetas de los ejes
fig_bar.update_layout(
    title='Cantidad de ventas por hora',
    xaxis_title='Hora',
    yaxis_title='Cantidad de ventas',
    xaxis=dict(
        dtick=1
    )
)


# Mostrar gráfico en Streamlit
st.plotly_chart(fig_bar)



# Crear una tabla pivot con los campos de "df_actual_filtrado"
pivot_table = pd.pivot_table(df_actual_filtrado, values='total', index='branch_office', columns='hora', aggfunc='sum', fill_value=0)

# Calcular la suma total de las filas y agregarla como una nueva fila llamada "All"
pivot_table.loc['All'] = pivot_table.sum(axis=0)

# Extraer las etiquetas de las filas y las columnas de la tabla pivot
row_labels = pivot_table.index.tolist()
column_labels = ['Horas'] + [int(col) for col in pivot_table.columns]  # Convertir las etiquetas de columna en números enteros

# Calcular los colores de las filas
row_colors = generate_row_colors(pivot_table, '#F0F8FF', 'white', '#AFCEEE')

# funcion para formatear a moneda $
def format_currency(number):
    return f"${number:,.0f}"

# Crear un objeto go.Table() con las etiquetas, los datos y los colores de las filas de la tabla pivot
table_data = [row_labels] + [pivot_table[col].tolist() for col in pivot_table.columns]
formatted_table_data = [[format_currency(value) if isinstance(value, (int, float)) else value for value in row] for row in table_data]

table_trace = go.Table(header=dict(values=column_labels, align='left'),
                       cells=dict(values=formatted_table_data, align='left', fill_color=[row_colors]),
                       columnwidth=[450] + [180]*(len(column_labels)-1))  # Ajustar el ancho de las columnas


# Añadir el objeto go.Table() al objeto go.Figure() y mostrar el gráfico en Streamlit
fig = go.Figure(data=[table_trace])

fig.update_layout(
    width=900,
    height=1100
)
st.plotly_chart(fig)
