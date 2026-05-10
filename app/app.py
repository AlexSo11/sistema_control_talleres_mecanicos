"""
⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣿⡿⠗⠀⠠⠄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⠈⠑⢶⣶⡄
⢀⣶⣦⣸⠀⢼⣟⡇⠀⠀⢀⣀⠀⠘⡿⠃
⠀⢿⣿⣿⣄⠒⠀⠠⢶⡂⢫⣿⢇⢀⠃⠀
⠀⠈⠻⣿⣿⣿⣶⣤⣀⣀⣀⣂⡠⠊⠀⠀
⠀⠀⠀⠃⠀⠀⠉⠙⠛⠿⣿⣿⣧⠀⠀⠀
⠀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠘⣿⣿⡇⠀⠀
⠀⠀⠀⣷⣄⡀⠀⠀⠀⢀⣴⡟⠿⠃⠀⠀
⠀⠀⠀⢻⣿⣿⠉⠉⢹⣿⣿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠁⠀⠀⠀⠉⠁

Desarrollo AlexWhite USER GIT AlexSo11
"""
import tkinter as tk
from tkinter import ttk, messagebox
from conexion import ConexionDB

from UI.clientes import ClientesUI
from UI.vehiculos import VehiculosUI
from UI.reparaciones import ReparacionesUI
from UI.piezas import PiezasUI
from UI.usuarios import UsuariosUI

from DB.dbUsuario import DBUsuario
from DB.dbReparaciones import DBReparacion
from DB.dbPiezas import DBPieza

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dbtaller_mecanico'
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Taller - Login")
        self.root.geometry("300x230")
        self.root.resizable(False, False)
        self.con = ConexionDB(**DB_CONFIG)
        self.db = DBUsuario(self.con)
        self.usuario_actual = None
        self.build_login()

    def build_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frm = ttk.Frame(self.root, padding=20)
        frm.pack(expand=True, fill='both')

        ttk.Label(frm, text="Login", font=("Segoe UI", 22)).pack(pady=(0,10))

        ttk.Label(frm, text="Usuario:").pack(anchor='w')
        self.entry_user = ttk.Entry(frm)
        self.entry_user.pack(fill='x')

        ttk.Label(frm, text="Contraseña:").pack(anchor='w', pady=(8,0))
        self.entry_pass = ttk.Entry(frm, show="*")
        self.entry_pass.pack(fill='x')

        ttk.Button(frm, text="Entrar", command=self.login).pack(pady=12)
        ttk.Button(frm, text="Crear cuenta (demo)", command=self.crear_cuenta_demo).pack()

    def crear_cuenta_demo(self):
        # Crear usuario admin si no existe
        exists = self.db.buscar_usuario_por_username('admin')
        if not exists:
            ok, msg = self.db.crear_usuario('admin', 'admin123', nombre='Administrador', rol='admin')
            messagebox.showinfo("Crear cuenta", f"Admin: {msg}")
        
        # Crear usuario auxiliar si no existe
        exists = self.db.buscar_usuario_por_username('auxiliar')
        if not exists:
            ok, msg = self.db.crear_usuario('auxiliar', 'auxiliar123', nombre='Auxiliar Demo', rol='auxiliar')
            messagebox.showinfo("Crear cuenta", f"Auxiliar: {msg}")
        
        # Crear usuario mecánico si no existe
        exists = self.db.buscar_usuario_por_username('mecanico')
        if not exists:
            ok, msg = self.db.crear_usuario('mecanico', 'mecanico123', nombre='Mecánico Demo', rol='mecanico')
            messagebox.showinfo("Crear cuenta", f"Mecánico: {msg}")

    def login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Validación", "Introduce usuario y contraseña.")
            return
        ok, resp = self.db.autenticar(u, p)
        if ok:
            self.usuario_actual = resp
            self.build_menu()
        else:
            messagebox.showerror("Error", resp)

    def build_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("")
        self.root.resizable(True, True)
        
        menubar = tk.Menu(self.root, bg="black", fg="white", activebackground="red", activeforeground="yellow")
        self.root.config(menu=menubar)
        menubar.add_command(label="Cerrar sesión", activebackground="dark slate gray", activeforeground="black", command=self.cerrar_sesion)
        menubar.add_command(label="Salir", command=self.root.quit)

        header = ttk.Frame(self.root, padding=10)
        header.pack(fill='x')
        ttk.Label(header, text=f"Bienvenido: {self.usuario_actual.get('username')}", font=("Segoe UI", 14)).pack(side='left')
        ttk.Label(header, text=f"Rol: {self.usuario_actual.get('rol')}", font=("Segoe UI", 10)).pack(side='right')

        tab_control = ttk.Notebook(self.root)

        # Usuarios (admin)
        if self.usuario_actual.get('rol') == 'admin':
            self.tab_usuarios = ttk.Frame(tab_control)
            tab_control.add(self.tab_usuarios, text='Usuarios')
            UsuariosUI(self.tab_usuarios, self.usuario_actual)

        # Clientes (admin y auxiliar)
        if self.usuario_actual.get('rol') in ['admin', 'auxiliar']:
            self.tab_clientes = ttk.Frame(tab_control)
            tab_control.add(self.tab_clientes, text='Clientes')
            ClientesUI(self.tab_clientes, self.usuario_actual)

        # Vehículos (admin y auxiliar)
        if self.usuario_actual.get('rol') in ['admin', 'auxiliar']:
            self.tab_vehiculos = ttk.Frame(tab_control)
            tab_control.add(self.tab_vehiculos, text='Vehículos')
            VehiculosUI(self.tab_vehiculos, self.usuario_actual)

        # Reparaciones (admin y mecanico)
        if self.usuario_actual.get('rol') in ['admin', 'mecanico']:
            self.tab_reparaciones = ttk.Frame(tab_control)
            tab_control.add(self.tab_reparaciones, text='Reparaciones')
            ReparacionesUI(self.tab_reparaciones, self.usuario_actual)

        # Piezas (admin)
        if self.usuario_actual.get('rol') == 'admin':
            self.tab_piezas = ttk.Frame(tab_control)
            tab_control.add(self.tab_piezas, text='Piezas')
            PiezasUI(self.tab_piezas, self.usuario_actual)

        tab_control.pack(fill='both', expand=True, padx=5, pady=5)

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.root.geometry("300x230")
        self.root.resizable(False, False)
        self.build_login()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
