import mysql.connector
from mysql.connector import Error

class ConexionDB:
    def __init__(self, host='localhost', user='root', password='', database='dbtaller_mecanico'):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }

    def obtener_conexion(self):
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print('Error al conectar a la BD:', e)
            return None
