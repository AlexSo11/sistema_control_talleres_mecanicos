from mysql.connector import Error

class DBVehiculo:
    def __init__(self, conexion):
        self.conexion = conexion

    def crear_vehiculo(self, matricula, cliente_id, marca, modelo, año, color, tipo_combustible):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehiculos (matricula, cliente_id, marca, modelo, año, color, tipo_combustible)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (matricula, cliente_id, marca, modelo, año, color, tipo_combustible))
            conn.commit()
            return True, "Vehículo creado exitosamente"
        except Error as e:
            return False, f"Error al crear vehículo: {e}"
        finally:
            cursor.close()
            conn.close()

    def listar_vehiculos(self):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.nombre as cliente_nombre 
                FROM vehiculos v 
                LEFT JOIN clientes c ON v.cliente_id = c.cliente_id
            """)
            return cursor.fetchall()
        except Error as e:
            print("Error al listar vehículos:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_vehiculo_por_matricula(self, matricula):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.nombre as cliente_nombre 
                FROM vehiculos v 
                LEFT JOIN clientes c ON v.cliente_id = c.cliente_id 
                WHERE v.matricula=%s
            """, (matricula,))
            return cursor.fetchone()
        except Error as e:
            print("Error al buscar vehículo:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def buscar_vehiculo_por_cliente(self, cliente_id):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.nombre as cliente_nombre 
                FROM vehiculos v 
                LEFT JOIN clientes c ON v.cliente_id = c.cliente_id 
                WHERE v.cliente_id=%s
            """, (cliente_id,))
            return cursor.fetchall()
        except Error as e:
            print("Error al buscar vehículos por cliente:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_vehiculo_por_marca(self, marca):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, c.nombre as cliente_nombre 
                FROM vehiculos v 
                LEFT JOIN clientes c ON v.cliente_id = c.cliente_id  # CORREGIDO: era c.id
                WHERE v.marca LIKE %s
            """, (f"%{marca}%",))
            return cursor.fetchall()
        except Error as e:
            print("Error al buscar vehículos por marca:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def actualizar_vehiculo(self, matricula_original, nueva_matricula, cliente_id, marca, modelo, año, color, tipo_combustible):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vehiculos 
                SET matricula=%s, cliente_id=%s, marca=%s, modelo=%s, año=%s, color=%s, tipo_combustible=%s
                WHERE matricula=%s
            """, (nueva_matricula, cliente_id, marca, modelo, año, color, tipo_combustible, matricula_original))
            conn.commit()
            return True, "Vehículo actualizado exitosamente"
        except Error as e:
            return False, f"Error al actualizar vehículo: {e}"
        finally:
            cursor.close()
            conn.close()

    def eliminar_vehiculo(self, matricula):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehiculos WHERE matricula=%s", (matricula,))
            conn.commit()
            return True, "Vehículo eliminado exitosamente"
        except Error as e:
            return False, f"Error al eliminar vehículo: {e}"
        finally:
            cursor.close()
            conn.close()