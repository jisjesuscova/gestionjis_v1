import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import locale
import plotly.graph_objects as go

# Configuración de la conexión a la base de datos utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://jysparki_jis:Jis2020!@103.72.78.28/jysparki_jis') 

st.header("Reporte de Abonados") 

# Crear la consulta con la sintaxis de SQLAlchemy y obtener los resultados como un DataFrame de Pandas
query_detalle_emitidos = text("""
select 
`dtes`.`rut` AS `rut`,
`users`.`names` AS `cliente`,
(`dtes`.`folio`*1) AS `folio`,
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

# Unir los tres dataframes por branch_office_id
df_merge = pd.merge(df_dte_emitidos, df_dm_suc, on='branch_office_id', how='outer')
# Convertir la columna de date en un objeto datetime
df_merge['date'] = pd.to_datetime(df_merge['date'])
# Crear la columna del año
df_merge['anio'] = df_merge['date'].dt.year
# Crear la columna del mes
df_merge['mes_num'] = df_merge['date'].dt.month
# Reemplazar los valores nulos con cero

df_merge.sort_values(by=['branch_office_id'])
df_merge.sort_values(by=['branch_office_id'], inplace=True)

meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
df_merge['mes_num'] = df_merge['mes_num'].replace(meses)
df_merge = df_merge.rename(columns={"mes_num": "mes"})
df_merge['folio'] = df_merge['folio'].fillna(0)
df_merge = df_merge.dropna(subset=['folio'])
df_merge['folio'] = df_merge['folio'].astype(int)

df_detalle_emitidos = df_merge[["folio","rut","cliente","branch_office", "responsable", "status", "cantidad", "amount", "anio", "mes"]]
df_detalle_emitidos = df_detalle_emitidos.dropna()

# Crear lista de opciones para el filtro de responsable
opciones_responsable = df_detalle_emitidos["responsable"].unique().tolist()
opciones_responsable.insert(0, "Todos")  # Agregar la opción "Todos" al principio de la lista
# Crear lista de opciones para el filtro de mes
opciones_periodo_mes = df_detalle_emitidos["mes"].unique().tolist()
# Crear lista de opciones para el filtro de año
opciones_periodo_año = df_detalle_emitidos["anio"].unique().astype(int).tolist()
# Crear filtros con las listas de opciones
responsable = st.selectbox("Filtrar por responsable", opciones_responsable)
mes = st.selectbox("Filtrar por Mes", opciones_periodo_mes)
anio = st.selectbox("Filtrar por periodo", opciones_periodo_año)

# Filtrar el dataframe según la opción seleccionada
if responsable == "Todos":
    df_filtrado = df_detalle_emitidos[(df_detalle_emitidos["mes"] == mes) & (df_detalle_emitidos["anio"] == anio)]
else:
    df_filtrado = df_detalle_emitidos[(df_detalle_emitidos["responsable"] == responsable) & (df_detalle_emitidos["mes"] == mes)& (df_detalle_emitidos["anio"] == anio)]
df_status_emitidos = df_detalle_emitidos[(df_detalle_emitidos["mes"] == mes)& (df_detalle_emitidos["anio"] == anio)]


def format_currency(number):
    return f"{number:,.0f}"

def format_moneda(number):
    return f"${number:,.0f}"

# Obtener la suma total del campo 'cantidad' y del campo 'amount' "general"
total_cantidad = df_filtrado['cantidad'].sum()
total_amount = df_filtrado['amount'].sum()


# Filtrar el dataframe por el status "Imputada Pagada"
df_filtrado_imputada_pagada = df_filtrado[df_filtrado["status"] == "Imputada Pagada"]
df_filtrado_imputada_por_pagar = df_filtrado[df_filtrado["status"] == "Imputada por Pagar"]

# Obtener la suma total del campo 'cantidad' y del campo 'amount' "Imputada Pagada"
total_cantidad_imputada_pagada = df_filtrado_imputada_pagada['cantidad'].sum()
total_amount_imputada_pagada = df_filtrado_imputada_pagada['amount'].sum()

# Obtener la suma total del campo 'cantidad' y del campo 'amount' "Imputada por Pagar"
total_cantidad_imputada_por_pagar = df_filtrado_imputada_por_pagar['cantidad'].sum()
total_amount_imputada_por_pagar = df_filtrado_imputada_por_pagar['amount'].sum()

# Aplicar la función format_currency a las variables
q_imputada_por_pagar = format_currency(total_cantidad_imputada_por_pagar)
q_imputada_pagada = format_currency(total_cantidad_imputada_pagada)
q_total = format_currency(total_cantidad)

# Aplicar la función format_moneda a las variables
total_imputada_por_pagar = format_moneda(total_amount_imputada_por_pagar)
total_imputada_pagada = format_moneda(total_amount_imputada_pagada)
total_total = format_moneda(total_amount)

# Crear dos columnas para mostrar los resultados con st.metric
col1, col2, col3 = st.columns(3)


col1.metric(label="Total Pagada", value=total_imputada_pagada)
col2.metric(label="Total por Pagar", value=total_imputada_por_pagar)
col3.metric(label="Total", value=total_total)


# Crear dos columnas para mostrar los resultados con st.metric
col4, col5, col6 = st.columns(3)

# Mostrar la suma total del campo 'cantidad' en la primera columna
col4.metric(label="cantidad Pagada", value=q_imputada_pagada)

# Mostrar la suma total del campo 'amount' en la segunda columna
col5.metric(label="cantidad por Pagar", value=q_imputada_por_pagar)

col6.metric(label="cantidad", value=q_total)


# Crear la tabla dinámica
pivot_table = pd.pivot_table(
    data=df_filtrado,
    index='branch_office', 
    columns='status', 
    values=['amount', 'cantidad'],
    aggfunc={'amount': 'sum', 'cantidad': 'sum'}
)

# Rellenar los valores nulos con 0
pivot_table = pivot_table.fillna(0)

# Agregar la suma total de cada columna como una nueva fila
pivot_table.loc['Total'] = pivot_table.sum()

# Función para generar colores de fondo para filas pares e impares
def generate_row_colors(pivot_table, even_color, odd_color, total_color):
    row_colors = []
    for i, (_, row) in enumerate(pivot_table.iterrows()):
        if row.name == 'Total':
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


# Formatear los campos 'amount' y 'cantidad'
amount_format = "${:,.0f}"  # Formato para 'amount'
cantidad_format = "{:,.0f}"    # Formato para 'cantidad'

# Aplicar el formato a los campos 'amount' y 'cantidad'
formatted_cell_values = []
for col in pivot_table.columns:
    if col[0] == "amount":
        formatted_cell_values.append(pivot_table[col].apply(lambda x: amount_format.format(x)))
    elif col[0] == "cantidad":
        formatted_cell_values.append(pivot_table[col].apply(lambda x: cantidad_format.format(x)))
    else:
        formatted_cell_values.append(pivot_table[col])


# Crear header_values y cell_values
header_values = [pivot_table.index.name] + [f"{col[0]} - {col[1]}" for col in pivot_table.columns]
cell_values = [pivot_table.index] + [pivot_table[col] for col in pivot_table.columns]


# Crear el objeto go.Table
fig = go.Figure(data=[go.Table(
    header=dict(values=header_values,
                fill_color='#AFCEEE',
                font_color='#FFFFFF',
                align='left'),
    cells=dict(values=[pivot_table.index] + formatted_cell_values,
               fill_color=[row_colors],  # Aplicar los colores de fondo para las filas
               align='left'
               ))
        ])


fig.update_layout(
    title="Resumen de DTE's Emitidos",   
    width=600,
    height=500
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)

# Crear lista de opciones para el filtro de branch_office
opciones_branch_office = df_filtrado["branch_office"].unique().tolist()
opciones_branch_office.insert(0, "Todos")  # Agregar la opción "Todos" al principio de la lista

# Crear filtro con las listas de opciones
branch_office = st.selectbox("Filtrar por sucursal", opciones_branch_office)


if branch_office == "Todos":
    df_filtrado_branch_office = df_filtrado
else:
    df_filtrado_branch_office = df_filtrado[df_filtrado["branch_office"] == branch_office]

df_filtrado_detalle = df_filtrado_branch_office[["folio","rut","cliente","status", "cantidad", "amount"]]

df_filtrado_detalle["folio"] = df_filtrado_detalle["folio"].astype(int)

df_filtrado_detalle.sort_values(by=['status'])
df_filtrado_detalle.sort_values(by=['status'],ascending=False, inplace=True)

df_filtrado_detalle["folio"] = df_filtrado_detalle["folio"].apply(lambda x: '{:,}'.format(x))



st.dataframe(df_filtrado_detalle)