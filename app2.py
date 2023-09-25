import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def kpi_ingresos_mes():
    df_ingresos = conn.query("SELECT * FROM KPI_INGRESOS_IMG_MES", ttl=600)
    return df_ingresos

@st.cache_data(ttl=3600)
def qry_branch_offices():
    sucursales = conn.query("SELECT * FROM QRY_BRANCH_OFFICES", ttl=600)
    return sucursales

@st.cache_data(ttl=3600)
def qry_periodos():
    periodo = conn.query("SELECT * FROM DM_PERIODO", ttl=600)
    return periodo


@st.cache_data(ttl=3600)
def qry_ppto():
    ppto = conn.query("SELECT * FROM QRY_PPTO_DIA WHERE DATE >= '2023-01-01'", ttl=600)
    return ppto

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)

def calcular_variacion(df, columna_actual, columna_anterior):
    df = df.fillna(0)
    variacion = (df[columna_actual] / df[columna_anterior] - 1) * 100
    variacion = variacion.apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}%")
    return variacion

def calcular_ticket_promedio(df, columna_ingresos, columna_tickets):
    df = df.fillna(0)
    ticket_promedio = (df[columna_ingresos] / df[columna_tickets]).round(0)
    return ticket_promedio

df_total = kpi_ingresos_mes()

container = st.container()
with container:
    st.title("GESTION DE OPERACIONES")
    #st.markdown("---")
    ### INGRESOS ACTUAL 2023
    df_ingresos_2023 = df_total[(df_total["año"] == 2023)]
    columns_ingresos = ["periodo", "branch_office" , "ticket_number" , "Venta_Neta" , "Venta_SSS" , "Ingresos" , "Ingresos_SSS" ]
    df_ingresos_act = df_ingresos_2023[columns_ingresos]   
    ### INGRESOS ACTUAL 2022
    df_ingresos_2022 = df_total[(df_total["año"] == 2022)]
    df_ingresos_ant = df_ingresos_2022[columns_ingresos]
 
    df_ingresos_actual = df_ingresos_act.rename(columns={"ticket_number": "ticket_number_Act", 
                                        "Venta_Neta" : "Venta_Neta_Act" ,
                                        "Venta_SSS": "Venta_SSS_Act",
                                        "Ingresos" : "Ingresos_Act",
                                        "Ingresos_SSS" : "Ingresos_SSS_Act"})
    
    df_ingresos_anterior = df_ingresos_ant.rename(columns={"ticket_number": "ticket_number_Ant", 
                                            "Venta_Neta" : "Venta_Neta_Ant" ,
                                            "Venta_SSS": "Venta_SSS_Ant",
                                            "Ingresos" : "Ingresos_Ant",
                                            "Ingresos_SSS" : "Ingresos_SSS_Ant"})  
    
    merged_df = df_ingresos_actual.merge(df_ingresos_anterior, on=["branch_office", "periodo"], how="left")

    merged_df = merged_df.assign(
    var_SSS = calcular_variacion(merged_df, 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant'),
    var_Q = calcular_variacion(merged_df, 'ticket_number_Act', 'ticket_number_Ant'),
    ticket_prom_act = calcular_ticket_promedio(merged_df, 'Ingresos_Act', 'ticket_number_Act'),
    ticket_prom_ant = calcular_ticket_promedio(merged_df, 'Ingresos_Ant', 'ticket_number_Ant'))
    merged_df = merged_df.fillna(0) 


    df_ppto = qry_ppto()
    df_periodo = qry_periodos()   
    merged_ppto = df_ppto.merge(df_periodo, left_on='date', right_on='Fecha', how='left')
    df_group_ppto = merged_ppto.groupby(['Periodo', 'branch_office_id'])['ppto'].sum().reset_index()

    df_sucursales = qry_branch_offices()
    columns_sucursal = ["names", "branch_office_id","branch_office" , "principal" , "zone" , "segment"]
    df_sucursales = df_sucursales[columns_sucursal]
    df_sucursales.rename(columns={"names": "supervisor"}, inplace=True)

    df_ppto_final = df_group_ppto.merge(df_sucursales, left_on='branch_office_id', right_on='branch_office_id', how='left')
    df_ppto_final.rename(columns={"Periodo": "periodo"}, inplace=True)
    columns_in_final_ppto = ['periodo', 'branch_office', 'ppto']    
    df_ppto_final = df_ppto_final[columns_in_final_ppto]

    final_df = merged_df.merge(df_sucursales, on="branch_office", how="left")
    # Realizar el merge entre final_df y df_ppto_final
    final_df = final_df.merge(df_ppto_final, on=['branch_office', 'periodo'], how='left')
    final_df.rename(columns={"branch_office": "sucursal"}, inplace=True)
    final_df.rename(columns={"ppto": "Ppto_Ventas"}, inplace=True)
    final_df.rename(columns={"ticket_number_Act": "ticket_number"}, inplace=True)

    final_df = final_df.assign(
    desv = calcular_variacion(final_df, 'Ingresos_Act', 'Ppto_Ventas'))   


    columns_to_show = ['periodo' , 'sucursal' , 'supervisor' , 'Ingresos_Act', 'Ingresos_Ant', 
                       'Venta_Neta_Act', 'Venta_Neta_Ant' , 'ticket_prom_act',  'ticket_prom_ant' ,
                       'var_Q' ,'var_SSS', 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant', 'Ppto_Ventas', 'ticket_number', 'desv'] 

    columns_to_show_in_visualization = ['sucursal','periodo', 'Ingresos_Act', 'Ingresos_Ant','Ppto_Ventas', 'Venta_Neta_Act', 'Venta_Neta_Ant',
                                        'ticket_prom_act', 'ticket_prom_ant', 'var_Q', 'var_SSS', 
                                        'Ingresos_SSS_Act', 'Ingresos_SSS_Ant', 'desv','ticket_number']

    df_inicial_display = final_df[columns_to_show_in_visualization].copy()    

    periodos_2023_con_datos = df_total[df_total['año'] == 2023]['periodo'].unique()
    ultimo_periodo = periodos_2023_con_datos[-1]
    periodos_seleccionados_por_defecto = ultimo_periodo

    st.sidebar.title('Filtros Disponibles')    
    periodos = final_df['periodo'].unique()
    supervisors = final_df['supervisor'].unique()
    supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
    branch_offices = final_df[final_df['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
    branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
    periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=periodos_seleccionados_por_defecto)

    if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
        df_filtrado = final_df[
            (final_df['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
            (final_df['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
            (final_df['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)]
        df_filtrado = df_filtrado[columns_to_show]
        columns_to_exclude = ['periodo', 'sucursal', 'supervisor', 'ticket_prom_act', 'ticket_prom_ant', 'var_Q', 'var_SSS']
        sum_total = df_filtrado.drop(columns=columns_to_exclude).sum()
        sum_total_row = pd.Series({'periodo': 'Total', 'sucursal': '', 'supervisor': ''})
        sum_total_row = sum_total_row.append(sum_total)
        df_filtrado = df_filtrado.append(sum_total_row, ignore_index=True)
        # Crea un nuevo DataFrame con las columnas deseadas para df_filtrado
        df_filtrado_display = df_filtrado[columns_to_show_in_visualization].copy()        
    else:
        df_filtrado_display = df_inicial_display.copy()
 
    sum_df_filtrado = df_filtrado_display.sum()
   
    ventas_act_sum = sum_df_filtrado['Venta_Neta_Act']
    ingresos_act_sum = sum_df_filtrado['Ingresos_Act']
    ingresos_ppto_sum = sum_df_filtrado['Ppto_Ventas']   
    ticket_number = sum_df_filtrado['ticket_number']  
    sss_actual_sum = sum_df_filtrado['Ingresos_SSS_Act']    
    ventas_ant_sum = sum_df_filtrado['Venta_Neta_Ant']
    ingresos_ant_sum = sum_df_filtrado['Ingresos_Ant']
    sss_anterior_sum = sum_df_filtrado['Ingresos_SSS_Ant']
    var_sss = (sss_actual_sum/sss_anterior_sum-1) * 100
    desv_ppto = (ingresos_act_sum/ingresos_ppto_sum-1) * 100
    ticket_prom_sum = (ventas_act_sum / ticket_number)

    ingresos_act = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ingresos_Act'].values[0])
    ingresos_ant = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ingresos_Ant'].values[0])
    ingresos_ppto = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ppto_Ventas'].values[0])
    
    var_sss_formatted = format_percentage(var_sss)
    desv_formatted = format_percentage(desv_ppto)
    ticket_promedio_formatted = format_currency(ticket_prom_sum)

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
                <div class="card-body order-card text-center">
                <h5 class="card-title">INGRESOS ACTUAL</h5>
                <h2 class="card-title">{ingresos_act}</h2>                                               
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col2:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-green mb-3">
                <div class="card-body order-card text-center">
                <h5 class="card-title">INGRESOS ANTERIOR</h5>
                <h2 class="card-title">{ingresos_ant}</h2> 
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col3:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-yellow mb-3">
                <div class="card-body order-card text-center">
                <h5 class="card-title">INGRESOS PPTO</h5>
                <h2 class="card-title">{ingresos_ppto}</h2> 
                </div>
            </div>
            """,unsafe_allow_html=True,)
        
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-pink mb-3">
                <div class="card-body order-card text-center">
                <h5 class="card-title">VAR % SSS</h5>
                <h2 class="card-title">{var_sss_formatted}</h2> 
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col5:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-red mb-3">
                <div class="card-body order-card text-center">
                <h5 class="card-title">DESVIACION %</h5>
                <h2 class="card-title">{desv_formatted}</h2> 
                </div>
            </div>
            """,unsafe_allow_html=True,)
    with col6:
        st.markdown(
            f"""           
            <div class="card text-white bg-c-purple mb-3">
                <div class="card-body order-card text-center">               
                <h5 class="card-title">TICKET PROM</h5>
                <h2 class="card-title">{ticket_promedio_formatted}</h2> 
                </div>
            </div>
            """,unsafe_allow_html=True,)

    st.markdown("---")
    df_filtrado_display = df_filtrado_display.reset_index(drop=True)
    df_filtrado_display.set_index('sucursal', inplace=True)
    columnas_a_mostrar = ['periodo','Ingresos_Act', 'Ingresos_Ant', 'Ppto_Ventas', 'var_SSS', 'desv']

    ingresos_act_sum = sum_df_filtrado['Ingresos_Act']
    nuevo_var_SSS = (sss_actual_sum/sss_anterior_sum-1) * 100
    nueva_desv =  (ingresos_act_sum/ingresos_ppto_sum-1) * 100

    fila_personalizada = {
        'Ingresos_Act': (df_filtrado_display['Ingresos_Act'].sum())/2,
        'Ingresos_Ant': (df_filtrado_display['Ingresos_Ant'].sum())/2,
        'Ppto_Ventas': (df_filtrado_display['Ppto_Ventas'].sum())/2,
        'var_SSS': format_percentage(nuevo_var_SSS),
        'desv': format_percentage(nueva_desv)}
    df_filtrado_con_personalizada = df_filtrado_display[columnas_a_mostrar].iloc[:-1].append(pd.Series(fila_personalizada, name='Total'))
    # Mostrar el DataFrame resultante en Streamlit
    st.dataframe(df_filtrado_con_personalizada)

if __name__ == "__main__":
    st.title("Tu Segunda Aplicación de Streamlit")

    


    
    





