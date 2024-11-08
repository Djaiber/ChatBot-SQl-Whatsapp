import psycopg2
from flask import Flask, request, jsonify
from openai import OpenAI
app = Flask(__name__)


# Parámetros de conexión a la base de datos
client = OpenAI(api_key="api-key")

db_config = {
    "dbname": "libraryDB",
    "user": "postgres",
    "password": "password",
    "host": "host",
    "port": 5432
}

def openai_answer(question):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": 'Eres un experto en PostgrestSQL. Dada una pregunta de entrada, primero crea una consulta PostgrestSQL sintácticamente correcta para ejecutarla, luego observa los resultados de la consulta y devuelve la respuesta a la pregunta de entrada. A menos que el usuario especifique en la pregunta un número específico de ejemplos, limita la consulta a un máximo de 5 resultados utilizando la cláusula LIMIT de PostgrestSQL. Puedes ordenar los resultados para devolver los datos más informativos de la base de datos. Nunca consultes todas las columnas de una tabla; debes consultar solo las columnas necesarias para responder la pregunta. Envuelve cada nombre de columna entre comillas dobles (") para identificarlas como delimitadores. Asegúrate de usar solo los nombres de columna que puedes ver en las tablas a continuación. Ten cuidado de no consultar columnas que no existen. También presta atención a qué columna está en qué tabla. Utiliza la función date("now") para obtener la fecha actual, si la pregunta involucra "hoy". Asegurate de unicamente responder unicamente SQL, remueve saltos de linea, reemplaza \ por vacio'},
            {
                "role": "user",
                "content": "Te dare informacion adicional para consultar 'Esta es una base de datos encargada de la gestion de libros en una biblioteca, donde tendremos diferentes tablas tales como 'autor' que contiene id, nombre, fecha_nacimiento, nacionalidad. tenemos tambien otra tabla llamada 'autor_libro' donde se relacionan los libros con los autores conteniendo id_autor, id_libro. Otra tabla es la encargada de la informacion del libro llamada 'libro' que contiene id, titulo, anio_publicacion, isbn, genero. Otra tabla se llama 'prestamo' para gestionar a que persona se le presto un libro, contiendo asi id, id_persona, id_libro, fecha_prestamo, fecha_devolucion. Finalmente se tiene la tabla 'persona' que contiene id, nombre, correo, fecha_nacimiento'"
            },
            {
                "role": "user",
                "content": f"{question}"
            }
        ]
    )
    respuesta = completion.choices[0].message.content
    return respuesta

def query_sql(query):
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        query = f"{query}"
        cursor.execute(query)
        results = cursor.fetchall()
        print(results)
        return results
        # for row in results:
        #     print(row)
    except Exception as e:
        print("Ocurrió un error:", e)
        return "No info"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Endpoint para consultas
@app.route('/query', methods=['POST'])
def query_database():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query parameter provided"}), 400
    try:
        response = {}
        rst = openai_answer(query)
        response['Query_Sql'] = str(rst)
        response['Answer'] = str(query_sql(rst))
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
