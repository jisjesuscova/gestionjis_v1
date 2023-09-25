import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
 
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def kpi_dte_mes():
    df_dte = conn.query("SELECT * FROM KPI_DTES_MES", ttl=600)
    return df_dte

@st.cache_data(ttl=3600)
def qry_branch_offices():
    sucursales = conn.query("SELECT * FROM QRY_BRANCH_OFFICES", ttl=600)
    return sucursales

@st.cache_data(ttl=3600)
def qry_periodos():
    periodo = conn.query("SELECT Periodo,Trimestre, period,Año FROM DM_PERIODO GROUP BY period", ttl=600)
    return periodo

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)

df_dtes = kpi_dte_mes()
df_periodo = qry_periodos()
df_sucursales = qry_branch_offices()

merged_df = df_dtes.merge(df_sucursales, on='branch_office_id', how='left')
merged_df = merged_df.merge(df_periodo, left_on='period', right_on='period', how='left')
merged_df = merged_df.rename(columns={"rut_x": "rut", 
                                      "branch_office" : "sucursal" ,
                                      "names": "supervisor",
                                      "dte_type_id" : "tipo",
                                      "amount": "monto"})

columns_mostrar = ["rut", "cliente" , "folio" , "sucursal" ,"supervisor" , "tipo" , "status" , "monto", "Periodo" , "Año", "comment"]
df_status_dte = merged_df[columns_mostrar]   

df_status_dte['contador'] = df_status_dte['tipo'].apply(lambda x: 1 if x in [33, 39] else 1)
df_status_dte['link'] = df_status_dte['comment'].apply(lambda x: 'sí' if 'Código de autorización' in str(x) else 'no')
df_status_dte['folio'] = df_status_dte['folio'].astype(str)
ultimo_mes = df_status_dte['Periodo'].max()

st.sidebar.title('Filtros Disponibles')    
periodos = df_status_dte['Periodo'].unique()
supervisors = df_status_dte['supervisor'].unique()
supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
branch_offices = df_status_dte[df_status_dte['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=[ultimo_mes])



container = st.container()
with container:
    if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados or status_seleccionados:
        df_filtrado = df_status_dte[
            (df_status_dte['Periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
            (df_status_dte['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
            (df_status_dte['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True) ]
        
        st.title("GESTION DE ABONADOS")
        st.markdown("---")
        #st.write(df_filtrado)
    else:
        st.title("GESTION DE ABONADOS")
        st.markdown("---")
        #st.write(df_status_dte)   

    monto_pagada = format_currency(df_filtrado[df_filtrado['status'] == 'Imputada Pagada']['monto'].sum())
    monto_por_pagar = format_currency(df_filtrado[df_filtrado['status'] == 'Imputada por Pagar']['monto'].sum())
    cantidad_pagada = df_filtrado[df_filtrado['status'] == 'Imputada Pagada']['contador'].sum()
    cantidad_por_pagar = df_filtrado[df_filtrado['status'] == 'Imputada por Pagar']['contador'].sum()
    cantidad_link_si = df_filtrado[df_filtrado['link'] == 'sí']['contador'].sum()
    
    df_agrupado = df_filtrado.sum()
    contador_sum = df_agrupado['contador']
    monto_sum = format_currency(df_agrupado['monto'])
    porc_pagados = format_percentage((cantidad_pagada  / contador_sum)*100)
    porc_por_pagar = format_percentage((cantidad_por_pagar  / contador_sum)*100)
    porc_link = format_percentage((cantidad_link_si  / contador_sum)*100)

    #Link de Boostrap y FontAwesone
    style = """
            .order-card {
                color: #fff;
            }
            .bg-c-blue {
                background: linear-gradient(45deg,#4099ff,#73b4ff);
            }
            .bg-c-green {
                background: linear-gradient(45deg,#2ed8b6,#59e0c5);
            }
            .bg-c-yellow {
                background: linear-gradient(45deg,#FFB64D,#ffcb80);
            }
            .bg-c-pink {
                background: linear-gradient(45deg,#FF5370,#ff869a);
            } 
            .bg-c-red {
                background: linear-gradient(45deg,#FF6666,#FFccca);
            }  
            .bg-c-purple {
                background: linear-gradient(45deg,#9933ff,#ccccfa);
            }                     
            """
    # Agrega los estilos CSS a Streamlit
    st.markdown(
                f"""
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">           
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" integrity="sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                """,
                unsafe_allow_html=True,)
    st.write(f"<style>{style}</style>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-blue mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">PAGADAS $</h5>
                <h3 class="card-title">{monto_pagada}</h3>                                               
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col2:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-green mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">POR PAGAR $</h5>
                <h3 class="card-title">{monto_por_pagar}</h3> 
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col3:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-yellow mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">TOTAL $</h5>
                <h3 class="card-title">{monto_sum}</h3>   
                </div>
            </div>
            """,unsafe_allow_html=True,)
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-pink mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">N° PAGADA</h5>
                <h3 class="card-title">{cantidad_pagada}</h3>                                              
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col2:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-purple mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">N° POR PAGAR</h5>
                <h3 class="card-title">{cantidad_por_pagar}</h3>                                              
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col3:
        st.markdown(
            f"""           
            <div class="card text-white bg-secondary mb-3">
                <div class="text-center pt-1">
                <h5 class="card-text">TOTAL N°</h5>
                <h3 class="card-title">{contador_sum}</h3>                                               
                </div>
            </div>
            """,unsafe_allow_html=True,)
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""           
            <div class="card text-white bg-success mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">% PAGADOS</h5>
                <h3 class="card-title">{porc_pagados}</h3>                                              
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col2:
        st.markdown(
            f"""           
            <div class="card text-white bg-info mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">% POR PAGAR</h5>
                <h3 class="card-title">{porc_por_pagar}</h3>                                              
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col3:
        st.markdown(
            f"""           
            <div class="card text-white bg-primary mb-3">
                <div class="text-center">
                <h5 class="card-text pt-1">% POR LINK</h5>
                <h3 class="card-title">{porc_link}</h3>                                              
                </div>
            </div>
            """,unsafe_allow_html=True,)
        

container = st.container()
with container:
    df_nuevo = df_filtrado[['folio', 'rut', 'cliente', 'sucursal', 'tipo', 'monto', 'status']].set_index('folio').sort_values(by='monto', ascending=False)  
    

    pivot_monto = df_filtrado.pivot_table(values='monto', index='supervisor', columns='status', aggfunc='sum', fill_value=0)
    pivot_monto['Total'] = pivot_monto.sum(axis=1)
    pivot_monto = pivot_monto.sort_values(by='Imputada Pagada', ascending=False)
    pivot_contador = df_filtrado.pivot_table(values='contador', index='supervisor', columns='status', aggfunc='sum', fill_value=0)
    pivot_contador['Total'] = pivot_contador.sum(axis=1)
    pivot_contador = pivot_contador.sort_values(by='Imputada Pagada', ascending=False)
    merged_pivot = pd.merge(pivot_monto, pivot_contador, on='supervisor', suffixes=('_monto', '_contador'))

    merged_pivot.loc['Total'] = merged_pivot.sum()
    merged_pivot = merged_pivot.rename(columns={"Imputada Pagada_monto": "Pagada $", 
                                                "Imputada por Pagar_monto": "Por Pagar $",
                                                "Total_monto": "Total $",
                                                "Imputada Pagada_contador": "Pagada N°",
                                                "Imputada por Pagar_contador": "Por Pagar N°",
                                                "Total_contador": "Total N°"
                                                })

    st.write(merged_pivot)

    pivot_monto_sucursal = df_filtrado.pivot_table(values='monto', index='sucursal', columns='status', aggfunc='sum', fill_value=0)
    pivot_monto_sucursal['Total'] = pivot_monto_sucursal.sum(axis=1)

    pivot_contador_sucursal = df_filtrado.pivot_table(values='contador', index='sucursal', columns='status', aggfunc='sum', fill_value=0)
    pivot_contador_sucursal['Total'] = pivot_contador_sucursal.sum(axis=1)

    merged_pivot_sucursal = pd.merge(pivot_monto_sucursal, pivot_contador_sucursal, on='sucursal', suffixes=('_monto', '_contador'))

    merged_pivot_sucursal.loc['Total'] = merged_pivot_sucursal.sum()
    merged_pivot_sucursal = merged_pivot_sucursal.rename(columns={"Imputada Pagada_monto": "Pagada $", 
                                                                "Imputada por Pagar_monto": "Por Pagar $",
                                                                "Total_monto": "Total $",
                                                                "Imputada Pagada_contador": "Pagada N°",
                                                                "Imputada por Pagar_contador": "Por Pagar N°",
                                                                "Total_contador": "Total N°"
                                                            })
    
    st.write(merged_pivot_sucursal)
    st.write(df_nuevo)  
 




  


