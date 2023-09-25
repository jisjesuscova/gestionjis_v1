import streamlit as st
import mysql.connector
from mysql.connector import Error

# Establecer la conexión a la base de datos
@st.cache(allow_output_mutation=True)
def establecer_conexion():
    try:
        connection = mysql.connector.connect(
            host='103.72.78.28',
            database='jysparki_jis',
            user='jysparki_jis',
            password='Jis2020!'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error al conectar a la base de datos: {e}")

# Función para borrar ingresos
def borrado_ingresos():
    conn = establecer_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SET @año = YEAR(CURDATE());
                SET @mes = MONTH(CURDATE())-1;
                DELETE FROM KPI_INGRESOS_IMG_MES
                WHERE period COLLATE utf8mb4_unicode_ci >= CONCAT(@año, '-', LPAD(@mes, 2, '0')) COLLATE utf8mb4_unicode_ci;
            """)
            conn.commit()
            st.success("Borrado de datos exitosamente")
        except Error as e:
            st.error(f"Error al ejecutar la consulta DELETE: {e}")
        finally:
            cursor.close()
            conn.close()

# Llamar a la función de borrado de ingresos
borrado_ingresos()

 
conn = st.experimental_connection('mysql', type='sql')


def carga_ingresos():
    conn.query("""
                        INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, Venta_SSS, Ingresos_SSS)
                        SELECT
                        DM_PERIODO.Periodo,
                        DM_PERIODO.period,
                        DM_PERIODO.`Año`,
                        QRY_BRANCH_OFFICES.branch_office, 
                        QRY_IND_SSS.`value`, 
                        SUM(QRY_INGRESOS_TOTALES_PBI.ticket_number)AS ticket_number, 
                        SUM(QRY_INGRESOS_TOTALES_PBI.abonados) AS abonados, 
                        SUM(QRY_INGRESOS_TOTALES_PBI.net_amount) AS net_amount, 
                        SUM(QRY_INGRESOS_TOTALES_PBI.transbank) AS transbank,	
                        SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank)) AS Venta_Neta, 
                        SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados)) AS Ingresos, 
                        SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank) * (QRY_IND_SSS.`value`))) AS Venta_SSS, 
                        SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados) * (QRY_IND_SSS.`value`))) AS Ingresos_SSS
                        FROM QRY_INGRESOS_TOTALES_PBI
                        LEFT JOIN QRY_BRANCH_OFFICES
                        ON QRY_INGRESOS_TOTALES_PBI.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
                        LEFT JOIN QRY_IND_SSS
                        ON QRY_INGRESOS_TOTALES_PBI.clave = QRY_IND_SSS.clave
                        LEFT JOIN DM_PERIODO
                        ON QRY_INGRESOS_TOTALES_PBI.date = DM_PERIODO.Fecha
                        WHERE	QRY_BRANCH_OFFICES.status_id = 15 AND
                        MONTH(`QRY_INGRESOS_TOTALES_PBI`.`date`) >= ((MONTH(curdate())-1)) AND
                        YEAR(`QRY_INGRESOS_TOTALES_PBI`.`date`) = YEAR(curdate())
                        GROUP BY DM_PERIODO.Periodo,DM_PERIODO.period,DM_PERIODO.`Año`,QRY_BRANCH_OFFICES.branch_office
                        ORDER BY QRY_INGRESOS_TOTALES_PBI.date ASC
                        """, ttl=600)    
    st.success("Ingresos cargados exitosamente")
    


# Botón para cargar ingresos
if st.button("Borrado Ingresos"):
    borrado_ingresos()

if st.button("Cargar Ingresos"):
    carga_ingresos()