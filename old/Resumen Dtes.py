import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import locale
import datetime
import plotly.graph_objects as go


# Establecer la configuración regional
locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')

# Configuración de la conexión a la base de datos utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://jysparki_jis:Jis2020!@103.72.78.28/jysparki_jis') 

st.header("Dashboard de Abonados") 

# Crear la consulta con la sintaxis de SQLAlchemy y obtener los resultados como un DataFrame de Pandas
query_detalle_emitidos = text("""
select 
`dtes`.`rut` AS `rut`,
`users`.`names` AS `cliente`,
`dtes`.`folio` AS `folio`,
`dtes`.`branch_office_id` AS `branch_office_id`,
`dtes`.`dte_type_id` AS `dte_type_id`,
IF(dte_type_id = 61,-1,1) AS cantidad,
`dtes`.`status_id` AS `status_id`,
`dtes`.`amount` AS `amount`,
`dtes`.`period` AS `period`,
`dtes`.`comment` AS `comment`,
 date_format(`dtes`.`created_at`,'%Y-%m-%d') AS `date`,
`statuses`.`status` AS `status`,
`dtes`.`dte_id` AS `dte_id`,
`dtes`.`chip_id` AS `chip_id` 
from `dtes` 
left join `customers` 
on(`dtes`.`rut` = `customers`.`rut`)
left join `users` 
on(`customers`.`rut` = `users`.`rut`) 
left join `statuses` 
on(`dtes`.`status_id` = `statuses`.`status_id`)
where `dtes`.`rut` <> '66666666-6' 
and `dtes`.`created_at` > '2022-12-31 00:00:00' 
and `dtes`.`dte_version_id` = 1 
and `dtes`.`status_id` > 17 
and `dtes`.`status_id` < 24 
and `users`.`rol_id` = 14
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_dte_emitidos = pd.read_sql(query_detalle_emitidos, conn)


#query para mostrar los datos maestros de sucursales
query_datos_suc = text("""
SELECT
	QRY_BRANCH_OFFICES.branch_office_id, 
	QRY_BRANCH_OFFICES.`names` as responsable, 
	QRY_BRANCH_OFFICES.branch_office, 
	QRY_BRANCH_OFFICES.principal, 
	QRY_BRANCH_OFFICES.zone, 
	QRY_BRANCH_OFFICES.segment, 
	QRY_BRANCH_OFFICES.spots, 
	QRY_BRANCH_OFFICES.price_minute, 
	QRY_BRANCH_OFFICES.price_hour	
FROM
	QRY_BRANCH_OFFICES
WHERE
	status_id = 15 and QRY_BRANCH_OFFICES.visibility_id = 1
GROUP BY
	QRY_BRANCH_OFFICES.branch_office_id
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_dm_suc = pd.read_sql(query_datos_suc, conn)
    
# Cerrar la conexión a la base de datos
engine.dispose()

st.markdown("---")

# Unir los tres dataframes por branch_office_id

df_merge = pd.merge(df_dte_emitidos, df_dm_suc, on='branch_office_id', how='outer')
#df_merge = df_merge.rename(columns={"segment": "segmento", "principal": "marca"})

# Convertir la columna de date en un objeto datetime
df_merge['date'] = pd.to_datetime(df_merge['date'])

# Crear la columna del año
df_merge['anio'] = df_merge['date'].dt.year

# Crear la columna del mes
df_merge['mes_num'] = df_merge['date'].dt.month

# Reemplazar los valores nulos con cero
#df_merge = df_merge.fillna(0)

df_merge.sort_values(by=['branch_office_id'])
df_merge.sort_values(by=['branch_office_id'], inplace=True)


meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
df_merge['mes_num'] = df_merge['mes_num'].replace(meses)
df_merge = df_merge.rename(columns={"mes_num": "mes"})



df_detalle_emitidos = df_merge[["folio","branch_office", "responsable", "status", "amount","cantidad", "anio", "mes"]]

df_detalle_emitidos = df_detalle_emitidos.dropna()


#----------------------------------------------------------------

# Crear lista de opciones para el filtro de responsable
opciones_responsable = df_detalle_emitidos["responsable"].unique().tolist()
opciones_responsable.insert(0, "Todos")  # Agregar la opción "Todos" al principio de la lista


# Crear lista de opciones para el filtro de mes
opciones_periodo_mes = df_detalle_emitidos["mes"].unique().tolist()

# Crear lista de opciones para el filtro de año
opciones_periodo_año = df_detalle_emitidos["anio"].unique().astype(int).tolist()


#----------------------------------------------------------------
# Crear filtros con las listas de opciones
responsable = st.selectbox("Filtrar por responsable", opciones_responsable)
mes = st.selectbox("Filtrar por Mes", opciones_periodo_mes)
anio = st.selectbox("Filtrar por periodo", opciones_periodo_año)


#----------------------------------------------------------------
# Filtrar el dataframe según la opción seleccionada
if responsable == "Todos":
    df_filtrado = df_detalle_emitidos[(df_detalle_emitidos["mes"] == mes) & (df_detalle_emitidos["anio"] == anio)]
else:
    df_filtrado = df_detalle_emitidos[(df_detalle_emitidos["responsable"] == responsable) & (df_detalle_emitidos["mes"] == mes)& (df_detalle_emitidos["anio"] == anio)]


# Filtrar DataFrame por responsable y periodo seleccionados
#df_filtrado = df_detalle_emitidos[(df_detalle_emitidos["responsable"] == responsable) & (df_detalle_emitidos["mes"] == mes)& (df_detalle_emitidos["anio"] == anio)]



st.markdown("---")

df_status_emitidos = df_detalle_emitidos[(df_detalle_emitidos["mes"] == mes)& (df_detalle_emitidos["anio"] == anio)]
df_pagados = df_status_emitidos[["mes", "responsable", "status", "amount", "cantidad", "folio"]]


# Creamos la pivot table
pivot_table = pd.pivot_table(df_pagados, 
                             index=['responsable'], 
                             columns=['status'], 
                             values=['amount', 'cantidad'], 
                             aggfunc={'amount': 'sum', 'cantidad': 'sum'}, 
                             margins=True)


def is_all_row(row):
    return row.name == 'All'

row_colors = ['#AFCEEE' if is_all_row(row) else 'white' for _, row in pivot_table.iterrows()]


# Reemplazar los valores nulos con cero
pivot_table = pivot_table.fillna(0)

# Aplica formato de moneda a la columna "amount"
pivot_table['amount'] = pivot_table['amount'].applymap(lambda x: f"${x:,.0f}")

# Aplica formato de número entero a la columna "cantidad"
pivot_table['cantidad'] = pivot_table['cantidad'].applymap(lambda x: f"{x:,.0f}")


# Función para generar colores de fondo para filas pares e impares
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

# Generar lista de colores de fondo para las filas de la tabla
row_colors = generate_row_colors(pivot_table, '#F0F8FF', 'white', '#AFCEEE')

# Crear el objeto go.Table
header_values = [pivot_table.index.name] + list(pivot_table.columns)
cell_values = [pivot_table.index] + [pivot_table[col] for col in pivot_table.columns]


# Crear el objeto go.Table con los colores de fondo especificados
fig = go.Figure(data=[go.Table(
    header=dict(values=header_values,                
                fill_color='#AFCEEE',
                font_color='#FFFFFF',
                align='left'),
    cells=dict(values=cell_values,
               fill_color=[row_colors],  # Utilizar la lista de colores de filas creada
               align='left'))
])

fig.update_layout(
    title="Resumen de DTE's Emitidos",   
    width=800,
    height=1000
)

# Mostrar la tabla en Streamlit
st.plotly_chart(fig)