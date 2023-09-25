import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import locale
import datetime
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots



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



# Crear 3 columnas
uno_column, dos_column, tres_column = st.columns(3)


# muestra los totales Acumulado Actual mes
with uno_column:
    st.metric(label="Actual", value=locale.currency(ingresos_actual_sum, grouping=True))

# muestra los totales Acumulado Anterior mes
with dos_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="Año Anterior", value=locale.currency(ingresos_anterior_sum, grouping=True))

# muestra los totales Acumulado Ppto mes
with tres_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="Presupuesto", value=locale.currency(ingresos_ppto_sum, grouping=True))

# Crear 3 columnas
cuatro_column, cinco_column, seis_column = st.columns(3)

# muestra Variacion SSS Acumulado mes
with cuatro_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="VAR %", value=(round(float((float(ingresos_actual_SSS_sum) / float(ingresos_anterior_SSS_sum) - 1) * 100),2)))

# muestra Desviacion % Acumulado mes
with cinco_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="DESV %", value=(round(float((float(ingresos_actual_sum) / float(ingresos_ppto_sum) - 1) * 100),2)))

# muestra Ticket Promedio Acumulado mes    
with seis_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="Ticket Promedio", value=locale.currency((float(ingresos_actual_sum) / float(ticket_actual_sum)) , grouping=True))

# Crear 3 columnas
siete_column, ocho_column, nueve_column = st.columns(3)

# muestra Ticket Pagados Acumulado mes
with siete_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="Ticket Pagados", value=locale.currency(ticket_actual_sum , grouping=True))

# muestra total Visitas Acumulado mes
with ocho_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="Visitas", value=locale.currency((ticket_actual_sum *3) , grouping=True)) 

# muestra Cantidad de Sucursales Mes
with nueve_column:
    # Mostrar la sumatoria en Streamlit
    st.metric(label="Sucursales", value=cantidad_sucursal)



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

#st.dataframe(df_nuevo)

##Grafico evolutivo mensual
# Crear figura con dos subtramas
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Agregar barras correspondientes al eje principal
fig.add_trace(go.Bar(
    x=df_nuevo['mes'],
    y=df_nuevo['Actual_E'],
    name='Ingresos Actual',
    marker_color='rgb(17, 141, 255)'
))

fig.add_trace(go.Bar(
    x=df_nuevo['mes'],
    y=df_nuevo['Anterior_E'],
    name='Año Anterior',
    marker_color='rgb(18, 35, 158)'
))

fig.add_trace(go.Bar(
    x=df_nuevo['mes'],
    y=df_nuevo['Ppto_E'],
    name='Presupuesto',
    marker_color='rgb(230, 108, 55)'
))

# Agregar línea correspondiente al eje secundario
fig.add_trace(go.Scatter(
    x=df_nuevo['mes'],
    y=df_nuevo['SSS'],
    name=' Var sss',
    mode='lines',
    line=dict(width=4, color='red'),
    yaxis='y2'
))

# Actualizar diseño de la figura
fig.update_layout(
    title='Gráfico Evolutivo de ingresos y Variación SSS',
    xaxis_title='mes',
    yaxis_title='Ingresos',
    yaxis2_title='Var sss',
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(dtick=1),
    #yaxis=dict(dtick=8),
    width=800,
    height=500
)

#fig.update_yaxes(range=[0, 50], secondary_y=True)

# Mostrar figura en Streamlit
st.plotly_chart(fig)
#fig.show()


st.markdown("---")


# Unir los dataframes por la columna "dia"
#df_union = df_actual.merge(df_anterior, on="dia", how="outer").merge(df_ppto, on="dia", how="outer")

## Seleccionar las columnas que queremos mostrar y renombrarlas
#df_union = df_union[["dia", "Ingresos_actual", "Ingresos_anterior", "ppto"]]
#df_union = df_union.rename(columns={"Ingresos_actual": "Actual", "Ingresos_anterior": "Anterior"})


#query para mostrar los ingresos actual acumulados por sucursal, ingreso y ticket actual
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


# Aplicar el color de fondo a las columnas pares
#styled_df = df_detalle.background_gradient(subset=df_detalle.IndexSlice[:, [0, 2]], cmap='Blues')

# Aplicar el formato deseado a los números



# Aplicar estilo a filas pares
#styled_df = df_detalle.style.apply(lambda x: ['background-color: #f2f2f2' if i%2==0 else '' for i in range(len(x))])



# Mostrar DataFrame en Streamlit
st.dataframe(df_detalle)


df_segmento = df_merge[["segmento", "Ingresos_actual"]]
df_marca = df_merge[["marca", "Ingresos_actual"]]

ingresos_segmento = (df_segmento.groupby(by=['segmento']).sum()[['Ingresos_actual']].sort_values(by='Ingresos_actual'))
ingresos_segmento.reset_index(inplace=True)

ingresos_marca = (df_marca.groupby(by=['marca']).sum()[['Ingresos_actual']].sort_values(by='Ingresos_actual'))
ingresos_marca.reset_index(inplace=True)
#ingresos_marca = (df_merge.groupby(by=['marca']).sum()[['Ingresos_actual']].sort_values(by='Ingresos_actual'))

#st.write(ingresos_segmento)
#st.write(ingresos_marca)

fig_ingresos_segmento = px.bar(
    ingresos_segmento,
    x='Ingresos_actual',
    y='segmento',
    orientation='h',
    title='<b>Ventas por Segmento</b>',
    template='plotly_white'
)

fig_ingresos_segmento.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    #showlegend=True,
    xaxis_title='Ingresos actuales',
    yaxis_title='Segmento',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


fig_ingresos_marca = px.bar(
    ingresos_marca,
    x='Ingresos_actual',
    y='marca',
    orientation='h',
    title='<b>Ventas por Marca</b>',
    template='plotly_white'
)

fig_ingresos_marca.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    #showlegend=True,
    xaxis_title='Ingresos actuales',
    yaxis_title='Marca',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)




left_column, right_column = st.columns(2)

left_column.plotly_chart(fig_ingresos_segmento, use_container_width = True) 
right_column.plotly_chart(fig_ingresos_marca, use_container_width = True) 