import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
 
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def kpi_recaudacion_dia():
    df_recaudacion = conn.query("""SELECT
                        date_format(`deposits`.`collection_date`,'%Y-%m-%d') AS Fecha, 
                        deposits.branch_office_id AS branch_office_id, 
                        sum(deposits.deposit_amount) AS deposito	
                        FROM deposits 
                        LEFT JOIN statuses
                        ON deposits.status_id = statuses.status_id
                        LEFT JOIN QRY_BRANCH_OFFICES
                        ON deposits.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
                        WHERE 	deposits.collection_date > '2022-12-31'
                        GROUP BY
                        deposits.collection_date, 
                        deposits.branch_office_id""", ttl=600)
    return df_recaudacion

@st.cache_data(ttl=3600)
def kpi_deposito_dia():
    df_deposito = conn.query("""SELECT
                        date_format(`collections`.`created_at`,'%Y-%m-%d') AS Fecha, 
                        collections.branch_office_id AS branch_office_id, 	
                        sum(collections.gross_amount) AS recaudacion	
                        FROM collections LEFT JOIN cashiers
                        ON collections.cashier_id = cashiers.cashier_id
                        LEFT JOIN branch_offices
                        ON collections.branch_office_id = branch_offices.branch_office_id
                        WHERE
                        collections.special_cashier = 0 AND
                        cashiers.cashier_type_id <> 3 AND
                        collections.created_at > '2022-12-31'
                        GROUP BY
                        collections.created_at, 
                        collections.branch_office_id""", ttl=600)
    return df_deposito

@st.cache_data(ttl=3600)
def qry_branch_offices():
    sucursales = conn.query("SELECT * FROM QRY_BRANCH_OFFICES", ttl=600)
    return sucursales

@st.cache_data(ttl=3600)
def qry_periodos():
    periodo = conn.query("SELECT * FROM DM_PERIODO", ttl=600)
    return periodo

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)

df_recaudacion = kpi_recaudacion_dia()
df_deposito = kpi_deposito_dia()
df_periodo = qry_periodos()
df_sucursales = qry_branch_offices()

df_estatus = df_recaudacion.merge(df_deposito, on=['branch_office_id', 'Fecha'], how='left')
df_estatus['diferencia'] = df_estatus['recaudacion'] - df_estatus['deposito']

df_estatus = df_estatus.merge(df_sucursales[['branch_office_id', 'names', 'branch_office']], on='branch_office_id', how='left')

df_estatus['Fecha'] = pd.to_datetime(df_estatus['Fecha'])
df_periodo['Fecha'] = pd.to_datetime(df_periodo['Fecha'])

df_estatus['Fecha'] = df_estatus['Fecha'].dt.date
df_periodo['Fecha'] = df_periodo['Fecha'].dt.date
df_estatus = df_estatus.merge(df_periodo[['Fecha', 'Periodo', 'period', 'Año']], on='Fecha', how='left')

df_estatus.rename(columns={"branch_office": "sucursal",
                           "names": "supervisor",
                           "Periodo": "periodo",
                           "recaudacion": "recaudado",
                           "deposito": "depositado"
                           }, inplace=True)


ultimo_mes = df_estatus['periodo'].max()

# Crear el sidebar
st.sidebar.title('Filtros Disponibles')
supervisors = df_estatus['supervisor'].unique()
supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
branch_offices = df_estatus[df_estatus['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)

periodos = df_estatus['periodo'].unique()
periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=[ultimo_mes])

if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
    df_filtrado = df_estatus[
        (df_estatus['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
        (df_estatus['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
        (df_estatus['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)]
    #st.write(df_filtrado)
else:
    #st.write(df_estatus)
    pass


monto_recaudado = format_currency(df_filtrado['recaudado'].sum())
monto_depositado = format_currency(df_filtrado['depositado'].sum())
monto_diferencia = format_currency(df_filtrado['diferencia'].sum())


container = st.container()
# Agrega los estilos CSS a Streamlit
st.markdown(
            f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">           
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" integrity="sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
            """,unsafe_allow_html=True,)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
            f"""           
            <div class="card text-white bg-primary mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">RECAUDADO $</h5>
                <h3 class="card-title">{monto_recaudado}</h3>                                               
                </div>
            </div>
            """,unsafe_allow_html=True,)
with col2:
    st.markdown(
            f"""           
            <div class="card text-white bg-success mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">DEPOSITADO $</h5>
                <h3 class="card-title">{monto_depositado}</h3>                                               
                </div>
            </div>
            """,unsafe_allow_html=True,)
with col3:
    st.markdown(
            f"""           
            <div class="card text-white bg-secondary mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">DIFERENCIA $</h5>
                <h3 class="card-title">{monto_diferencia}</h3>                                               
                </div>
            </div>
            """,unsafe_allow_html=True,)


container = st.container()
with container:  

    # Agrupar por "sucursal" y calcular las sumas de "recaudado", "depositado" y "diferencia"
    df_agrupado = df_filtrado.groupby('sucursal').agg({
        'recaudado': 'sum',
        'depositado': 'sum',
        'diferencia': 'sum'
    })

    # Calcular el total de todas las sucursales y agregarlo como una fila al DataFrame
    total_general = df_agrupado.sum()
    df_total = pd.DataFrame({
        'recaudado': [total_general['recaudado']],
        'depositado': [total_general['depositado']],
        'diferencia': [total_general['diferencia']]
    }, index=['Total'])

    # Aplicar el formato de moneda a las columnas numéricas en df_agrupado y df_total
    df_agrupado['recaudado'] = df_agrupado['recaudado'].apply(format_currency)
    df_agrupado['depositado'] = df_agrupado['depositado'].apply(format_currency)
    df_agrupado['diferencia'] = df_agrupado['diferencia'].apply(format_currency)

    df_total['recaudado'] = df_total['recaudado'].apply(format_currency)
    df_total['depositado'] = df_total['depositado'].apply(format_currency)
    df_total['diferencia'] = df_total['diferencia'].apply(format_currency)

    # Establecer "sucursal" como el índice en df_agrupado
    df_agrupado.index.name = 'sucursal'

    # Concatenar df_total al final de df_agrupado para agregar la fila "Total"
    df_agrupado = pd.concat([df_agrupado, df_total])

    # Filtrar df_agrupado
    df_agrupado_filtrado = df_agrupado[df_agrupado['diferencia'] != "$0"]

    # Mostrar el DataFrame agrupado con "sucursal" como índice y la fila "Total"
    st.write(df_agrupado_filtrado)



    # Calcular los totales de las columnas numéricas en df_filtrado
    totales = df_filtrado[['recaudado', 'depositado', 'diferencia']].sum()

    # Crear una fila 'Total' con los totales y valores en blanco para 'Fecha' y 'sucursal'
    fila_total = pd.DataFrame({'Fecha': ['Total'], 
                            'sucursal': [''], 
                            'recaudado': [totales['recaudado']], 
                            'depositado': [totales['depositado']], 
                            'diferencia': [totales['diferencia']]})

    # Concatenar la fila 'Total' al DataFrame df_filtrado
    df_nuevo = pd.concat([df_filtrado, fila_total])

    columnas_deseadas = ["Fecha", "sucursal", "recaudado", "depositado", "diferencia"]
    df_nuevo = df_nuevo[columnas_deseadas]
    df_nuevo.set_index("Fecha", inplace=True)

    # Aplicar el formato de moneda a las columnas numéricas
    df_nuevo['recaudado'] = df_nuevo['recaudado'].apply(format_currency)
    df_nuevo['depositado'] = df_nuevo['depositado'].apply(format_currency)
    df_nuevo['diferencia'] = df_nuevo['diferencia'].apply(format_currency)

    df_nuevo_filtrado = df_nuevo[df_nuevo['diferencia'] != "$0"]

    # Mostrar el DataFrame con la fila 'Total'
    st.write(df_nuevo_filtrado)



