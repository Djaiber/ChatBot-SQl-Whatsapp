import psycopg2
from psycopg2 import sql
import os

def create_connection():
    try:
        # Establecer la conexión con la base de datos
        connection = psycopg2.connect(
            host='whatsappdbaws.ckd83boidbuw.us-east-1.rds.amazonaws.com',
            port='5432',
            database='users',
            user='postgres',
            password='post01234#'
        )
        return connection
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al conectar a la base de datos: {error}")
        return None

def fetch_data(query):
    conn = create_connection()
    print(conn)
    if conn is None:
        return
    try:
        # Crear un cursor para ejecutar la consulta
        with conn.cursor() as cursor:
            cursor.execute(query)
            
            # Obtener los resultados
            records = cursor.fetchall()
            
            # Mostrar los resultados
            for row in records:
                print(row)
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al ejecutar la consulta: {error}")
    
    finally:
        # Cerrar la conexión
        if conn:
            conn.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    # Define tu consulta SELECT aquí
    print('empezo')
    query = "SELECT * FROM usuarios_whatsapp;"
    
    # Llamar a la función para obtener datos
    fetch_data(query)
