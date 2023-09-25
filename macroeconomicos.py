import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale

# Establecer la localización para formatear como moneda
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
periodo_img = '07 - Julio'
conn = st.experimental_connection('mysql', type='sql')
csv_path = "data/ipc.csv"
csv_path_imacec = "data/imacec.csv"
csv_path_uf = "data/uf.csv"
csv_path_desempleo = "data/desempleo.csv"
csv_path_anac = "data/anac.csv"

@st.cache_data(ttl=3600)
def ingreso_acum_mes_actual():
    df_acum_mes_actual = conn.query("SELECT * FROM KPI_INGRESOS_IMG_MES", ttl=600)
    return df_acum_mes_actual

@st.cache_data(ttl=3600)
def qry_branch_offices():
    sucursales = conn.query("SELECT * FROM QRY_BRANCH_OFFICES", ttl=600)
    return sucursales

@st.cache_data(ttl=3600)
def eerr():
    df_eerr = conn.query("SELECT Grupo,Cuentas,Supervisor,Sucursal,año, Meses, Monto FROM QRY_TP_EERR WHERE `Año` >= 2022 and Grupo <> '90 - Extras' and Sucursal <>  'Ajuste COQUIMBO'", ttl=600)
    return df_eerr


@st.cache_data(ttl=3600)
def RRHH_dotacion():
    df_dotacion_trabajadores = conn.query("""SELECT
	RRHH_Dotacion.rut, 
	RRHH_Dotacion.item, 
	RRHH_Dotacion.grupo, 
	RRHH_Dotacion.cantidad, 
	DM_PERIODO.Periodo as periodo,
	YEAR(RRHH_Dotacion.fecha) AS año
    FROM RRHH_Dotacion LEFT JOIN DM_PERIODO
    ON RRHH_Dotacion.fecha = DM_PERIODO.Fecha""", ttl=600)
    return df_dotacion_trabajadores

container = st.container()

meses_mapping = {
    "Enero": "01 - Enero",
    "Febrero": "02 - Febrero",
    "Marzo": "03 - Marzo",
    "Abril": "04 - Abril",
    "Mayo": "05 - Mayo",
    "Junio": "06 - Junio",
    "Julio": "07 - Julio",
    "Agosto": "08 - Agosto",
    "Septiembre": "09 - Septiembre",
    "Octubre": "10 - Octubre",
    "Noviembre": "11 - Noviembre",
    "Diciembre": "12 - Diciembre"
}
with container:
    st.title("INFORME MENSUAL DE GESTIÓN 2023")
    st.markdown("---")
with container: #1- INDICADORES MACROECONÓMICOS
    # Datos indice IPC 
    st.header("1.- INDICADORES MACROECONÓMICOS  	:chart_with_upwards_trend:")

    df = pd.read_csv(csv_path, sep=";")
    df["mes"] = df["mes"].map(meses_mapping)
    df["indice_ipc"] = df["indice_ipc"].str.replace(",", ".").astype(float)
    df_filtered = df[ (df["año"] == 2022) | (df["año"] == 2023)]
    pivot_df = df_filtered.fillna(0)
    pivot_df["var"] = ((pivot_df["indice_ipc"] / pivot_df["indice_ipc"].shift(1)) - 1) * 100
    pivot_df["var"] = pivot_df["var"].apply(lambda x: f"{x:.1f} %")                
    pivot_table = pivot_df.pivot_table(index='mes', columns='año', values='var', aggfunc='first', fill_value='0')
    #st.table(pivot_table)    

    # grafico variación de IPC
    fig = px.line(
        pivot_df,
        x="mes",
        y="var",
        color="año",
        title="1.- Variaciones Indice Precio al Consumidor IPC",
        line_shape="linear",
        color_discrete_map={2022: "orange", 2023: "blue"})
    data_2022 = pivot_df[pivot_df['año'] == 2022]
    fig.add_trace(
        px.line(data_2022, x="mes", y="var", color_discrete_sequence=['orange'])
        .update_traces(
            mode="markers+lines+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            texttemplate="%{text}",
            textposition="bottom center",
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in data_2022["var"]]
        ).data[0])
    data_2023 = pivot_df[pivot_df['año'] == 2023]
    fig.add_trace(
        px.line(data_2023, x="mes", y="var", color_discrete_sequence=['blue'])
        .update_traces(
            mode="markers+lines+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            texttemplate="%{text}",
            textposition="top center",
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in data_2023["var"]]).data[0])
    st.plotly_chart(fig)
   
    # Datos indice UF    
    #st.write("Variaciones UF:")      
    df = pd.read_csv(csv_path_uf, sep=";")                
    df["mes"] = df["mes"].map(meses_mapping)
    df["indice_uf"] = df["indice_uf"].str.replace(",", ".").astype(float)
    df["indice_dolar"] = df["indice_dolar"].str.replace(",", ".").astype(float)
    df_filtered = df[df["año"] == 2023]
    df_filtered = df_filtered[["mes", "indice_uf", "utm", "indice_dolar"]]
    df_filtered["indice_uf"] = df_filtered["indice_uf"].fillna(0)
    df_filtered["indice_dolar"] = df_filtered["indice_dolar"].fillna(0)
    df_filtered["indice_uf"] = df_filtered["indice_uf"].astype(int)
    df_filtered["indice_dolar"] = df_filtered["indice_dolar"].astype(int)
    df_filtered["indice_uf"] = df_filtered["indice_uf"].round(0)
    df_filtered["indice_dolar"] = df_filtered["indice_dolar"].round(0)
    df_filtered["UF"] = df_filtered["indice_uf"].apply(lambda x: "${:,}".format(x))
    df_filtered["UTM"] = df_filtered["utm"].apply(lambda x: "${:,}".format(x))
    df_filtered["DOLAR"] = df_filtered["indice_dolar"].apply(lambda x: "${:,}".format(x))             
    #st.table(df_filtered[["mes", "UF", "UTM", "DOLAR"]])
  
    # grafico variación UF
    fig_indice_uf = go.Figure()
    fig_indice_uf.add_trace(
        go.Scatter(
            x=df_filtered["mes"],
            y=df_filtered["indice_uf"],
            name="Indice UF",
            line=dict(color="orange"),
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in df_filtered["UF"]],
            textposition="top center"))

    fig_indice_uf.update_layout(
        title="2.- Evolución UF en 2023",
        xaxis=dict(title="Mes"),
        yaxis=dict(title="Indice UF", tickformat="$,"),
        legend=dict(x=0, y=1.1))

    st.plotly_chart(fig_indice_uf)
    
    # grafico evolución UTM
    fig_utm = go.Figure()
    fig_utm.add_trace(
        go.Scatter(
            x=df_filtered["mes"],
            y=df_filtered["utm"],
            name="UTM",
            line=dict(color="blue"),
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in df_filtered["UTM"]],
            textposition="top center"))
    fig_utm.update_layout(
        title="3.- Evolución UTM en 2023",
        xaxis=dict(title="Mes"),
        yaxis=dict(title="UTM", tickformat="$,"),
        legend=dict(x=0, y=1.1))
    st.plotly_chart(fig_utm)

    # grafico evolución Dolar
    fig_indice_dolar = go.Figure()
    fig_indice_dolar.add_trace(
        go.Scatter(
            x=df_filtered["mes"],
            y=df_filtered["indice_dolar"],
            name="Indice Dólar",
            line=dict(color="green"),
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in df_filtered["DOLAR"]],
            textposition="top center"))
    fig_indice_dolar.update_layout(
        title="4.- Evolución Dólar en 2023",
        xaxis=dict(title="Mes"),
        yaxis=dict(title="Indice Dólar", tickformat="$,"),
        legend=dict(x=0, y=1.1))

    st.plotly_chart(fig_indice_dolar)    

    df_imacec = pd.read_csv(csv_path_imacec, sep=";")
    df_imacec["mes"] = df_imacec["mes"].map(meses_mapping)
    df_imacec["indice_imacec"] = df_imacec["indice_imacec"].str.replace(",", ".").astype(float)
    df_imacec = df_imacec.drop(columns="key")
    df_imacec = df_imacec.fillna(0)
    df_filtered_imacec = df_imacec[df_imacec["año"].isin([2022, 2023])]
    df_pivot_imacec = df_filtered_imacec.pivot(index="mes", columns="año", values="indice_imacec")
    df_pivot_imacec["var"] = ((df_pivot_imacec[2023] / df_pivot_imacec[2022]) - 1) * 100
    df_pivot_imacec["var"] = df_pivot_imacec["var"].fillna(0).apply(lambda x: f"{x:.1f} %")
    replacement_value = " "
    df_pivot_imacec["var"] = df_pivot_imacec["var"].replace("0.0 %", replacement_value)
    df_pivot_imacec = df_pivot_imacec[["var"]]
    #st.table(df_pivot_imacec)

    # Filtrar los meses que tienen valor en la columna 'var'
    df_filtered_months = df_pivot_imacec[df_pivot_imacec['var'] != replacement_value]

    # Crear el gráfico solo para los meses con valor en la columna 'var'
    fig_variaciones_imacec = go.Figure()
    fig_variaciones_imacec.add_trace(
        go.Scatter(
            x=df_filtered_months.index,
            y=df_filtered_months['var'],
            name='Variaciones IMACEC',
            line=dict(color='purple'),
            mode='lines+markers+text',
            marker=dict(symbol='circle', size=8, line=dict(color='white', width=1)),
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in df_filtered_months['var']],
            textposition='top center'))

    fig_variaciones_imacec.update_layout(
        title='5.- Indicador Mensual de Actividad Económica - IMACEC en 2023',
        xaxis=dict(title='Mes'),
        yaxis=dict(title='Variación IMACEC (%)'),
        legend=dict(x=0, y=1.1))

    st.plotly_chart(fig_variaciones_imacec)
    # Datos indice DESEMPLEO
    df_desempleo= pd.read_csv(csv_path_desempleo, sep=";")    
    df_desempleo["mes"] = df_desempleo["mes"].map(meses_mapping)              
    df_desempleo = df_desempleo.drop(columns="key")   
    df_desempleo = df_desempleo.fillna(0) 
    df_desempleo["fuerza_trabajo"] = df_desempleo["fuerza_trabajo"].str.replace(",", ".").astype(float)
    df_desempleo["desocupados"] = df_desempleo["desocupados"].str.replace(",", ".").astype(float)

    df_filtered = df_desempleo[df_desempleo["año"] == 2023] 
    df_filtered["fuerza_trabajo"] = df_filtered["fuerza_trabajo"].fillna(0)
    df_filtered["desocupados"] = df_filtered["desocupados"].fillna(0)         
    df_filtered["fuerza_trabajo"] = df_filtered["fuerza_trabajo"].astype(int)
    df_filtered["desocupados"] = df_filtered["desocupados"].astype(int)                
    df_filtered["fuerza_trabajo"] = df_filtered["fuerza_trabajo"].round(0)
    df_filtered["desocupados"] = df_filtered["desocupados"].round(0)                
    df_filtered["Desempleo %"] = (df_filtered["desocupados"]/ df_filtered["fuerza_trabajo"] ) * 100
    df_filtered["Desempleo %"] = df_filtered["Desempleo %"].apply(lambda x: f"{x:.1f} %")
    #st.table(df_filtered[["mes", "Desempleo %"]])
    # grafico evolución DESEMPLEO
    fig_desempleo = go.Figure()
    fig_desempleo.add_trace(
        go.Scatter(
            x=df_filtered["mes"],
            y=df_filtered["Desempleo %"],
            name="Desempleo %",
            line=dict(color="red"),
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in df_filtered["Desempleo %"]],
            textposition="top center"))

    fig_desempleo.update_layout(
        title="6.- Evolución Tasa de Desempleo Nacional",
        xaxis=dict(title="Mes"),
        yaxis=dict(title="Desempleo %"),
        legend=dict(x=0, y=1.1))
    st.plotly_chart(fig_desempleo)

with container: #2- INDICADORES MICROECONÓMICOS
    st.header("2.- INDICADORES MICROECONÓMICOS :bar_chart:") 
    # Datos indice ANAC
    df_anac = pd.read_csv(csv_path_anac, sep=";")
    df_anac["mes"] = df_anac["mes"].map(meses_mapping)
    df_anac = df_anac.drop(columns="key")
    df_anac = df_anac.fillna(0)
    df_filtered = df_anac[df_anac["año"] == 2023]
    df_filtered["Total"] = df_filtered["pasajeros"] + df_filtered["suv"] + df_filtered["camioneta"] + df_filtered["comercial"]
    #st.write(df_filtered)
    df_copied = df_anac.copy()  # Copia del DataFrame original
    df_copied = df_copied[df_copied["año"].isin([2022, 2023])]
    df_copied = df_copied.fillna(0)
    df_copied["Total"] = df_copied["pasajeros"] + df_copied["suv"] + df_copied["camioneta"] + df_copied["comercial"]
    df_copied["Total"] = df_copied["Total"].round(0)
    pivot_table_copied = df_copied.pivot_table(index='mes', columns='año', values='Total', aggfunc='first', fill_value=0)
    pivot_table_copied[2023] = pivot_table_copied[2023].astype(float)
    pivot_table_copied[2022] = pivot_table_copied[2022].astype(float)
    pivot_table_copied["var"] = ((pivot_table_copied[2023] / pivot_table_copied[2022]) - 1) * 100
    pivot_table_copied["var"] = pivot_table_copied["var"].apply(lambda x: f"{x:.1f} %")
    replacement_value = " "
    pivot_table_copied["var"] = pivot_table_copied["var"].replace("-100.0 %", replacement_value)
    pivot_table_copied[2023] = pivot_table_copied[2023].apply(lambda x: "{:,.0f}".format(x))
    pivot_table_copied[2022] = pivot_table_copied[2022].apply(lambda x: "{:,.0f}".format(x))
    #st.table(pivot_table_copied)    
    # grafico evolución ANAC 2
    fig_var = go.Figure()
    # Agregar la línea de variación var en y2
    fig_var.add_trace(
        go.Scatter(
            x=pivot_table_copied.index,
            y=pivot_table_copied["var"],
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=2)),
            line=dict(color="#FF5858"),  # Cambiar el color a rojo
            text=[f'<span style="color: #0C356A;"><b>{var}</b></span>' for var in pivot_table_copied["var"]],            
            textposition="top center",
            name="Variación %",
            yaxis="y2",))
    # Agregar la barra para el año 2022
    fig_var.add_trace(
        go.Bar(
            x=pivot_table_copied.index,
            y=pivot_table_copied[2022],
            text=[f'<b>{value}</b>' for value in pivot_table_copied[2022]],
            textposition="inside",  # Mostrar etiquetas dentro de las barras
            textfont=dict(color="white", size=10),
            textangle=-90,  # Color y tamaño de las etiquetas
            name="2022",
            marker_color="#2F58CD"))

    # Agregar la barra para el año 2023
    fig_var.add_trace(
        go.Bar(
            x=pivot_table_copied.index,
            y=pivot_table_copied[2023],
            text=[f'<b>{value}</b>' for value in pivot_table_copied[2023]],
            textposition="inside",  # Mostrar etiquetas dentro de las barras
            textfont=dict(color="white", size=10),  # Color y tamaño de las etiquetas
            textangle=-90, 
            name="2023",
            marker_color="#3795BD"))
    fig_var.update_layout(
        title="1. Venta de Vehículos Categoria Livianos Comparativo Año 2022-2023",
        xaxis=dict(title="Mes"),
        yaxis=dict(title="Valor"),
        yaxis2=dict(
            title="Variación %",
            overlaying="y",
            side="right",
            showgrid=False,  # Desactivar las líneas de la cuadrícula en y2
        ),
        legend=dict(x=0, y=-0.6),
        barmode="group",)
    st.plotly_chart(fig_var)

    # Grafico STACK ANAC
    fig_anac = px.bar(
        df_filtered,
        x="mes",
        y=["pasajeros", "suv", "camioneta", "comercial"],
        title="2. Segmentación Venta de Vehículos Categoria Livianos 2023",
        labels={"value": "Cantidad", "variable": "Tipo de Vehículo"},
        color_discrete_map={
            "pasajeros": "#11009E",
            "suv": "#4942E4",
            "camioneta": "#8696FE",
            "comercial": "#C4B0FF"
        })

    fig_anac.update_layout(barmode="stack")

    # Agregar etiquetas de datos centradas en cada barra
    for trace in fig_anac.data:
        trace.text = df_filtered[trace.name].apply(lambda x: f"<b>{x:,}</b>")
        trace.textposition = 'inside'
        trace.textfont.color = 'white'  # Color del texto en blanco
        trace.textfont.size = 12  # Tamaño del texto

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_anac)
with container: #3.1- INDICADORES INGRESOS
    st.header("3.1- INDICADORES INGRESOS :rocket: :heavy_dollar_sign:")
    st.markdown("---")
    #Datos Ingresos Netos Comparativos
    df_original = eerr()
    df_ingresos_eerr = df_original[(df_original["Grupo"] == '10 - INGRESOS')]
    columns_ingresos = ["Meses", "Año" , "Sucursal", "Monto"]
    df_ingresos_comparativo = df_ingresos_eerr[columns_ingresos]
    pivot_table = df_ingresos_comparativo.pivot_table(index="Meses", columns="Año", values="Monto", aggfunc="sum")
    pivot_table["var"] = (pivot_table[2023] / pivot_table[2022] - 1)*100
    pivot_table["var"] = pivot_table["var"].apply(lambda x: f"{x:.1f} %") 
    replacement_value = " "
    pivot_table["var"] = pivot_table["var"].replace("nan %", replacement_value)
    pivot_table[2022] = pivot_table[2022].apply(lambda x: "$" + format(round(x), ",") if not pd.isna(x) else "NaN")
    pivot_table[2023] = pivot_table[2023].apply(lambda x: "$" + format(round(x), ",") if not pd.isna(x) else "NaN")  
    #st.write(pivot_table)

    #datos de dataframe Ingresos Netos por Segmentación
    df_sucursales = qry_branch_offices()
    df_eerr_segment = df_original.merge(df_sucursales, left_on="Sucursal", right_on="branch_office", how="inner")
    columns_eerr = ["Grupo" , "Meses", "Año" , "Sucursal", "Monto", "principal", "zone", "segment"]
    df_eerr_segment = df_eerr_segment[columns_eerr]
    df_ingresos_segment = df_eerr_segment[
    (df_eerr_segment["Grupo"] == '10 - INGRESOS') &
    (df_eerr_segment["Meses"] == periodo_img) & #cambiar el periodo segun el mes que necesitamos presentar
    (df_eerr_segment["Año"] == 2023)]    
    df_ingresos_segment_grouped = df_ingresos_segment.groupby("segment").sum()
    total_row = df_ingresos_segment_grouped.sum()
    df_ingresos_segment_grouped.loc["Total"] = total_row
    df_ingresos_segment_grouped["part"] = (df_ingresos_segment_grouped["Monto"] / total_row["Monto"]) * 100
    df_ingresos_segment_grouped["part"] = df_ingresos_segment_grouped["part"].apply(lambda x: f"{x:.1f} %")
    df_ingresos_segment_grouped["Monto"] = df_ingresos_segment_grouped["Monto"].apply(
    lambda x: round(x) if not pd.isna(x) else None)
    df_ingresos_segment_filtered = df_ingresos_segment_grouped[df_ingresos_segment_grouped.index != "Total"]
    df_ingresos_segment_filtered = df_ingresos_segment_filtered.sort_values(by="Monto", ascending=False)
    df_ingresos_segment_filtered["Monto"] = df_ingresos_segment_filtered["Monto"].apply(
        lambda x: "$" + format(x, ",") if not pd.isna(x) else "NaN")
    
    #datos de dataframe Composición de Ingresos Netos 
    df_ingresos_composicion = df_original[
        (df_original["Grupo"] == '10 - INGRESOS') &
        (df_original["Año"] == 2023)]
    columns_composicion = ["Meses", "Cuentas", "Monto"]
    df_ingresos_composicion = df_ingresos_composicion[columns_composicion]
    df_pivot = df_ingresos_composicion.pivot_table(
        index="Cuentas",
        columns="Meses",
        values="Monto",
        aggfunc="sum")
    df_pivot.loc["Total"] = df_pivot.sum()
    df_pivot_percentage = df_pivot.divide(df_pivot.loc["Total"]) * 100
    df_pivot_percentage = df_pivot_percentage.applymap(lambda x: f"{x:.1f} %")
    df_pivot_transposed = df_pivot.transpose().reset_index()
    df_pivot_transposed.rename(columns={"index": "Meses"}, inplace=True)
    #st.write(df_pivot_transposed)
    
    
    df_for_plot = df_pivot_transposed[
        (df_pivot_transposed["Meses"] != "Total") &
        (df_pivot_transposed["Meses"] != "Total_2")]
    
    # Crear gráfico de Plotly
    fig_var = go.Figure() #1.- Ingresos Netos Comparativos años 2022 - 2023
    fig_var.add_trace(
        go.Scatter(
            x=pivot_table.index,
            y=pivot_table["var"],
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            line=dict(color="red"),
            text=[f'<span style="color: #3C2317;"><b>{var}</b></span>' for var in pivot_table["var"]],
            textposition="top center",
            name="Variación %",
            yaxis="y2",))
    fig_var.add_trace(
        go.Bar(
            x=pivot_table.index,
            y=pivot_table[2022],
            text=pivot_table[2022],  # Agregar etiquetas de datos al interior de las barras
            textposition="inside",  # Posición dentro de las barras
            insidetextanchor='start',  # Anclaje al inicio de la barra
            textangle=270,  # Orientación vertical
            textfont_color="white",  # Color blanco para las etiquetas
            name="2022",
            marker_color="#C47AFF",))
    fig_var.add_trace(
        go.Bar(
            x=pivot_table.index,
            y=pivot_table[2023],
            text=pivot_table[2023],  # Agregar etiquetas de datos al interior de las barras
            textposition="inside",  # Posición dentro de las barras
            insidetextanchor='start',  # Anclaje al inicio de la barra
            textangle=270,  # Orientación vertical
            textfont_color="white",  # Color blanco para las etiquetas
            name="2023",
            marker_color="#4649FF",))

    fig_var.update_layout(
        title="1.- Ingresos Netos Comparativos años 2022 - 2023",
        xaxis=dict(title="Meses"),
        yaxis=dict(title="Ingresos Netos"),
        yaxis2=dict(
            title="Variación %",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(x=0, y=-0.6),
        barmode="group",)
    st.plotly_chart(fig_var)

    fig = go.Figure() #2.- Ingresos Netos por Segmentación
    fig.add_trace(
        go.Bar(
            x=df_ingresos_segment_filtered.index,
            y=df_ingresos_segment_filtered["Monto"],
            text=df_ingresos_segment_filtered["Monto"],
            textposition="inside",
            insidetextanchor="start",
            textangle=0,
            textfont_color="white",
            name="Monto",
            marker_color="#1363DF",))
    fig.add_trace(
        go.Scatter(
            x=df_ingresos_segment_filtered.index,
            y=df_ingresos_segment_filtered["part"],
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            line=dict(color="#F54748"),
            text=[f'<span style="color: #3C2317;"><b>{part}</b></span>' for part in df_ingresos_segment_filtered["part"]],
            textposition="top center",
            name="Participación %",
            yaxis="y2",))
    fig.update_layout(
        title="2.- Ingresos Netos por Segmentación",
        xaxis=dict(title="Segmento"),
        yaxis=dict(title="Monto"),
        yaxis2=dict(
            title="Participación %",
            overlaying="y",
            side="right",
            showgrid=False,),
        legend=dict(x=0, y=-0.6),
        barmode="group",)
    st.plotly_chart(fig)

    # Grafico Indicadores de Ingresos 3
    st.markdown("---")
    st.write(df_pivot)
    #st.write(df_pivot_transposed)
    fig = px.bar(
        df_for_plot,
        x="Meses",
        y=["Ingreso por Administración", "Ingresos Boleta Electrónica", "Ingresos por Abonados"],
        title="INDICADORES DE INGRESOS - Composición de Ingresos Netos",
        labels={"value": "Monto", "variable": "Cuentas"},
        color_discrete_map={
            "Ingreso por Administración": "#BFDCAE",
            "Ingresos Boleta Electrónica": "#206A5D",
            "Ingresos por Abonados": "#68B0AB"})
    fig.update_layout(
        barmode="stack",        
        legend=dict(x=0, y=-0.6))  # Posicionar la leyenda debajo del eje x
    # Configurar las etiquetas de datos
    for trace in fig.data:
        trace.text = df_for_plot[trace.name].apply(lambda x: f"<b>${x:,}</b>")  # Formatear como moneda
        trace.textposition = 'inside'
        trace.textfont.color = 'white'  # Establecer el color del texto en blanco
        #trace.insidetextanchor = 'start'  # Anclar el texto al inicio de la barra
        trace.textangle = 0  # Orientación horizontal del texto
        trace.textposition = 'inside'  # Posicionar el texto dentro de la barra
        trace.textfont.size = 12  # Ajustar el tamaño del texto en función del valor máximo de las barras

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


    df_pivot_filtered = df_pivot_percentage[df_pivot_percentage.index != "Total"]
    st.markdown("---")
    st.write(df_pivot_percentage)   
    fig_evolucion = go.Figure()
    for cuenta in df_pivot_filtered.index:
        fig_evolucion.add_trace(go.Scatter(
            x=df_pivot_filtered.columns,
            y=df_pivot_filtered.loc[cuenta],
            mode='lines+markers+text',  # Agregar marcadores y texto
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=2)),  # Definir marcadores
            text=[f'<span style="color: #3C2317;"><b>{value}</b></span>' for value in df_pivot_filtered.loc[cuenta]],  # Texto para etiquetas
            textposition="top center",  # Posición del texto
            name=cuenta))
    fig_evolucion.update_layout(
        title="Evolución de Cuentas por Mes",
        xaxis_title="Meses",
        yaxis_title="Porcentaje (%)",
        legend=dict(x=0.5, y=-0.6))
    st.plotly_chart(fig_evolucion)
with container: #4.4- INDICADORES REMUNERACIONES
    st.header("4.1.- INDICADORES DE DOTACIÓN")
    st.markdown("---")
    df_original = eerr()
    df_remuneracion_eerr = df_original[(df_original["Grupo"] == '60 - REMUNERACION') &
    (df_original["Año"] == 2023)]
    columns_remuneracion = ["Meses",  "Cuentas" , "Monto"]
    df_remuneracion_comparativo = df_remuneracion_eerr[columns_remuneracion]
   
    pivot_table_remuneracion = df_remuneracion_comparativo.pivot_table(
        index='Cuentas',  
        columns='Meses',  
        values='Monto',  
        aggfunc='sum')   
    pivot_table_remuneracion = pivot_table_remuneracion.fillna(0)
    total_column_sum = pivot_table_remuneracion.sum()
    total_row = pd.DataFrame(total_column_sum).T
    total_row.index = ['Total']
    pivot_table_remuneracion = pivot_table_remuneracion.append(total_row)
    filas_filtradas = pivot_table_remuneracion.loc[["Total", "Honorarios"]]
    
    nuevo_dataframe = pd.DataFrame(filas_filtradas)  
    nuevo_dataframe = nuevo_dataframe.applymap(lambda x: -x)
    nuevo_dataframe.loc["part"] = (nuevo_dataframe.loc["Honorarios"] / nuevo_dataframe.loc["Total"]) * 100
    nuevo_dataframe.loc["part"] = nuevo_dataframe.loc["part"].apply(lambda x: f"{x:.1f} %")
    nuevo_dataframe.loc["Total"] = nuevo_dataframe.loc["Total"].apply(lambda x: f"${int(x):,}")
    nuevo_dataframe.loc["Honorarios"] = nuevo_dataframe.loc["Honorarios"].apply(lambda x: f"${int(x):,}")
    

    fig_var = go.Figure()

    # Agregar la línea "part"
    fig_var.add_trace(
        go.Scatter(
            x=nuevo_dataframe.columns,
            y=nuevo_dataframe.loc["part"],
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            line=dict(color="red"),
            text=[f'<span style="color: #6C3428;"><b>{part}</b></span>' for part in nuevo_dataframe.loc["part"]],
            textposition="top center",
            name="Participación %",
            yaxis="y2",))

    # Agregar la barra "Total"
    fig_var.add_trace(
        go.Bar(
            x=nuevo_dataframe.columns,
            y=nuevo_dataframe.loc["Total"],
            text=nuevo_dataframe.loc["Total"], 
            textposition="inside", 
            insidetextanchor='start', 
            textangle=270, 
            textfont_color="white", 
            name="Total", 
            marker_color="#4D77FF",))

    # Agregar la barra "Honorarios"
    fig_var.add_trace(
        go.Bar(
            x=nuevo_dataframe.columns,
            y=nuevo_dataframe.loc["Honorarios"],
            text=nuevo_dataframe.loc["Honorarios"], 
            textposition="inside", 
            insidetextanchor='start', 
            textangle=270, 
            textfont_color="white", 
            name="Honorarios", 
            marker_color="#1D5D9B",))

    # Actualizar el diseño del gráfico
    fig_var.update_layout(
        title="Gráfico de Remuneraciones",
        xaxis=dict(title="Meses"),
        yaxis=dict(title="Valor"),
        yaxis2=dict(
            title="Participación %",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(x=0, y=-0.6),
        barmode="stack",
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_var)

    st.header("4.2- INDICADORES DE DOTACIÓN")
    st.markdown("---")
    df_dotacion = RRHH_dotacion()

    # Crear el pivot table
    pivot_table_dotacion = df_dotacion.pivot_table(
        index='item',  
        columns='periodo',  
        values='cantidad',  
        aggfunc='sum')   
    
    pivot_table_dotacion = pivot_table_dotacion.fillna(0)
    
    full_partime_rows = pivot_table_dotacion[pivot_table_dotacion.index.isin(['Full', 'Partime'])]
    egresos_rows = pivot_table_dotacion[pivot_table_dotacion.index.isin(['Voluntario', 'Desvinculado'])]
    honorarios_rows = pivot_table_dotacion[pivot_table_dotacion.index.isin(['Honorarios '])]
    ingresos_rows = pivot_table_dotacion[pivot_table_dotacion.index.isin(['Ingreso'])]

    dotacion_sum = full_partime_rows.sum()
    egresos_sum = egresos_rows.sum()
    honorarios_sum = honorarios_rows.sum()
    ingresos_sum = ingresos_rows.sum()

    pivot_table_dotacion.loc['dotacion'] = dotacion_sum
    pivot_table_dotacion.loc['egresos'] = egresos_sum
    #pivot_table_dotacion.loc['honrarios'] = honorarios_sum

    # Calcular la suma de "dotacion" y "Honorarios"
    dotacion_total_sum = dotacion_sum + honorarios_sum
    dotacion_real = dotacion_total_sum + ingresos_sum - egresos_sum
    egresos_porc = round(((egresos_sum / dotacion_total_sum)* 100),1)

    # Agregar la suma como nueva fila a la tabla pivote
    pivot_table_dotacion.loc['dotacion_total'] = dotacion_total_sum
    pivot_table_dotacion.loc['dotacion_real'] = dotacion_real
    pivot_table_dotacion.loc['egresos_porc'] = egresos_porc
    
    # Reordenar las filas según un orden personalizado
    order = ['Full', 'Partime', 'dotacion', 'Honorarios ', 'dotacion_total', 'Ingreso', 'egresos', 'dotacion_real', 'egresos_porc']
    
    # Crear un diccionario para renombrar las filas
    column_show = {
    'dotacion': 'Dotación Nominal',    
    'Honorarios ': 'Honorarios',
    'dotacion_total': 'Dotación Total',
    'Ingreso': 'Ingresos',
    'egresos': 'Egresos',
    'dotacion_real': 'Dotación Real',
    'egresos_porc': 'Egresos %'}    

    pivot_table_dotacion = pivot_table_dotacion.loc[order].rename(index=column_show)

    # Crear la figura
    fig_var = go.Figure()

    # Agregar la línea "% egresos"
    fig_var.add_trace(
        go.Scatter(
            x=pivot_table_dotacion.columns,
            y=pivot_table_dotacion.loc["Egresos %"],
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            line=dict(color="red"),
            text=[f'<span style="color: #6C3428;"><b>{round(val,0)}%</b></span>' for val in pivot_table_dotacion.loc["Egresos %"]],
            textposition="top center",
            name="% Egresos",
            yaxis="y2",
        )
    )

    bar_columns = ["Dotación Total", "Egresos", "Ingresos"]
    colors = ["#4D77FF", "#1D5D9B", "#59C3C3"]

    for i, column in enumerate(bar_columns):
        fig_var.add_trace(
            go.Bar(
                x=pivot_table_dotacion.columns,
                y=pivot_table_dotacion.loc[column],
                text=pivot_table_dotacion.loc[column],
                textposition="inside",
                insidetextanchor='start',
                textangle=0,
                textfont_color="white",
                name=column,
                marker_color=colors[i],
            )
        )

    # Actualizar el diseño del gráfico
    fig_var.update_layout(
        title="Dotación Vs Rotación",
        xaxis=dict(title="Meses"),
        yaxis=dict(title="Valor"),
        yaxis2=dict(
            title="% Egresos",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(x=0, y=-0.6),
        barmode="stack",
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_var)


    # Crear la figura
    fig_var = go.Figure()

    # Agregar las barras apiladas para "Full", "Partime" y "Honorarios"
    bar_columns = ["Full", "Partime", "Honorarios"]
    colors = ["#4D77FF", "#FFAB76", "#B8B5FF"]

    for i, column in enumerate(bar_columns):
        fig_var.add_trace(
            go.Bar(
                x=pivot_table_dotacion.columns,
                y=pivot_table_dotacion.loc[column],
                text=pivot_table_dotacion.loc[column],
                textposition="inside",
                insidetextanchor='start',
                textangle=0,
                textfont_color="white",
                name=column,
                marker_color=colors[i],
            )
        )

    # Agregar la línea para "Dotación Total"
    fig_var.add_trace(
        go.Scatter(
            x=pivot_table_dotacion.columns,
            y=pivot_table_dotacion.loc["Dotación Total"],
            mode="lines+markers+text",
            marker=dict(symbol="circle", size=8, line=dict(color="white", width=1)),
            line=dict(color="#810034"),
            text=[f'<span style="color: #6C3428;"><b>{val:.0f}</b></span>' for val in pivot_table_dotacion.loc["Dotación Total"]],
            textposition="top center",
            name="Dotación Total",
        )
    )

    # Actualizar el diseño del gráfico
    fig_var.update_layout(
        title="Distribución Dotación Real",
        xaxis=dict(title="Meses"),
        yaxis=dict(title="Valor"),
        legend=dict(x=0, y=-0.6),
        barmode="stack",
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_var)

    fig_var = go.Figure()

    # Agregar las barras apiladas horizontales
    bar_columns = ["Egresos", "Ingresos"]
    colors = ["#1D5D9B", "#59C3C3"]

    for i, column in enumerate(bar_columns):
        if column == "Egresos":
            data = -1 * pivot_table_dotacion.loc[column]  # Convertir Egresos en negativo
        else:
            data = pivot_table_dotacion.loc[column]
        
        fig_var.add_trace(
            go.Bar(
                y=pivot_table_dotacion.columns,
                x=data,
                orientation='h',  # Barra horizontal
                text=data,
                textposition="inside",
                insidetextanchor='start',
                textangle=0,
                textfont_color="white",
                name=column,
                marker_color=colors[i],
            )
        )

    # Actualizar el diseño del gráfico
    fig_var.update_layout(
        title="Egresos vs Ingresos",
        xaxis=dict(title="Valor"),
        yaxis=dict(title="Meses"),
        legend=dict(x=0, y=-0.6),
        barmode="relative",  # Barras apiladas
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig_var)

    
        

    
 

with container: #5.1- INDICADORES DE GASTOS
    st.header("5.1- INDICADORES DE GASTOS")
    st.markdown("---")
    df_original = eerr()    
    df_gastos_original = df_original[(df_original["Año"] == 2023)]
    resultado = df_gastos_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
    resultado.loc['Resultado Operacional'] = resultado.sum()
    ingresos = resultado.loc['10 - INGRESOS']
    for mes in ingresos.index:
        resultado[mes + ' %'] = round((resultado[mes] / ingresos[mes]) * 100, 2).apply(lambda x: f'{x:.2f}%')
    column_order = []
    for mes in ingresos.index:
        column_order.append(mes)
        column_order.append(mes + ' %')
    resultado = resultado[column_order]
    resultado = resultado.sort_index()
    st.dataframe(resultado, width=0)
    with st.expander(" 1.- Gastos de Remuneración Sobre Venta"):
        df_remuneraciones = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['60 - REMUNERACION', '10 - INGRESOS']))]
        df2 = df_remuneraciones.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('60 - REMUNERACION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
            
        # Reiniciar el índice del DataFrame
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
        
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        # Agregar las barras de ingresos y remuneraciones
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                        name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['60 - REMUNERACION'],
                                        name="Remuneraciones", offsetgroup=0, marker_color='#F3A953'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                            mode="lines+markers+text", name="% Part",
                                            line=dict(width=3, color="red"),
                                            marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
                                            yaxis="y2",                                            
                                            text=[f'<span style="color: blue;"><b>{value:.2f}%</b></span>' for value in df2['part%']],
                                            textposition="top center"))
        # Configurar el diseño del gráfico
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)
    
        df_remuneraciones = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['60 - REMUNERACION', '10 - INGRESOS']))]
        df2 = df_remuneraciones.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('60 - REMUNERACION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        df2['10 - INGRESOS'] = df2['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df2['60 - REMUNERACION'] = df2['60 - REMUNERACION'].apply(lambda x: f"${int(x):,}")


        df2_transposed = df2.transpose()
        st.dataframe(df2_transposed, width=0)

    with st.expander(" 2.- Gastos de Arriendos Sobre Venta Neta"):       
        df_arriendo = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['70 - ARRIENDOS', '10 - INGRESOS']))]
        df2 = df_arriendo.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('70 - ARRIENDOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
        
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        # Agregar las barras de ingresos y arriendos
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['70 - ARRIENDOS'],
                                    name="Arriendos", offsetgroup=0, marker_color='#F3A953'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
            mode="lines+markers+text", name="% Part",
            line=dict(width=3, color="red"),
            marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
            yaxis="y2",
            text=[f'<span style="color: blue;"><b>{value:.2f}%</b></span>' for value in df2['part%']],
            textposition="top center"))
        # Configurar el diseño del gráfico
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)

        df_arriendo = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['70 - ARRIENDOS', '10 - INGRESOS']))]
        df2 = df_arriendo.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('70 - ARRIENDOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        
        # Aplicar formato de moneda a los montos
        df2['10 - INGRESOS'] = df2['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df2['70 - ARRIENDOS'] = df2['70 - ARRIENDOS'].apply(lambda x: f"${int(x):,}")
        
        # Transponer el DataFrame
        df2_transposed = df2.transpose()      
        
        st.dataframe(df2_transposed, width=0)

    with st.expander(" 3.- Gastos de Materiales Sobre Venta Neta"):          
        df_materiales = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['20 - MATERIALES', '10 - INGRESOS']))]
        df2 = df_materiales.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('20 - MATERIALES')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
        
        # Crear el gráfico con subplots
        fig_combined = go.Figure()
        # Agregar las barras de ingresos y materiales
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                                    name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['20 - MATERIALES'],
                    name="Materiales", offsetgroup=0,  marker_color='#F3A953'))
        # Agregar la línea al gráfico secundario
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                                        mode="lines+markers+text", name="% Part",
                                        line=dict(width=3, color="red"),
                                        marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
                                        yaxis="y2",
                                        text=[f'<span style="color: blue;"><b>{value:.2f}%</b></span>' for value in df2['part%']],
                                        textposition="top center"))
        # Configurar el diseño del gráfico
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)

        df_materiales = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['20 - MATERIALES', '10 - INGRESOS']))]
        df2 = df_materiales.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('20 - MATERIALES')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')

        # Aplicar formato de moneda a los montos
        df2['10 - INGRESOS'] = df2['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df2['20 - MATERIALES'] = df2['20 - MATERIALES'].apply(lambda x: f"${int(x):,}")

        # Transponer el DataFrame
        df2_transposed = df2.transpose()      

        st.dataframe(df2_transposed, width=0)

    with st.expander(" 4.- Gastos de Mantención Sobre Venta Neta"):  
        df_mantencion = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['30 - MANTENCION', '10 - INGRESOS']))]
        df2 = df_mantencion.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('30 - MANTENCION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')      
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['30 - MANTENCION'],
                name="Mantención", offsetgroup=0, marker_color='#F3A953'))
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                mode="lines+markers+text", name="% Part",
                line=dict(width=3, color="red"),
                marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
                yaxis="y2",
                text=[f'<span style="color: blue;"><b>{value:.2f}%</b></span>' for value in df2['part%']],
                textposition="top center"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)

        df_mantencion = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['30 - MANTENCION', '10 - INGRESOS']))]
        df2 = df_mantencion.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('30 - MANTENCION')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')

        # Aplicar formato de moneda a los montos
        df2['10 - INGRESOS'] = df2['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df2['30 - MANTENCION'] = df2['30 - MANTENCION'].apply(lambda x: f"${int(x):,}")

        # Transponer el DataFrame
        df2_transposed = df2.transpose()      

        st.dataframe(df2_transposed, width=0)

    with st.expander(" 5.- Gastos de Servicios Sobre Venta Neta"):  
        df_servicios = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['40 - SERVICIOS', '10 - INGRESOS']))]
        df2 = df_servicios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('40 - SERVICIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['40 - SERVICIOS'],
                name="Servicios", offsetgroup=0, marker_color='#F3A953'))
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                mode="lines+markers+text", name="% Part",
                line=dict(width=3, color="red"),
                marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
                yaxis="y2",
                text=[f'<span style="color: blue;"><b>{value:.2f}%</b></span>' for value in df2['part%']],
                textposition="top center"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)

        df_servicios = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['40 - SERVICIOS', '10 - INGRESOS']))]
        df2 = df_servicios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('40 - SERVICIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')

        # Aplicar formato de moneda a los montos
        df2['10 - INGRESOS'] = df2['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df2['40 - SERVICIOS'] = df2['40 - SERVICIOS'].apply(lambda x: f"${int(x):,}")

        # Transponer el DataFrame
        df2_transposed = df2.transpose() 
        st.dataframe(df2_transposed, width=0)
    
    with st.expander(" 6.- Gastos de Varios Sobre Venta Neta"):  
        df_varios = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['50 - VARIOS', '10 - INGRESOS']))]
        df2 = df_varios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2['part%'] = round((df2[('50 - VARIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')
        df2.reset_index(inplace=True)   
        df2['part%'] = df2['part%'].str.rstrip('%').astype(float)
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['10 - INGRESOS'],
                name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df2['Meses'], y=df2['50 - VARIOS'],
                name="Varios", offsetgroup=0, marker_color='#F3A953'))
        fig_combined.add_trace(go.Scatter(x=df2['Meses'], y=df2['part%'],
                mode="lines+markers+text", name="% Part",
                line=dict(width=3, color="red"),
                marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
                yaxis="y2",
                text=[f'<span style="color: blue;"><b>{value:.2f}%</b></span>' for value in df2['part%']],
                textposition="top center"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_combined)

        df_varios = df_gastos_original[df_gastos_original['Grupo'].apply(lambda val: any(val == s for s in ['50 - VARIOS', '10 - INGRESOS']))]
        df2 = df_varios.pivot_table(index='Meses', columns='Grupo', values='Monto', aggfunc='sum')
        df2.loc['Total'] = df2.sum()    
        df2['part%'] = round((df2[('50 - VARIOS')] / df2[('10 - INGRESOS')])*100, 2).apply(lambda x: f'{x:.2f}%')

        # Aplicar formato de moneda a los montos
        df2['10 - INGRESOS'] = df2['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df2['50 - VARIOS'] = df2['50 - VARIOS'].apply(lambda x: f"${int(x):,}")

        # Transponer el DataFrame
        df2_transposed = df2.transpose()      

        st.dataframe(df2_transposed, width=0)

    with st.expander(" 7.- Gastos de Resultado Operacional Sobre Venta Neta"):  
        df_total = df_gastos_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
        df_total.loc['R.O.P'] = df_total.sum() 
        filas_seleccionadas = ['10 - INGRESOS', 'R.O.P']
        df_seleccion = df_total.loc[filas_seleccionadas]
        df_seleccion.loc['Part%'] = round((df_seleccion.loc['R.O.P'] / df_seleccion.loc['10 - INGRESOS']) * 100, 2).apply(lambda x: f'{x:.2f}%')   
        df_nuevo = df_seleccion.T.copy()       
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(x=df_nuevo.index, y=df_nuevo['10 - INGRESOS'],
                name="Ingresos", offsetgroup=0, marker_color='#3399FF'))
        fig_combined.add_trace(go.Bar(x=df_nuevo.index, y=df_nuevo['R.O.P'],
                name="Total", offsetgroup=0, marker_color='#F3A953'))
        fig_combined.add_trace(go.Scatter(x=df_nuevo.index, y=df_nuevo['Part%'],
                mode="lines+markers+text", name="% Part",
                line=dict(width=3, color="red"),
                marker=dict(size=8, symbol="circle", line=dict(color="white", width=2)),
                yaxis="y2",
                text=[f'<span style="color: blue;"><b>{value}</b></span>' for value in df_nuevo['Part%']],
                textposition="top center"))
        fig_combined.update_layout(yaxis=dict(title="Valores", showgrid=True, zeroline=True))
        fig_combined.update_layout(yaxis2=dict(title="% Part", showgrid=False, zeroline=False, overlaying="y", side="right"))
        fig_combined.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))        
        st.plotly_chart(fig_combined)
        
        #Tabla de datos ROP
        df_total = df_gastos_original.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
        df_total.loc['R.O.P'] = df_total.sum() 
        filas_seleccionadas = ['10 - INGRESOS', 'R.O.P']
        df_seleccion = df_total.loc[filas_seleccionadas]
        df_seleccion = df_seleccion.assign(Total=df_seleccion.sum(axis=1)) 
        df_seleccion.loc['Part%'] = round((df_seleccion.loc['R.O.P'] / df_seleccion.loc['10 - INGRESOS']) * 100, 2).apply(lambda x: f'{x:.2f}%')  
        df_nuevo = df_seleccion.T.copy()

        # Aplicar formato de moneda a los montos
        df_nuevo['10 - INGRESOS'] = df_nuevo['10 - INGRESOS'].apply(lambda x: f"${int(x):,}")
        df_nuevo['R.O.P'] = df_nuevo['R.O.P'].apply(lambda x: f"${int(x):,}")
        

        st.dataframe(df_nuevo,  width=0)









    








