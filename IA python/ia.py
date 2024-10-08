from flask import Flask, render_template, request, jsonify
import pyodbc
import mysql.connector
import logging
<<<<<<< HEAD
from langchain_community.llms import Ollama

=======
 
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
app = Flask(__name__)
 
# Configuración del modelo Llama 3.2
llm = Ollama(model="llama3.2", temperature=0.1)
 
# Configurar el logging
logging.basicConfig(level=logging.INFO)
<<<<<<< HEAD

# Configurar la conexión MySQL
=======
 
 
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
def obtener_parametros_conexion():
    try:
        # Conectar a MySQL
        conexion_mysql = mysql.connector.connect(
            host='10.47.18.110',
            user='operdat',
            password='operacionesJ4',
            database='gob_datos'
        )
<<<<<<< HEAD
=======
 
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
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
<<<<<<< HEAD
        return resultado
    except mysql.connector.Error as err:
        logging.error(f"Error en la conexión a MySQL: {err}")
        return None
    finally:
        cursor.close()
        conexion_mysql.close()

# Obtener las palabras clave de la tabla 'palabraclave'
def obtener_palabras_clave():
    try:
        conexion_mysql = mysql.connector.connect(
            host='10.47.18.110',
            user='operdat',
            password='operacionesJ4',
            database='gob_datos'
        )
        cursor = conexion_mysql.cursor()
        query = "SELECT palabra_clave FROM palabra_clave"
        cursor.execute(query)
        palabras = [fila[0] for fila in cursor.fetchall()]  
        return palabras
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener palabras clave: {err}")
        return []
    finally:
        cursor.close()
        conexion_mysql.close()

def buscar_palabra_clave(pregunta):
    palabras_clave_dpi = obtener_palabras_clave()
    palabras_encontradas = [palabra for palabra in palabras_clave_dpi if palabra.lower() in pregunta.lower()]
    print(f"Palabra clave encontrada: {palabras_encontradas}")
    return palabras_encontradas if palabras_encontradas else None

def generar_consulta_sql(pregunta, fecha_inicio, fecha_fin, palabras_clave, prompt1):
    prompt1 = obtener_prompts(palabras_clave)
    if any(palabra.lower() in pregunta.lower() for palabra in palabras_clave):
=======
 
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
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
        prompt = f"""
        {prompt1}
        WHERE a.fecha BETWEEN TO_DATE('{fecha_inicio}', 'yyyy-mm-dd') AND TO_DATE('{fecha_fin}', 'yyyy-mm-dd')
        Pregunta: {pregunta}
<<<<<<< HEAD
        Respuesta: Devuelve solo la consulta SQL sin ninguna explicación ni texto adicional.
        """
        try:
            consulta_sql = llm.invoke(prompt).strip()
            consulta_sql = consulta_sql.replace("```sql", "").replace("```", "").strip()
=======
 
        Respuesta: Solo devuelve la consulta SQL sin ningún comentario ni texto adicional.
        """
        try:
            consulta_sql = llm.invoke(prompt).strip()
 
            # Asegúrate de que la consulta no tenga caracteres de formato
            consulta_sql = consulta_sql.replace("```sql", "").replace("```", "").strip()
 
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
            return consulta_sql
        except Exception as e:
            logging.error(f"Error generando consulta SQL: {e}")
            return None
    else:
        return "Solo respondo consultas relacionadas al DPI."
<<<<<<< HEAD

=======
 
 
# Función para ejecutar la consulta SQL y obtener resultados desde Netezza
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
def ejecutar_consulta(consulta, driver, ip_url, usuario, password, base_datos, timeout):
    try:
        connection_string = f'DRIVER={driver};SERVER={ip_url};UID={usuario};PWD={password};DATABASE={base_datos};LoginTimeout={timeout}'
        conexion = pyodbc.connect(connection_string)
        cursor = conexion.cursor()
        cursor.execute(consulta)
        resultados = cursor.fetchall()
        return resultados
<<<<<<< HEAD
    except pyodbc.Error as err:
        logging.error(f"Error en la consulta Netezza: {err}")
        return None
    finally:
        cursor.close()
        conexion.close()

def obtener_prompts(palabras_encontradas):
    try:
        conexion_mysql = mysql.connector.connect(
            host='10.47.18.110',
            user='operdat',
            password='operacionesJ4',
            database='gob_datos'
        )
        cursor = conexion_mysql.cursor()
        palabra_clave_str = "','".join(palabras_encontradas)
        query = f"""
        SELECT d.prompt 
        FROM palabra_clave a 
        JOIN palabra_negocio c ON c.id_palabra = a.id_palabra_clave 
        JOIN negocio b ON c.id_negocio = b.id_negocio 
        JOIN prompt d ON d.id_negocio = b.id_negocio 
        WHERE a.palabra_clave IN ('{palabra_clave_str}')
        """
        cursor.execute(query)
        prompts = [fila[0] for fila in cursor.fetchall()]
        return prompts
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener prompts: {err}")
        return []
    finally:
        cursor.close()
        conexion_mysql.close()

@app.route('/')
def index():
    return render_template('index.html')

=======
 
    except pyodbc.Error as err:
        logging.error(f"Error en la consulta Netezza: {err}")
        return None
 
 
@app.route('/')
def index():
    return render_template('index.html')
 
 
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
@app.route('/consulta', methods=['POST'])
def consulta():
    data = request.get_json()
    pregunta = data.get('pregunta')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
<<<<<<< HEAD

    palabras_encontradas = buscar_palabra_clave(pregunta)

    if not palabras_encontradas:
        return jsonify({"error": "No keywords found in the query"}), 400

    prompts = obtener_prompts(palabras_encontradas)
    if not prompts:
        return jsonify({"error": "No prompts found for the given keywords"}), 400

    consulta_sql = generar_consulta_sql(pregunta, fecha_inicio, fecha_fin, palabras_encontradas, prompts[0])

    if consulta_sql is None:
        return jsonify({"error": "Error al generar la consulta SQL"}), 500

=======
 
    # Generar la consulta SQL
    consulta_sql = generar_consulta_sql(pregunta, fecha_inicio, fecha_fin)
 
    if consulta_sql is None:
        return jsonify({"error": "Error al generar la consulta SQL"}), 500
 
    # Obtener los parámetros de conexión
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
    conexion_params = obtener_parametros_conexion()
    if not conexion_params:
        return jsonify({"error": "No se pudo obtener los parámetros de conexión"}), 500
 
    driver, ip_url, usuario, password, base_datos, timeout = conexion_params
<<<<<<< HEAD

    resultados = ejecutar_consulta(consulta_sql, driver, ip_url, usuario, password, base_datos, timeout)

    resultados_list = [list(fila) for fila in resultados] if resultados else []

=======
 
    # Ejecutar la consulta
    resultados = ejecutar_consulta(consulta_sql, driver, ip_url, usuario, password, base_datos, timeout)
 
    # Preparar resultados para el frontend
    if resultados is not None:
        resultados_list = [list(fila) for fila in resultados]
    else:
        resultados_list = []
 
>>>>>>> 14fd9791e6ba5626f169b45327ed3b6e1a068e3a
    return jsonify({
        "pregunta": pregunta,
        "palabras_encontradas": palabras_encontradas,
        "consulta_sql": consulta_sql,
        "resultados": resultados_list
    })
 
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5139, debug=True)