import streamlit as st
import pandas as pd
import locale
import plotly.express as px
import plotly.graph_objects as go


# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')


@st.cache_data(ttl=3600)
def ingreso_acum_mes_actual():
    df_acum_mes_actual = conn.query("select * from KPI_INGRESOS_MES", ttl=600)
    return df_acum_mes_actual

# Número de filas por página
rows_per_page = 50

# Función para mostrar el DataFrame con paginación
def show_dataframe_with_pagination(df):
    total_rows = len(df)
    num_pages = (total_rows - 1) // rows_per_page + 1

    page_number = st.number_input('Página', min_value=1, max_value=num_pages, value=1)

    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)

    st.dataframe(df[start_idx:end_idx], use_container_width=True, height=400)

df_total = ingreso_acum_mes_actual()

def calcular_variacion(df, columna_actual, columna_anterior):
    # Calcula la variación porcentual entre dos columnas de un DataFrame
    variacion = (df[columna_actual] / df[columna_anterior] - 1) * 100
    # Formatea la variación con dos decimales y agrega el símbolo "%"
    variacion = variacion.apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}")
    return variacion

def calcular_ticket_promedio(df, columna_ingresos, columna_tickets):
    # Calcula el ticket promedio entre dos columnas de un DataFrame
    ticket_promedio = (df[columna_ingresos] / df[columna_tickets]).round(0)
    return ticket_promedio


# Diccionario con los nombres originales y los nuevos nombres de las columnas de ingresos
columnas_ingresos = {
    'venta_SSS': 'ventas act',
    'venta_sss_anterior': 'ventas ant',
    'ingresos_SSS': 'ingresos act',
    'ingresos_sss_anterior': 'ingresos ant'
}

# Diccionario con los nombres originales y los nuevos nombres de las columnas de tickets
columnas_tickets = {
    'ticket_number': 'ticket act',
    'ticket_anterior': 'ticket ant'
}

# Diccionario con los nombres originales y los nuevos nombres de las columnas de variación
columnas_variacion = {
    'var% SSS': 'var SSS',
    'var Q': 'var Q'
}

# Diccionario con los nombres originales y los nuevos nombres de las columnas de ticket promedio
columnas_ticket_promedio = {
    'ticket prom act': 'ticket prom act'
}

# Crear el DataFrame df_acum_mes con el filtro para el año 2023
df_acum_mes = df_total[df_total['año'] == 2023]
# Crear el DataFrame df_acum_mes_ant con el filtro para el año 2022
df_acum_mes_ant = df_total[df_total['año'] == 2022]

df_acum_mes_ant = df_acum_mes_ant.rename(columns={'ingresos_SSS':'ingresos_sss_anterior',
                                   'venta_SSS':'venta_sss_anterior',
                                   'Trimestre':'trimestre',
                                   'Periodo':'periodo',
                                   'ticket_number':'ticket_anterior'})

df_agrupado = pd.merge(df_acum_mes, df_acum_mes_ant, how='left', left_on=['branch_office', 'periodo'],
                       right_on=['branch_office', 'periodo'], suffixes=('', '_ant'))

# Eliminar las columnas del DataFrame df_acum_mes_ant que se duplicaron en la fusión
df_agrupado = df_agrupado.drop(columns=[ 'id','trimestre_ant', 'period_ant' , 'id_ant', 'año_ant' , 'supervisor_ant'])

# Usar las funciones definidas para crear las nuevas columnas del DataFrame df_agrupado
df_agrupado = df_agrupado.assign(
    var_SSS = calcular_variacion(df_agrupado, 'ingresos_SSS', 'ingresos_sss_anterior'),
    var_Q = calcular_variacion(df_agrupado, 'ticket_number', 'ticket_anterior'),
    ticket_prom_act = calcular_ticket_promedio(df_agrupado, 'ingresos_SSS', 'ticket_number')
)

df_agrupado = df_agrupado.rename(columns={
    'periodo': 'periodo',
    'branch_office': 'sucursal',    
    'venta_SSS': 'ventas act',
    'venta_sss_anterior': 'ventas ant',
    'ingresos_SSS': 'ingresos act',
    'ingresos_sss_anterior': 'ingresos ant',
    'ticket_number': 'ticket act',
    'ticket_anterior': 'ticket ant'  
    })

##segunda parte

# Seleccionar las columnas que deseas mostrar en ambos DataFrames
columns_to_show = ['periodo' , 'sucursal' , 'ventas act', 'ventas ant',  'ingresos act', 'ingresos ant',  'ticket act' ,  'ticket ant',  'var_SSS', 'var_Q', 'ticket_prom_act']

# Ahora puedes usar la lista actualizada para seleccionar las columnas del DataFrame
df_inicial = df_agrupado[columns_to_show].set_index('periodo')

st.sidebar.title('Filtros Disponibles')
# Obtener una lista de todas los filtros disponibles
periodos = df_agrupado['periodo'].unique()
supervisors = df_agrupado['supervisor'].unique()
supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
branch_offices = df_agrupado[df_agrupado['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos)

# Filtrar el DataFrame según los filtros seleccionados
if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
    df_filtrado = df_agrupado[
        (df_agrupado['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
        (df_agrupado['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
        (df_agrupado['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)
    ]
else:
    df_filtrado = df_inicial

# Creamos un DataFrame agrupado con la sumatoria total de cada columna de df_filtrado
sum_df_filtrado = df_filtrado.sum()

# Verificar si la columna 'periodo' está presente en df_filtrado antes de realizar la agrupación
if 'periodo' in df_filtrado.columns:
    df_group_mes = df_filtrado.groupby('periodo')[['ingresos act', 'ingresos ant']].sum().reset_index()
else:
    df_group_mes = df_inicial.groupby('periodo')[['ingresos act', 'ingresos ant']].sum().reset_index()

# Mostrar el DataFrame df_group_mes
#cst.dataframe(df_group_mes)

# Crear una nueva columna "var_sss" en el DataFrame
#df_group_mes["var_sss"] = (df_group_mes["ingresos act"] / df_group_mes["ingresos ant"])-1

# Calcular la variación "var_sss" utilizando la función calcular_variacion
df_group_mes["var_sss"] = calcular_variacion(df_group_mes, "ingresos act", "ingresos ant")

# Crear el gráfico con subplots
fig_combined = go.Figure()

# Agregar las barras al gráfico principal
fig_combined.add_trace(go.Bar(x=df_group_mes["periodo"], y=df_group_mes["ingresos act"],
                              name="Ingresos Actuales", marker_color="blue", yaxis="y1"))
fig_combined.add_trace(go.Bar(x=df_group_mes["periodo"], y=df_group_mes["ingresos ant"],
                              name="Ingresos Anteriores", marker_color="LightSkyBlue", yaxis="y1"))

# Agregar la línea al gráfico secundario
fig_combined.add_trace(go.Scatter(x=df_group_mes["periodo"], y=df_group_mes["var_sss"],
                                  mode="lines+markers", name="Var SSS", line=dict(width=5,color="red"), marker=dict(size=4, symbol="circle"), yaxis="y2"))

# Ajustar las propiedades del eje primario (y1)
fig_combined.update_layout(yaxis=dict(title="Ingresos", showgrid=True, zeroline=True))

# Ajustar las propiedades del eje secundario (y2)
fig_combined.update_layout(yaxis2=dict(title="Var SSS", showgrid=False, zeroline=False, overlaying="y", side="right"))

# Mover la leyenda debajo del eje x y centrada
fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))

# Mostrar el gráfico utilizando Streamlit
st.plotly_chart(fig_combined)

st.markdown("""---""")

# Función para formatear un número como moneda con símbolo de dólar y separadores de miles
def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)

# Obtener las sumatorias de las columnas requeridas
ticket_act_sum = sum_df_filtrado['ticket act']
ventas_act_sum = sum_df_filtrado['ventas act']
ingresos_act_sum = sum_df_filtrado['ingresos act']
ticket_ant_sum = sum_df_filtrado['ticket ant']
ventas_ant_sum = sum_df_filtrado['ventas ant']
ingresos_ant_sum = sum_df_filtrado['ingresos ant']
var_sss = (ingresos_act_sum/ingresos_ant_sum-1) * 100

# Formatear las sumatorias de ingresos a formato de moneda
ingresos_act_sum_formatted = format_currency(ingresos_act_sum)
ingresos_ant_sum_formatted = format_currency(ingresos_ant_sum)
var_sss_formatted = format_percentage(var_sss)


# Título principal con formato HTML
st.markdown("""
    <div class="mx-10 mt-5">
        <h1 class="text-6xl ">Indicadores JIS Parking</h1>
    </div>
""", unsafe_allow_html=True)

# Crear un contenedor principal con un ancho máximo de 1200px y un margen automático
with st.container():
    st.markdown(f"""
    <link href="https://unpkg.com/tailwindcss@2.2.4/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://demos.creative-tim.com/notus-js/assets/vendor/@fortawesome/fontawesome-free/css/all.min.css" rel="stylesheet">
         """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="flex flex-col items-center justify-center px-1 pt-4 pb5">
            <!---== primero     Stats Container ====--->
            <div class="flex flex-col xl:flex-row shadow hover:shadow-md w-full bg-white rounded-lg overflow-hidden cursor-pointer">
                <div class="w-72 bg-white max-w-xs mx-auto rounded-sm overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 transform hover:scale-100 cursor-pointer">
                    <div class="h-20 bg-green-400 flex items-center justify-between">
                        <p class="mr-0 text-white text-lg pl-5">INGRESOS ACTUAL</p>
                    </div>
                <div class="flex justify-between px-5 pt-6 mb-2 text-sm text-gray-600">
                <p>Venta Neta + Abonados</p>
            </div>
                <p class="py-4 text-3xl ml-5">{ingresos_act_sum_formatted}</p>
         </div>
    </div>   
</div>
""", unsafe_allow_html=True)

# Contenido de la segunda tarjeta "Ingresos Anterior"
    with col2:
        st.markdown(f"""    
       <div class="flex flex-col items-center justify-center px-1 pt-4 pb5">
            <!---== Segunda   Stats Container ====--->
            <div class="flex flex-col xl:flex-row shadow hover:shadow-md w-full bg-white rounded-lg overflow-hidden cursor-pointer">
                <div class="w-72 bg-white max-w-xs mx-auto rounded-sm overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 transform hover:scale-100 cursor-pointer">
                    <div class="h-20 bg-red-400 flex items-center justify-between">
                        <p class="mr-0 text-white text-lg pl-5">INGRESOS ANTERIOR</p>
                    </div>
                <div class="flex justify-between px-5 pt-6 mb-2 text-sm text-gray-600">
                <p>Venta Neta + Abonados</p>
            </div>
                <p class="py-4 text-3xl ml-5">{ingresos_ant_sum_formatted}</p>
        </div>
    </div>   
</div>
""", unsafe_allow_html=True)

# Contenido de la tercera tarjeta "Var SSS"
    with col3:
        st.markdown(f"""    
        <div class="flex flex-col items-center justify-center px-1 pt-4 pb5">
            <!---== Tercera Stats Container ====--->
            <div class="flex flex-col xl:flex-row shadow hover:shadow-md w-full bg-white rounded-lg overflow-hidden cursor-pointer">
                <div class="w-72 bg-white max-w-xs mx-auto rounded-sm overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 transform hover:scale-100 cursor-pointer">
                    <div class="h-20 bg-blue-400 flex items-center justify-between">
                        <p class="mr-0 text-white text-lg pl-5">VARIACION % SSS</p>
                    </div>
                <div class="flex justify-between px-5 pt-6 mb-2 text-sm text-gray-600">
                <p>Same Store Sale</p>
            </div>
                <p class="py-4 text-3xl ml-5">{var_sss_formatted}</p>
        </div>
    </div>   
</div>
""", unsafe_allow_html=True)

st.markdown("""---""")

st.write('Selección de datos:')

# Verificar si se han seleccionado opciones para al menos uno de los filtros
with st.container():
    if not (periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados):
        show_dataframe_with_pagination(df_agrupado[columns_to_show].set_index('periodo'))
        
    else:
        show_dataframe_with_pagination(df_filtrado[columns_to_show].set_index('periodo'))


