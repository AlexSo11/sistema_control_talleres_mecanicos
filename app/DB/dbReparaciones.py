"""Acceso a datos de reparaciones y sus piezas."""

from mysql.connector import Error

class DBReparacion:
    def __init__(self, conexion):
        self.conexion = conexion

    def crear_reparacion(self, matricula, usuario_id, fecha_entrada, fecha_salida, descripcion, piezas_data):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        
        cursor = conn.cursor()
        try:
            if conn.in_transaction:# Verificar si hay una transacción en progreso
                conn.rollback()
            
            for pieza in piezas_data:# Verificar stock antes de iniciar transacción
                cursor.execute("SELECT existencias FROM piezas WHERE pieza_id = %s", (pieza['pieza_id'],))
                resultado = cursor.fetchone()
                if not resultado or resultado[0] < pieza['cantidad']:
                    return False, f"Stock insuficiente para la pieza ID: {pieza['pieza_id']}"
            cursor.execute("START TRANSACTION")

            # Insertar reparación
            cursor.execute("""
                INSERT INTO reparaciones (matricula, usuario_id, fecha_entrada, fecha_salida, descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (matricula, usuario_id, fecha_entrada, fecha_salida, descripcion))

            folio = cursor.lastrowid
            
            for pieza in piezas_data:# Insertar piezas de la reparación y actualizar existencias
                cursor.execute("""
                    INSERT INTO reparacion_piezas (folio_reparacion, pieza_id, cantidad)
                    VALUES (%s, %s, %s)
                """, (folio, pieza['pieza_id'], pieza['cantidad']))
                
                # Actualizar existencias
                cursor.execute("UPDATE piezas SET existencias = existencias - %s WHERE pieza_id = %s", 
                             (pieza['cantidad'], pieza['pieza_id']))

            cursor.execute("COMMIT")
            return True, f"Reparación creada exitosamente. Folio: {folio}"

        except Error as e:
            try:
                cursor.execute("ROLLBACK")
            except:
                pass
            return False, f"Error al crear reparación: {e}"
        finally:
            cursor.close()
            conn.close()

    def actualizar_reparacion(self, folio, matricula, fecha_entrada, fecha_salida, descripcion, piezas_data):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        
        cursor = conn.cursor()
        try:
            # Verificar si hay una transacción en progreso
            if conn.in_transaction:
                conn.rollback()
            
            # Verificar stock antes de iniciar transacción (solo para nuevas cantidades)
            piezas_actuales = self.obtener_piezas_reparacion(folio)
            
            # Calcular diferencias de stock
            for nueva_pieza in piezas_data:
                pieza_actual = next((p for p in piezas_actuales if p['pieza_id'] == nueva_pieza['pieza_id']), None)
                cantidad_actual = pieza_actual['cantidad'] if pieza_actual else 0
                diferencia = nueva_pieza['cantidad'] - cantidad_actual
                
                if diferencia > 0:  # Si estamos agregando más piezas
                    cursor.execute("SELECT existencias FROM piezas WHERE pieza_id = %s", (nueva_pieza['pieza_id'],))
                    resultado = cursor.fetchone()
                    if not resultado or resultado[0] < diferencia:
                        return False, f"Stock insuficiente para la pieza ID: {nueva_pieza['pieza_id']}. Se necesitan {diferencia} unidades adicionales"

            # Iniciar transacción
            cursor.execute("START TRANSACTION")

            # Actualizar reparación
            cursor.execute("""
                UPDATE reparaciones 
                SET matricula = %s, fecha_entrada = %s, fecha_salida = %s, descripcion = %s
                WHERE folio = %s
            """, (matricula, fecha_entrada, fecha_salida, descripcion, folio))

            # Obtener piezas actuales para restaurar stock
            cursor.execute("SELECT pieza_id, cantidad FROM reparacion_piezas WHERE folio_reparacion = %s", (folio,))
            piezas_actuales = cursor.fetchall()
            
            # Restaurar existencias de todas las piezas actuales
            for pieza in piezas_actuales:
                cursor.execute("UPDATE piezas SET existencias = existencias + %s WHERE pieza_id = %s", 
                             (pieza[1], pieza[0]))

            # Eliminar todas las piezas actuales de la reparación
            cursor.execute("DELETE FROM reparacion_piezas WHERE folio_reparacion = %s", (folio,))

            # Insertar nuevas piezas y actualizar existencias
            for pieza in piezas_data:
                cursor.execute("""
                    INSERT INTO reparacion_piezas (folio_reparacion, pieza_id, cantidad)
                    VALUES (%s, %s, %s)
                """, (folio, pieza['pieza_id'], pieza['cantidad']))
                
                # Actualizar existencias (restamos la nueva cantidad)
                cursor.execute("UPDATE piezas SET existencias = existencias - %s WHERE pieza_id = %s", 
                             (pieza['cantidad'], pieza['pieza_id']))

            cursor.execute("COMMIT")
            return True, "Reparación actualizada exitosamente"

        except Error as e:
            try:
                cursor.execute("ROLLBACK")
            except:
                pass
            return False, f"Error al actualizar reparación: {e}"
        finally:
            cursor.close()
            conn.close()

    def listar_reparaciones(self):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, v.marca, v.modelo, u.username as usuario_nombre,
                       (SELECT COUNT(*) FROM reparacion_piezas rp WHERE rp.folio_reparacion = r.folio) as total_piezas
                FROM reparaciones r
                LEFT JOIN vehiculos v ON r.matricula = v.matricula
                LEFT JOIN usuarios u ON r.usuario_id = u.id
                ORDER BY r.folio DESC
            """)
            return cursor.fetchall()
        except Error as e:
            print("Error al listar reparaciones:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_reparacion_por_folio(self, folio):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, v.marca, v.modelo, u.username as usuario_nombre
                FROM reparaciones r
                LEFT JOIN vehiculos v ON r.matricula = v.matricula
                LEFT JOIN usuarios u ON r.usuario_id = u.id
                WHERE r.folio = %s
            """, (folio,))
            return cursor.fetchone()
        except Error as e:
            print("Error al buscar reparación:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def obtener_piezas_reparacion(self, folio):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT rp.*, p.descripcion, p.numero_serie, p.existencias as stock_actual
                FROM reparacion_piezas rp
                LEFT JOIN piezas p ON rp.pieza_id = p.pieza_id
                WHERE rp.folio_reparacion = %s
            """, (folio,))
            return cursor.fetchall()
        except Error as e:
            print("Error al obtener piezas de reparación:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    def eliminar_reparacion(self, folio):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión con la BD"
        
        cursor = conn.cursor()
        try:
            # Verificar si hay una transacción en progreso
            if conn.in_transaction:
                conn.rollback()
            
            cursor.execute("START TRANSACTION")
            
            # Primero restaurar las existencias de las piezas
            cursor.execute("SELECT pieza_id, cantidad FROM reparacion_piezas WHERE folio_reparacion = %s", (folio,))
            piezas = cursor.fetchall()
            
            for pieza in piezas:
                cursor.execute("UPDATE piezas SET existencias = existencias + %s WHERE pieza_id = %s", 
                             (pieza[1], pieza[0]))
            
            # Eliminar las piezas de la reparación
            cursor.execute("DELETE FROM reparacion_piezas WHERE folio_reparacion = %s", (folio,))
            
            # Eliminar la reparación
            cursor.execute("DELETE FROM reparaciones WHERE folio = %s", (folio,))
            
            cursor.execute("COMMIT")
            return True, "Reparación eliminada exitosamente"

        except Error as e:
            try:
                cursor.execute("ROLLBACK")
            except:
                pass
            return False, f"Error al eliminar reparación: {e}"
        finally:
            cursor.close()
            conn.close()