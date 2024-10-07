from flask import Flask, render_template, request, jsonify
import pyodbc
from langchain_community.llms import Ollama
import mysql.connector
import logging

app = Flask(__name__)

# Configuración del modelo Llama 3.2
llm = Ollama(model="llama3.2", temperature=0.1)

# Configurar el logging
logging.basicConfig(level=logging.INFO)


def obtener_parametros_conexion():
    try:
        # Conectar a MySQL
        conexion_mysql = mysql.connector.connect(
            host='10.47.18.110',
            user='operdat',
            password='operacionesJ4',
            database='gob_datos'
        )

        cursor = conexion_mysql.cursor()

        # Ejecutar la consulta para obtener los parámetros de conexión
        query = """
        SELECT a.driver, c.ip_url, b.user, b.PASSWORD, b.base_datos, a.timeout
        FROM conexion a
        JOIN base_datos b ON a.id_base_datos = b.id_base_datos
        JOIN servidor c ON c.id_servidor = a.id_servidor
        """
        cursor.execute(query)
        resultado = cursor.fetchone()

        # Cerrar la conexión a MySQL
        cursor.close()
        conexion_mysql.close()

        if resultado:
            # Desempaquetar los resultados en variables
            driver, ip_url, usuario, password, base_datos, timeout = resultado
            return driver, ip_url, usuario, password, base_datos, timeout
        else:
            logging.error("No se encontraron resultados.")
            return None

    except mysql.connector.Error as err:
        logging.error(f"Error en la conexión a MySQL: {err}")
        return None


def generar_consulta_sql(pregunta, fecha_inicio, fecha_fin):
    # Palabras clave que pueden indicar que la pregunta está relacionada con la consulta DPI
    palabras_clave_dpi = ["fecha", "nro telefono", "hora", "megabytes", "servicio", "linea", "telefono", "megas", "trafico"]

    # Verificar si contiene palabras clave
    if any(palabra in pregunta.lower() for palabra in palabras_clave_dpi):
        logging.info("PROCESANDO RESPUESTA...")  # Mensaje de procesamiento
        prompt = f"""
        A partir de la pregunta del usuario, genera una consulta SQL válida para Netezza IBM que pueda ejecutarse sobre la consulta_DPI.
        La consulta debe estar relacionada a la siguiente estructura:
        consulta_DPI:
        SELECT
            a.FECHA,
            a.NRO_TELEFONO TELEFONO,
            a.HORA,
            SUM(a.down + a.up)/1000/1000 MB,
            b.SERVICEID SERVICIO
        FROM
            PR_DPI.MODELO.AGG_NRO_DIA_DPI a,
            PR_DPI.MODELO.DIM_APP_DPI b
        WHERE
            a.fecha BETWEEN TO_DATE('{fecha_inicio}', 'yyyy-mm-dd') AND TO_DATE('{fecha_fin}', 'yyyy-mm-dd')
            AND a.idw_tipo_cdr_dpi = 1
            AND a.idw_app_dpi = b.idw_app_dpi
        GROUP BY
            a.FECHA,
            a.NRO_TELEFONO,
            a.HORA,
            b.SERVICEID
        ORDER BY
            SUM(a.down + a.up)/1000/1000
        LIMIT 100;
        Pregunta: {pregunta}

        Respuesta: Solo devuelve la consulta SQL sin ningún comentario ni texto adicional.
        """
        try:
            consulta_sql = llm.invoke(prompt).strip()

            # Asegúrate de que la consulta no tenga caracteres de formato
            consulta_sql = consulta_sql.replace("```sql", "").replace("```", "").strip()

            return consulta_sql
        except Exception as e:
            logging.error(f"Error generando consulta SQL: {e}")
            return None
    else:
        return "Solo respondo consultas relacionadas al DPI."


# Función para ejecutar la consulta SQL y obtener resultados desde Netezza
def ejecutar_consulta(consulta, driver, ip_url, usuario, password, base_datos, timeout):
    try:
        # Conexión a Netezza con pyodbc
        connection_string = f'DRIVER={driver};SERVER={ip_url};UID={usuario};PWD={password};DATABASE={base_datos};LoginTimeout={timeout}'
        conexion = pyodbc.connect(connection_string)
        cursor = conexion.cursor()
        cursor.execute(consulta)
        resultados = cursor.fetchall()  # Obtener todos los resultados
        cursor.close()
        conexion.close()
        print(f"Consulta a ejecutar: {consulta}")
        return resultados

    except pyodbc.Error as err:
        logging.error(f"Error en la consulta Netezza: {err}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/consulta', methods=['POST'])
def consulta():
    data = request.get_json()
    pregunta = data.get('pregunta')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')

    # Generar la consulta SQL
    consulta_sql = generar_consulta_sql(pregunta, fecha_inicio, fecha_fin)

    if consulta_sql is None:
        return jsonify({"error": "Error al generar la consulta SQL"}), 500

    # Obtener los parámetros de conexión
    conexion_params = obtener_parametros_conexion()
    if not conexion_params:
        return jsonify({"error": "No se pudo obtener los parámetros de conexión"}), 500

    driver, ip_url, usuario, password, base_datos, timeout = conexion_params

    # Ejecutar la consulta
    resultados = ejecutar_consulta(consulta_sql, driver, ip_url, usuario, password, base_datos, timeout)

    # Preparar resultados para el frontend
    if resultados is not None:
        resultados_list = [list(fila) for fila in resultados]
    else:
        resultados_list = []

    return jsonify({
        "pregunta": pregunta,
        "consulta_sql": consulta_sql,
        "resultados": resultados_list
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5139, debug=True)
