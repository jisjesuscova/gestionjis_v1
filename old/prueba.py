import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import locale
import datetime
import plotly.graph_objs as go




# Establecer la configuración regional
locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')

# Configuración de la conexión a la base de datos utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://jysparki_jis:Jis2020!@103.72.78.28/jysparki_jis') 


# # Configuración de la conexión a la base de datos
# connection = pymysql.connect(
#     host='103.72.78.28',
#     user='jysparki_jis',
#     password='Jis2020!',
#     db='jysparki_jis',
#     charset='utf8mb4',
#     cursorclass=pymysql.cursors.DictCursor
# )

st.header("Dashboard de Ventas") 

# Crear la consulta con la sintaxis de SQLAlchemy y obtener los resultados como un DataFrame de Pandas
query_actual = text("""
SELECT
    DAY(date) as dia,
    'actual' as Version,
	SUM(DASH_INGRESOS_ACUMULADO_ACTUAL.ticket_number) AS ticket_number, 
	SUM(DASH_INGRESOS_ACUMULADO_ACTUAL.Ingresos) AS Ingresos_actual, 	
	SUM(DASH_INGRESOS_ACUMULADO_ACTUAL.Ingresos_SSS) AS Ingresos_SSS_actual
FROM
	DASH_INGRESOS_ACUMULADO_ACTUAL
	GROUP BY
	DASH_INGRESOS_ACUMULADO_ACTUAL.date
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_actual = pd.read_sql(query_actual, conn)
    # Calcular la sumatoria de la columna "Ingresos_actual"
    ingresos_actual_sum = df_actual["Ingresos_actual"].sum()
    # Calcular la sumatoria de la columna "ticket_number"
    ticket_actual_sum = df_actual["ticket_number"].sum()


query_count = text("""
SELECT branch_office_id, SUM(Ingresos) as total_ingresos
FROM DASH_INGRESOS_ACUMULADO_ACTUAL
GROUP BY branch_office_id
HAVING SUM(Ingresos) > 100;
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_count = pd.read_sql(query_count, conn)
    # Calcular la sumatoria de la columna "Ingresos_actual"
    cantidad_sucursal = df_count["branch_office_id"].count()
    #print(cantidad_sucursal)

    

query_anterior = text("""
SELECT
    DAY(date) as dia,
    'Anterior' as Version,
	SUM(ticket_number) AS ticket_number,
	SUM(Ingresos) AS Ingresos_anterior,
	SUM(Ingresos_SSS) AS Ingresos_SSS_anterior
FROM
	DASH_INGRESOS_ACUMULADO_ANTERIOR
	GROUP BY
	date
""")

with engine.connect() as conn:
    df_anterior = pd.read_sql(query_anterior, conn)
    # Calcular la sumatoria de la columna "Ingresos_anterior"
    ingresos_anterior_sum = df_anterior["Ingresos_anterior"].sum()


query_ppto = text("""
SELECT
    DAY(date) as dia,
	date, 
	SUM(ppto) AS ppto
FROM
	DASH_INGRESOS_ACUMULADO_PPTO
	GROUP BY
	date
""")

with engine.connect() as conn:
    df_ppto = pd.read_sql(query_ppto, conn)
    # Calcular la sumatoria de la columna "Ingresos_ppto"
    ingresos_ppto_sum = df_ppto["ppto"].sum()


query_evo_actual = text("""
SELECT
	MONTH(date)as mes,
	sum(DASH_INGRESOS_ACTUAL.ticket_number) as ticket_number, 
	sum(DASH_INGRESOS_ACTUAL.Venta_Neta) as Venta_Neta, 
	sum(DASH_INGRESOS_ACTUAL.Ingresos) as Ingresos_actual, 
	sum(DASH_INGRESOS_ACTUAL.Venta_SSS) as Venta_SSS, 
	sum(DASH_INGRESOS_ACTUAL.Ingresos_SSS) as Ingresos_SSS_actual
FROM
	DASH_INGRESOS_ACTUAL
GROUP BY MONTH(date)
""")

with engine.connect() as conn:
    df_evo_actual = pd.read_sql(query_evo_actual, conn)
    # Calcular la sumatoria de la columna "Ingresos_sss_actual"
    ingresos_actual_SSS_sum = df_actual["Ingresos_SSS_actual"].sum()


query_evo_anterior = text("""
SELECT
	MONTH(date)as mes,
	sum(DASH_INGRESOS_ANTERIOR.ticket_number) as ticket_number, 
	sum(DASH_INGRESOS_ANTERIOR.Venta_Neta) as Venta_Neta, 
	sum(DASH_INGRESOS_ANTERIOR.Ingresos) as Ingresos_anterior, 
	sum(DASH_INGRESOS_ANTERIOR.Venta_SSS) as Venta_SSS, 
	sum(DASH_INGRESOS_ANTERIOR.Ingresos_SSS) as Ingresos_SSS_anterior
FROM
	DASH_INGRESOS_ANTERIOR
GROUP BY MONTH(date)
""")

with engine.connect() as conn:
    df_evo_anterior = pd.read_sql(query_evo_anterior, conn)
    # Calcular la sumatoria de la columna "Ingresos_sss_anterior"
    ingresos_anterior_SSS_sum = df_anterior["Ingresos_SSS_anterior"].sum()


query_evo_ppto = text("""
SELECT
	MONTH(date)as mes,
	sum(DASH_INGRESOS_PPTO.ppto) as Ingresos_ppto
FROM
	DASH_INGRESOS_PPTO
GROUP BY MONTH(date)
""")

with engine.connect() as conn:
    df_evo_ppto = pd.read_sql(query_evo_ppto, conn)

# Cerrar la conexión a la base de datos
engine.dispose()




## Unir los dataframes evo por la columna "mes" left outer join
df_union_evo = df_evo_actual.merge(df_evo_anterior, on="mes", how="outer").merge(df_evo_ppto, on="mes", how="outer")

## Seleccionar las columnas que queremos mostrar y renombrarlas
df_union_evo = df_union_evo[["mes", "Ingresos_actual", "Ingresos_anterior", "Ingresos_ppto", "Ingresos_SSS_actual", "Ingresos_SSS_anterior"]]
df_union_evo["vsss"] = round(((df_union_evo["Ingresos_SSS_actual"]/df_union_evo["Ingresos_SSS_anterior"]-1)*100),2)
df_union_evo = df_union_evo.rename(columns={"Ingresos_actual": "Actual_E", "Ingresos_anterior": "Anterior_E", "Ingresos_ppto": "Ppto_E", "Ingresos_SSS_actual": "SSS_actual" , "Ingresos_SSS_anterior": "SSS_anterior", "vsss": "SSS"})

#st.dataframe(df_union_evo)
varsss = (round(float((float(ingresos_actual_SSS_sum) / float(ingresos_anterior_SSS_sum) - 1) * 100),2))

st.markdown("---")

# Guarda la posicion del mes a reemplazar
mes_pos = datetime.datetime.now().month

df_nuevo = df_union_evo
df_nuevo.loc[mes_pos -1, ['mes', "Actual_E", "Anterior_E", "Ppto_E", "SSS_actual", "SSS_anterior", "SSS"]] = [mes_pos, ingresos_actual_sum, ingresos_anterior_sum, ingresos_ppto_sum, ingresos_actual_SSS_sum, ingresos_anterior_SSS_sum, varsss]
df_nuevo = df_nuevo.sort_values(by=['mes'], ignore_index=True)

meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
df_nuevo['mes'] = df_nuevo['mes'].replace(meses)


query_acumulado_actual_suc = text("""
SELECT
  DASH_INGRESOS_ACUMULADO_ACTUAL.branch_office_id,
	'Actual' AS version, 
	SUM(DASH_INGRESOS_ACUMULADO_ACTUAL.ticket_number) AS ticket_actual, 
	SUM(DASH_INGRESOS_ACUMULADO_ACTUAL.Ingresos) AS Ingresos_actual, 
	SUM(DASH_INGRESOS_ACUMULADO_ACTUAL.Ingresos_SSS) AS Ingresos_SSS_actual
	
FROM
	DASH_INGRESOS_ACUMULADO_ACTUAL
GROUP BY
	DASH_INGRESOS_ACUMULADO_ACTUAL.branch_office_id
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_actual_suc = pd.read_sql(query_acumulado_actual_suc, conn)
    # Calcular la sumatoria de la columna "Ingresos_actual"
    ingresos_actual_suc = df_actual_suc["Ingresos_actual"].sum()
    # Calcular la sumatoria de la columna "Ingresos_SSS_actual"
    ingresos_actual_sss_suc = df_actual_suc["Ingresos_SSS_actual"].sum()
    # Calcular la sumatoria de la columna "ticket_number"
    ticket_actual_suc = df_actual_suc["Ingresos_actual"].sum()
    

#query para mostrar los ingresos anterior acumulados por sucursal ingreso  anterior e ingresos SSS Anterior
query_acumulado_anterior_suc = text("""
SELECT
  DASH_INGRESOS_ACUMULADO_ANTERIOR.branch_office_id,
	'Anterior' AS version, 
	SUM(DASH_INGRESOS_ACUMULADO_ANTERIOR.ticket_number) AS ticket_number, 
	SUM(DASH_INGRESOS_ACUMULADO_ANTERIOR.Ingresos) AS Ingresos_anterior, 
	SUM(DASH_INGRESOS_ACUMULADO_ANTERIOR.Ingresos_SSS) AS Ingresos_SSS_anterior
	
FROM
	DASH_INGRESOS_ACUMULADO_ANTERIOR
GROUP BY
	DASH_INGRESOS_ACUMULADO_ANTERIOR.branch_office_id
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_anterior_suc = pd.read_sql(query_acumulado_anterior_suc, conn)
    # Calcular la sumatoria de la columna "Ingresos_actual"
    ingresos_anterior_suc = df_anterior_suc["Ingresos_anterior"].sum()
    # Calcular la sumatoria de la columna "Ingresos_SSS_actual"
    ingresos_anterior_sss_suc = df_anterior_suc["Ingresos_SSS_anterior"].sum()


#query para mostrar los ingresos anterior acumulados por sucursal ingreso  PPTO
query_acumulado_ppto_suc = text("""
SELECT
  DASH_INGRESOS_ACUMULADO_PPTO.branch_office_id,
	'Ppto' AS version, 
	SUM(DASH_INGRESOS_ACUMULADO_PPTO.ppto) AS Ingresos_ppto
	
FROM
	DASH_INGRESOS_ACUMULADO_PPTO
GROUP BY
	DASH_INGRESOS_ACUMULADO_PPTO.branch_office_id
""")

# Ejecutar la consulta a través del motor
with engine.connect() as conn:
    df_ppto_suc = pd.read_sql(query_acumulado_ppto_suc, conn)
    # Calcular la sumatoria de la columna "Ingresos_ppto"
    ingresos_ppto_suc = df_ppto_suc["Ingresos_ppto"].sum()

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
 
    


# Unir los tres dataframes por branch_office_id
df_merge = pd.merge(df_actual_suc, df_anterior_suc, on='branch_office_id', how='outer')
df_merge = pd.merge(df_merge, df_ppto_suc, on='branch_office_id', how='outer')
df_merge = pd.merge(df_merge, df_dm_suc, on='branch_office_id', how='outer')
df_merge = df_merge.rename(columns={"segment": "segmento", "principal": "marca"})

# Reemplazar los valores nulos con cero
df_merge = df_merge.fillna(0)

#df_merge.sort_values(by=['branch_office'])

df_detalle = df_merge[["branch_office", "Ingresos_actual", "Ingresos_anterior","Ingresos_ppto", "ticket_actual"]]

df_detalle["sssvar"] = round(((df_merge["Ingresos_SSS_actual"]/df_merge["Ingresos_SSS_anterior"]-1)*100),2)
df_detalle["pptodesv"] = round(((df_merge["Ingresos_actual"]/df_merge["Ingresos_ppto"]-1)*100),2)
df_detalle["ticket_prom"] = round((df_merge["Ingresos_actual"]/df_merge["ticket_actual"]),0)
df_detalle = df_detalle.rename(columns={"Ingresos_actual": "Actual", "branch_office": "Sucursal","Ingresos_anterior": "Año Ant","Ingresos_ppto": "Ppto","ticket_actual": "ticket","sssvar": "Var%", "pptodesv": "Desv%", "ticket_prom": "Ticket Promedio"})

df_detalle=df_detalle.set_index('Sucursal')
df_detalle.sort_values(by=['Sucursal'], inplace=True)


# Crear la tabla dinámica
pivot_table = pd.pivot_table(df_detalle, index='Sucursal', values=["Actual", "Año Ant", "Var%", "Ppto", "Desv%", "ticket", "Ticket Promedio"])

pivot_table['Actual'].apply(lambda x: f"${x:,.0f}") 
pivot_table['Año Ant'].apply(lambda x: f"${x:,.0f}") 

# Convertir la tabla dinámica a un dataframe y resetear los índices
df_pivot = pivot_table.reset_index()

# Crear la lista de cabeceras para la tabla
header_values = list(df_pivot.columns)

# Crear la lista de valores para la tabla
cell_values = [df_pivot[col].values.tolist() for col in df_pivot.columns]



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

row_colors = generate_row_colors(pivot_table, '#F0F8FF', 'white', '#AFCEEE')




# Crear el gráfico de tabla de Plotly
fig = go.Figure(data=[go.Table(
    header=dict(values=header_values,
                font_family="Courier New",
                font_size=14,
                fill_color='#AFCEEE',
                font_color='#FFFFFF',
                align='left'),
    cells=dict(values=cell_values,
               fill_color=[row_colors],  # Aplica los colores de fondo a las filas
               align='left'))
])

fig.update_layout(
    title="Detalle Ventas por Sucursal",   
    width=800,
    height=1000
)

# Mostrar el gráfico de tabla en Streamlit
st.plotly_chart(fig)