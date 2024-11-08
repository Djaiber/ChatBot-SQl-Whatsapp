from flask import Flask, request, jsonify
import psycopg2
import vanna as vn
from vanna.remote import VannaDefault

app = Flask(__name__)

# Configuración de Vanna AI
vanna_api_key = "15f2f2ed6b4141dc93a8d9c5108e78b0"
# vn.set_api_key(vanna_api_key)
vanna_model_name = 'chinook'
vn = VannaDefault(model=vanna_model_name, api_key=vanna_api_key)

# vn.set_model('biblioteca')
# training
vn.train(documentation="Esta es una base de datos encargada de la gestion de libros en una biblioteca, donde tendremos diferentes tablas tales como 'autor' que contiene id, nombre, fecha de nacimiento, nacionalidad. tenemos tambien otra tabla llamada 'autor_libro' donde se relacionan los libros con los autores conteniendo id_autor, id_libro. Otra tabla es la encargada de la informacion del libro llamada 'libro' que contiene id, titulo, anio_publicacion, isbn, genero. Otra tabla se llama 'prestamo' para gestionar a que persona se le presto un libro, contiendo asi id, id_persona, id_libro, fecha_prestamo, fecha_devolucion. Finalmente se tiene la tabla 'persona' que contiene id, nombre, correo, fecha_nacimiento")
# vn.train(sql="SELECT col1, col2, col3 FROM my_table")
vn.train(
    question="¿Cuáles son los libros escritos por Gabriel García Márquez?", 
    sql="SELECT l.titulo FROM libro l JOIN autor_libro al ON l.id = al.id_libro JOIN autor a ON a.id = al.id_autor WHERE a.nombre = 'Gabriel García Márquez';"
)

vn.train(
    question="¿Cuántos libros están registrados en la biblioteca?",
    sql="SELECT COUNT(*) AS total_libros FROM libro;"
)
vn.train(
    question="¿Quién ha pedido prestado 'Cien años de soledad'?",
    sql="SELECT p.nombre, p.correo, pr.fecha_prestamo, pr.fecha_devolucion FROM persona p JOIN prestamo pr ON p.id = pr.id_persona JOIN libro l ON pr.id_libro = l.id WHERE l.titulo = 'Cien años de soledad';"
)
vn.train(
    question="¿Cuántos libros ha escrito Isabel Allende?",
    sql="SELECT COUNT(*) AS total_libros FROM libro  JOIN autor_libro al ON l.id = al.id_libro JOIN autor a ON a.id = al.id_autor WHERE a.nombre = 'Isabel Allende';"
)
vn.train(
    question="¿Qué libros han sido prestados y aún no han sido devueltos?",
    sql="SELECT l.titulo, p.nombre, pr.fecha_prestamo FROM libro l JOIN prestamo pr ON l.id = pr.id_libro JOIN persona p ON p.id = pr.id_persona WHERE pr.fecha_devolucion IS NULL;"
)
vn.train(
    question="¿Cuál es la nacionalidad de los autores que han escrito libros de género 'Fantasía'?",
    sql="SELECT DISTINCT a.nacionalidad FROM autor a JOIN autor_libro al ON a.id = al.id_autor JOIN libro l ON l.id = al.id_libro WHERE l.genero = 'Fantasía';"
)
vn.train(
    question="¿Qué autores nacieron antes de 1970?",
    sql="SELECT nombre, fecha_nacimiento FROM autor WHERE fecha_nacimiento < '1970-01-01';"
)

# Parámetros de conexión a la base de datos
def conn_params():
    server_host = "databasehaskell.ckd83boidbuw.us-east-1.rds.amazonaws.com"
    server_port = "5432"
    database_name = "libraryDB"
    DB_username = "postgres"
    password = "fugfof-pYsva9-qixgap"
    return server_host, password, DB_username, database_name, server_port

server_host, password, DB_username, database_name, server_port = conn_params()
connected = vn.connect_to_postgres(
    host=server_host, dbname=database_name, user=DB_username, password=password, port=server_port
)
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
plan = vn.get_training_plan_generic(df_information_schema)
plan
vn.train(plan=plan)
# print("Database connected:", connected)
vn.get_training_data()
print('training')
print(vn.get_training_data())

# Endpoint para consultas
@app.route('/query', methods=['POST'])
def query_database():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query parameter provided"}), 400
    try:
        # Genera y ejecuta el SQL usando Vanna
        sql = vn.generate_sql(query)
        print(sql)
        df = vn.run_sql(sql)
        print(df)
        response = {
            "query": query,
            "sql": sql,
            "data": df.to_dict()  # Convierte el DataFrame a diccionario para JSON
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
