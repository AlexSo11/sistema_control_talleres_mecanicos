"""Acceso a datos de usuarios y autenticación (hash SHA-256)."""

import hashlib
from conexion import ConexionDB
from mysql.connector import Error

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DBUsuario:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_usuario(self, username, password, nombre='', apellido='', email='', telefono='', rol='auxiliar'):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        try:
            pw_hash = hash_password(password)
            cursor = conn.cursor()
            sql = ("INSERT INTO usuarios (username, password_hash, nombre, apellido, email, telefono, rol) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(sql, (username, pw_hash, nombre, apellido, email, telefono, rol))
            conn.commit()
            return True, "Usuario creado correctamente"
        except Error as e:
            return False, f"Error al crear usuario: {e}"
        finally:
            cursor.close()
            conn.close()

    def autenticar(self, username, password):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la BD"
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM usuarios WHERE username = %s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado"
            if row['password_hash'] == hash_password(password):
                user = {k:v for k,v in row.items() if k != 'password_hash'}
                return True, user
            else:
                return False, "Contraseña incorrecta"
        except Error as e:
            return False, f"Error en autenticación: {e}"
        finally:
            cursor.close()
            conn.close()

    def listar_usuarios(self):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, nombre, apellido, email, telefono, rol, creado_en FROM usuarios")
            rows = cursor.fetchall()
            return rows
        except Error:
            return []
        finally:
            cursor.close()
            conn.close()

    def buscar_usuario_por_id(self, user_id):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, nombre, apellido, email, telefono, rol, creado_en FROM usuarios WHERE id = %s", (user_id,))
            return cursor.fetchone()
        except Error:
            return None
        finally:
            cursor.close()
            conn.close()

    def buscar_usuario_por_username(self, username):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, nombre, apellido, email, telefono, rol, creado_en FROM usuarios WHERE username = %s", (username,))
            return cursor.fetchone()
        except Error:
            return None
        finally:
            cursor.close()
            conn.close()

    def actualizar_usuario(self, user_id, nombre, apellido, email, telefono, rol):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        try:
            cursor = conn.cursor()
            sql = ("UPDATE usuarios SET nombre=%s, apellido=%s, email=%s, telefono=%s, rol=%s WHERE id=%s")
            cursor.execute(sql, (nombre, apellido, email, telefono, rol, user_id))
            conn.commit()
            return True, "Usuario actualizado"
        except Error as e:
            return False, f"Error al actualizar: {e}"
        finally:
            cursor.close()
            conn.close()

    def actualizar_contrasena(self, user_id, nueva_password):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        try:
            pw_hash = hash_password(nueva_password)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password_hash=%s WHERE id=%s", (pw_hash, user_id))
            conn.commit()
            return True, "Contraseña actualizada"
        except Error as e:
            return False, f"Error al actualizar contraseña: {e}"
        finally:
            cursor.close()
            conn.close()

    def tiene_clientes_asignados(self, user_id):
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario_id=%s", (user_id,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()
            conn.close()

    def eliminar_usuario(self, user_id):
        if self.tiene_clientes_asignados(user_id):
            return False, "No se puede eliminar: el usuario tiene clientes asignados."
        
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
            conn.commit()
            return True, "Usuario eliminado"
        except Error as e:
            return False, f"Error al eliminar: {e}"
        finally:
            cursor.close()
            conn.close()