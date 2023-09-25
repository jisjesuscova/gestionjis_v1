import streamlit as st
import pandas as pd
import plotly.express as px


def show_eerr_page():
    # Inicializacion de conexion.
    conn = st.experimental_connection('mysql', type='sql')

    @st.cache_data(ttl=3600)
    def eerr():
        df_eerr = conn.query(
            "SELECT Grupo,Cuentas,Supervisor,Sucursal, Meses, Monto FROM QRY_TP_EERR WHERE `Año` = 2023 and Grupo <> '90 - Extras' and Sucursal <>  'Ajuste COQUIMBO'", ttl=600)
        return df_eerr

    # Obtener el DataFrame original
    df_original = eerr()

    # Crear un contenedor para todo el contenido
    container = st.container()

    with container:
        selected_meses = st.sidebar.multiselect(
            "Seleccionar Meses", df_original['Meses'].unique())
        selected_grupos = st.sidebar.multiselect(
            "Seleccionar Grupos", df_original['Grupo'].unique())
        selected_supervisores = st.sidebar.multiselect(
            "Seleccionar Supervisores", df_original['Supervisor'].dropna().unique())

        # Nuevo filtro para las cuentas basado en los grupos seleccionados
        if selected_grupos:
            cuentas_filtradas = df_original[df_original['Grupo'].isin(
                selected_grupos)]['Cuentas'].unique()
        else:
            cuentas_filtradas = df_original['Cuentas'].unique()
            selected_cuentas = st.sidebar.multiselect(
            "Seleccionar Cuentas", cuentas_filtradas)

        # Nuevo filtro para las sucursales basado en los supervisores seleccionados
        if selected_supervisores:
            sucursales_filtradas = df_original[df_original['Supervisor'].isin(
                selected_supervisores)]['Sucursal'].unique()
        else:
            sucursales_filtradas = df_original['Sucursal'].unique()
        selected_sucursales = st.sidebar.multiselect(
            "Seleccionar Sucursales", sucursales_filtradas)

        # Inicializar un DataFrame que contenga todos los datos no filtrados
        eerr_df = df_original.copy()

        # Aplicar los filtros seleccionados individualmente al DataFrame original
        if selected_meses:
            eerr_df = eerr_df[eerr_df['Meses'].isin(selected_meses)]
        if selected_grupos:
            eerr_df = eerr_df[eerr_df['Grupo'].isin(selected_grupos)]
        if selected_supervisores:
            eerr_df = eerr_df[eerr_df['Supervisor'].isin(selected_supervisores)]
        if selected_cuentas:
            eerr_df = eerr_df[eerr_df['Cuentas'].isin(selected_cuentas)]
        if selected_sucursales:
            eerr_df = eerr_df[eerr_df['Sucursal'].isin(selected_sucursales)]

        # Mostrar solo las columnas seleccionadas
        columns_to_display = ['Grupo', 'Cuentas', 'Meses', 'Monto']
        columns_to_plot = ['Grupo', 'Meses', 'Monto']
        filtered_plot = eerr_df[columns_to_plot]
        filtered_df = eerr_df[columns_to_display]

        

        # Calcular la sumatoria después de aplicar los filtros
        sum_row = filtered_df[columns_to_display].sum(numeric_only=True)
        sum_row['Grupo'] = 'Total General'

        # Agregar la fila de sumatoria al DataFrame filtrado
        filtered_df = filtered_df.append(sum_row, ignore_index=True)

        

        # Agrupar el DataFrame filtered_plot por 'Grupo' y 'Meses' y sumar el 'Monto'
        grouped_plot = filtered_plot.groupby(['Grupo', 'Meses']).sum().reset_index()

        # Filtrar el DataFrame para excluir 'Total General'
        grouped_plot = grouped_plot[grouped_plot['Grupo'] != 'Total General']

        # Crear el gráfico de columnas apiladas
        fig = px.bar(grouped_plot, x='Meses', y='Monto', color='Grupo', barmode='relative')

        # Ajustar el diseño del gráfico
        fig.update_layout(barmode='relative', xaxis_title='Meses', yaxis_title='Monto', legend_title='Grupo')

        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(filtered_df)

# Llamamos a la función para mostrar la página
show_eerr_page()
