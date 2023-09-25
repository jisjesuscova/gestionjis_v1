import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#solo streamlit
st.set_page_config(layout="wide")
st.title('Indicadores de Gastos')

# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def eerr():
    df_eerr = conn.query("SELECT Grupo,Cuentas,Supervisor,Sucursal, Meses, Monto FROM QRY_TP_EERR WHERE `Año` = 2023 and Grupo <> '90 - Extras' and Sucursal <>  'Ajuste COQUIMBO'", ttl=600)
    return df_eerr

# Obtener el DataFrame original
df_original = eerr()
st.markdown("---")
# Crear un contenedor para todo el contenido
container = st.container()
st.subheader("Detalle de Gastos")
st.markdown("---")

with container:
    resultado = df_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
    resultado.loc['Resultado Operacional'] = resultado.sum()
    ingresos = resultado.loc['10 - INGRESOS']

    # Calcular el porcentaje de cada grupo respecto a los ingresos y agregarlo como nuevas columnas
    for mes in ingresos.index:
        resultado[mes + ' %'] = round((resultado[mes] / ingresos[mes]) * 100, 2).apply(lambda x: f'{x:.2f}%')

    # Reordenar las columnas
    column_order = []
    for mes in ingresos.index:
        column_order.append(mes)
        column_order.append(mes + ' %')
    resultado = resultado[column_order]
    resultado = resultado.sort_index()
    st.dataframe(resultado, width=0)

with st.expander("Arriendos"):  
    col1, col2 = st.columns([5, 3])
    with col1: 
        df_arriendo = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['70 - ARRIENDOS', '10 - INGRESOS']))]
        df2 = df_arriendo.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('70 - ARRIENDOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
    
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['70 - ARRIENDOS'],
                                    name="Arriendos", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)


    with col2:
        df_arriendo = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['70 - ARRIENDOS', '10 - INGRESOS']))]
        df2 = df_arriendo.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('70 - ARRIENDOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        # Reiniciar el índice del DataFrame
        #df2.reset_index(inplace=True)
        st.dataframe(df2, width=0)

with st.expander("Remuneraciones"):  
    col1, col2 = st.columns([5, 3])
    with col1: 
        df_remuneraciones = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['60 - REMUNERACION', '10 - INGRESOS']))]
        df2 = df_remuneraciones.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('60 - REMUNERACION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
    
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['60 - REMUNERACION'],
                                    name="Remuneraciones", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)


    with col2:
        df_remuneraciones = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['60 - REMUNERACION', '10 - INGRESOS']))]
        df2 = df_remuneraciones.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('60 - REMUNERACION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        # Reiniciar el índice del DataFrame
        #df2.reset_index(inplace=True)
        st.dataframe(df2, width=0)

with st.expander("Materiales"):  
    col1, col2 = st.columns([5, 3])
    with col1: 
        df_materiales = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['20 - MATERIALES', '10 - INGRESOS']))]
        df2 = df_materiales.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('20 - MATERIALES')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
    
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['20 - MATERIALES'],
                                    name="Materiales", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)


    with col2:
        df_materiales = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['20 - MATERIALES', '10 - INGRESOS']))]
        df2 = df_materiales.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('20 - MATERIALES')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        # Reiniciar el índice del DataFrame
        #df2.reset_index(inplace=True)
        st.dataframe(df2, width=0)

with st.expander("Mantención"):  
    col1, col2 = st.columns([5, 3])
    with col1: 
        df_mantencion = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['30 - MANTENCION', '10 - INGRESOS']))]
        df2 = df_mantencion.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('30 - MANTENCION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
    
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['30 - MANTENCION'],
                                    name="Mantención", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)


    with col2:
        df_mantencion = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['30 - MANTENCION', '10 - INGRESOS']))]
        df2 = df_mantencion.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('30 - MANTENCION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        # Reiniciar el índice del DataFrame
        #df2.reset_index(inplace=True)
        st.dataframe(df2, width=0)

with st.expander("Servicios"):  
    col1, col2 = st.columns([5, 3])
    with col1: 
        df_servicios = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['40 - SERVICIOS', '10 - INGRESOS']))]
        df2 = df_servicios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('40 - SERVICIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
    
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['40 - SERVICIOS'],
                                    name="Servicios", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)


    with col2:
        df_servicios = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['40 - SERVICIOS', '10 - INGRESOS']))]
        df2 = df_servicios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('40 - SERVICIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        # Reiniciar el índice del DataFrame
        #df2.reset_index(inplace=True)
        st.dataframe(df2, width=0)

with st.expander("Varios"):  
    col1, col2 = st.columns([5, 3])
    with col1: 
        df_varios = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['50 - VARIOS', '10 - INGRESOS']))]
        df2 = df_varios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('50 - VARIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
    
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['50 - VARIOS'],
                                    name="Varios", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)


    with col2:
        df_varios = df_original[df_original['Grupo'].apply(lambda val: any(val == s for s in ['50 - VARIOS', '10 - INGRESOS']))]
        df2 = df_varios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('50 - VARIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        # Reiniciar el índice del DataFrame
        #df2.reset_index(inplace=True)
        st.dataframe(df2, width=0)


with st.expander("Resultado Operacional"):  
    col1, col2 = st.columns([5, 3])
    with col1:
        # Filtrar y pivotear los datos
        df_total = df_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
        df_total.loc['R.O.P'] = df_total.sum() 

        # Filtrar las filas correspondientes a '10 - INGRESOS' y 'R.O.P'
        filas_seleccionadas = ['10 - INGRESOS', 'R.O.P']
        df_seleccion = df_total.loc[filas_seleccionadas]

        # Calcular las sumas de las columnas y agregar una nueva columna 'Total'
        #df_seleccion = df_seleccion.assign(Total=df_seleccion.sum(axis=1)) 

        # Calcular la columna 'part%'
        df_seleccion.loc['Part%'] = round((df_seleccion.loc['R.O.P'] / df_seleccion.loc['10 - INGRESOS']) * 100, 2).apply(lambda x: f'{x:.2f}%')
        
        #st.dataframe(df_seleccion.T, width=0, hide_index=False)   
        df_nuevo = df_seleccion.T.copy()

        # Crear el gráfico con subplots       
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df_nuevo.index, y=df_nuevo['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='rgb(51, 153, 255)'))
        fig_combined.add_trace(go.Bar(x=df_nuevo.index, y=df_nuevo['R.O.P'],
                                    name="Total", offsetgroup=0, marker_color='rgba(255, 128, 0,1)'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df_nuevo.index, y=df_nuevo['Part%'],
                                        mode="lines+markers", name="% Part", line=dict(width=4, color="red"), marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)), yaxis="y2"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        
        st.plotly_chart(fig_combined)

    with col2:
        # Filtrar y pivotear los datos
        df_total = df_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
        df_total.loc['R.O.P'] = df_total.sum() 

        # Filtrar las filas correspondientes a '10 - INGRESOS' y 'R.O.P'
        filas_seleccionadas = ['10 - INGRESOS', 'R.O.P']
        df_seleccion = df_total.loc[filas_seleccionadas]

        # Calcular las sumas de las columnas y agregar una nueva columna 'Total'
        df_seleccion = df_seleccion.assign(Total=df_seleccion.sum(axis=1)) 

        # Calcular la columna 'part%'
        df_seleccion.loc['Part%'] = round((df_seleccion.loc['R.O.P'] / df_seleccion.loc['10 - INGRESOS']) * 100, 2).apply(lambda x: f'{x:.2f}%')
        
        #st.dataframe(df_seleccion.T, width=0, hide_index=False)   
        df_nuevo = df_seleccion.T.copy()
        st.dataframe(df_nuevo,  width=0)

