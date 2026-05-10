from mysql.connector import Error

class DBPieza:
    def __init__(self, conexion):
        self.conexion = conexion

    def crear_pieza(self, numero_serie, descripcion, precio, existencias):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO piezas (numero_serie, descripcion, precio, existencias)
                VALUES (%s, %s, %s, %s)
            """, (numero_serie, descripcion, precio, existencias))
            conn.commit()
            return True, "Pieza creada exitosamente"
        except Error as e:
            if "Duplicate entry" in str(e):
                return False, "Ya existe una pieza con ese número de serie"
            return False, f"Error al crear pieza: {e}"
        finally:
            cursor.close()
            conn.close()

    def listar_piezas(self):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM piezas ORDER BY pieza_id")
            return cursor.fetchall()
        except Error as e:
            print("Error al listar piezas:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_pieza_por_id(self, pieza_id):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM piezas WHERE pieza_id = %s", (pieza_id,))
            return cursor.fetchone()
        except Error as e:
            print("Error al buscar pieza:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def buscar_pieza_por_nombre(self, criterio):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM piezas 
                WHERE descripcion LIKE %s OR numero_serie LIKE %s
            """, (f"%{criterio}%", f"%{criterio}%"))
            return cursor.fetchall()
        except Error as e:
            print("Error al buscar pieza:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def actualizar_pieza(self, pieza_id, numero_serie, descripcion, precio, existencias):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE piezas 
                SET numero_serie=%s, descripcion=%s, precio=%s, existencias=%s
                WHERE pieza_id=%s
            """, (numero_serie, descripcion, precio, existencias, pieza_id))
            conn.commit()
            return True, "Pieza actualizada exitosamente"
        except Error as e:
            if "Duplicate entry" in str(e):
                return False, "Ya existe una pieza con ese número de serie"
            return False, f"Error al actualizar pieza: {e}"
        finally:
            cursor.close()
            conn.close()

    def eliminar_pieza(self, pieza_id):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM piezas WHERE pieza_id=%s", (pieza_id,))
            conn.commit()
            return True, "Pieza eliminada exitosamente"
        except Error as e:
            return False, f"Error al eliminar pieza: {e}"
        finally:
            cursor.close()
            conn.close()

    def actualizar_existencias(self, pieza_id, cantidad):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE piezas SET existencias = existencias - %s WHERE pieza_id = %s", 
                         (cantidad, pieza_id))
            conn.commit()
            return True, "Existencias actualizadas"
        except Error as e:
            return False, f"Error al actualizar existencias: {e}"
        finally:
            cursor.close()
            conn.close()