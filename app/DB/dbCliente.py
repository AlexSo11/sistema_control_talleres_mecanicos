"""Acceso a datos de clientes."""

from mysql.connector import Error

class DBCliente:
    def __init__(self, conexion):
        self.conexion = conexion

    def crear_cliente(self, usuario_id, nombre, ap_paterno, ap_materno, telefono, rfc):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (usuario_id, nombre, apellido_paterno, apellido_materno, telefono, rfc)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (usuario_id, nombre, ap_paterno, ap_materno, telefono, rfc))
            conn.commit()
            return True, "Cliente creado exitosamente"
        except Error as e:
            return False, f"Error al crear cliente: {e}"
        finally:
            cursor.close()
            conn.close()

    def listar_clientes_con_usuario(self):
        """Listar clientes con información del usuario"""
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.*, u.username as usuario_nombre 
                FROM clientes c 
                LEFT JOIN usuarios u ON c.usuario_id = u.id
            """)
            return cursor.fetchall()
        except Error as e:
            print("Error al listar clientes con usuario:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_cliente_por_id_con_usuario(self, cliente_id):
        """Buscar cliente por ID con información del usuario"""
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.*, u.username as usuario_nombre 
                FROM clientes c 
                LEFT JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.cliente_id = %s
            """, (cliente_id,))
            return cursor.fetchone()
        except Error as e:
            print("Error al buscar cliente con usuario:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def listar_clientes(self):
        """Listar clientes básico (sin información de usuario)"""
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes")
            return cursor.fetchall()
        except Error as e:
            print("Error al listar clientes:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_cliente_por_nombre(self, nombre):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes WHERE nombre LIKE %s", (f"%{nombre}%",))
            return cursor.fetchall()
        except Error as e:
            print("Error al buscar cliente:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def actualizar_cliente(self, cliente_id, usuario_id, nombre, ap_paterno, ap_materno, telefono, rfc):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes 
                SET usuario_id=%s, nombre=%s, apellido_paterno=%s, apellido_materno=%s,
                    telefono=%s, rfc=%s
                WHERE cliente_id=%s
            """, (usuario_id, nombre, ap_paterno, ap_materno, telefono, rfc, cliente_id))
            conn.commit()
            return True, "Cliente actualizado exitosamente"
        except Error as e:
            return False, f"Error al actualizar cliente: {e}"
        finally:
            cursor.close()
            conn.close()

    def eliminar_cliente(self, cliente_id):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE cliente_id=%s", (cliente_id,))
            conn.commit()
            return True, "Cliente eliminado"
        except Error as e:
            return False, f"Error al eliminar cliente: {e}"
        finally:
            cursor.close()
            conn.close()