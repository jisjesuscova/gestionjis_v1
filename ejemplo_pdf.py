import streamlit as st
import pdfkit
from jinja2 import Environment, FileSystemLoader
import pandas as pd
conn = st.experimental_connection('mysql', type='sql')

# Ruta de la plantilla HTML
html_template_path = "template/plantilla_informe_ventas.html"


pdfkit_options = {
    'page-size': 'A4',
    'orientation': 'Landscape',
    'path': 'C:\Program Files\wkhtmltopdf'  # Reemplaza con la ruta correcta
}

@st.cache_data(ttl=3600)
def kpi_ingresos_mes():
    df_ingresos = conn.query("SELECT * FROM KPI_INGRESOS_IMG_ACUM", ttl=600)
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
    ppto = conn.query("""
    SELECT * FROM QRY_PPTO_DIA
    WHERE MONTH(`QRY_PPTO_DIA`.`DATE`) = ((MONTH(curdate()-1))) 
    AND YEAR(`QRY_PPTO_DIA`.`DATE`) = YEAR(CURDATE()) 
    AND DAY(`QRY_PPTO_DIA`.`DATE`) <= DAY(curdate()-1)
    ORDER BY date asc """, ttl=600)
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

    st.markdown("---")
    df_filtrado_display = df_inicial_display.reset_index(drop=True)
    df_filtrado_display.set_index('sucursal', inplace=True)
    columnas_a_mostrar = ['periodo','Ingresos_Act', 'Ingresos_Ant', 'Ppto_Ventas', 'var_SSS', 'desv']

    ingresos_act_sum = df_inicial_display['Ingresos_Act']
    sss_actual_sum = df_inicial_display['Ingresos_SSS_Act']   
    sss_anterior_sum = df_inicial_display['Ingresos_SSS_Ant']
    ingresos_ppto_sum = df_inicial_display['Ppto_Ventas']   
    nuevo_var_SSS = (sss_actual_sum/sss_anterior_sum-1) * 100
    nueva_desv =  (ingresos_act_sum/ingresos_ppto_sum-1) * 100
    
    st.dataframe(df_filtrado_display[columnas_a_mostrar])


pdfkit_options = {
    'page-size': 'A4',
    'orientation': 'Landscape',
    'path': 'C://Program Files//wkhtmltopdf//bin/'  # Reemplaza con la ruta correcta
}


# Ruta para guardar el archivo PDF
output_pdf_path = 'informe_ventas.pdf'

# Convierte la plantilla HTML a PDF
pdfkit.from_file(html_template_path, output_pdf_path, options=pdfkit_options)

# Indica que el archivo PDF se ha generado
st.markdown(f"El archivo PDF se ha generado con éxito en: {output_pdf_path}")


  

    