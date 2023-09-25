import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
 
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def kpi_ingresos_mes():
    df_ingresos = conn.query("""SELECT
	api_transactions.branch_office_id,
	api_transactions.cashier_id,
	cashiers.cashier,
	api_transactions.folio,
	api_transactions.total * 1 AS total,
	api_transactions.entrance_hour,
	api_transactions.exit_hour,
	HOUR ( api_transactions.exit_hour ) AS hora,
	DATE_FORMAT( api_transactions.created_at, '%Y-%m-%d' ) AS fecha 
FROM
	api_transactions
	LEFT JOIN cashiers ON api_transactions.cashier_id = cashiers.cashier_id 
WHERE
	api_transactions.created_at >= '2023-07-01 00:00:00' 
	AND cashiers.is_electronic_id = 1 
ORDER BY
	cashier_id,
	exit_hour    
    """, ttl=600)
    return df_ingresos

@st.cache_data(ttl=3600)
def qry_branch_offices():
    sucursales = conn.query("SELECT * FROM QRY_BRANCH_OFFICES", ttl=600)
    return sucursales


df_total = kpi_ingresos_mes()

container = st.container()
with container:
    st.title("GESTION DE OPERACIONES")
    st.header("Reporte de Venta por Hora") 
    st.markdown("---")
    st.write(df_total)