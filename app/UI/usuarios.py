"""Interfaz de gestión de usuarios."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from DB.dbUsuario import DBUsuario
from conexion import ConexionDB

class UsuariosUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBUsuario(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # Verificar si es admin
        if not usuario_actual or usuario_actual.get('rol') != 'admin':
            ttk.Label(self.frame, text="Acceso denegado: Solo administradores pueden gestionar usuarios", 
                     font=("Segoe UI", 12), foreground="red").pack(expand=True)
            return

        # Variables
        self.var_id = tk.StringVar()
        self.var_username = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_rol = tk.StringVar(value='auxiliar')

        # Construir UI
        self.build_ui()
        self.cargar_usuarios()
        self.set_estado("inicio")

    def build_ui(self):
        frm = ttk.Frame(self.frame, padding=10)
        frm.pack(fill='both', expand=True)

        form = ttk.LabelFrame(frm, text="Datos usuario", padding=10)
        form.pack(side='left', fill='y', padx=(0,10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w')
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly')
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Usuario:").grid(row=1, column=0, sticky='w')
        self.entry_username = ttk.Entry(form, textvariable=self.var_username)
        self.entry_username.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Nombre:").grid(row=2, column=0, sticky='w')
        self.entry_nombre = ttk.Entry(form, textvariable=self.var_nombre)
        self.entry_nombre.grid(row=2, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Apellido:").grid(row=3, column=0, sticky='w')
        self.entry_apellido = ttk.Entry(form, textvariable=self.var_apellido)
        self.entry_apellido.grid(row=3, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Email:").grid(row=4, column=0, sticky='w')
        self.entry_email = ttk.Entry(form, textvariable=self.var_email)
        self.entry_email.grid(row=4, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Teléfono:").grid(row=5, column=0, sticky='w')
        self.entry_telefono = ttk.Entry(form, textvariable=self.var_telefono)
        self.entry_telefono.grid(row=5, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Rol:").grid(row=6, column=0, sticky='w')
        self.combo_rol = ttk.Combobox(form, values=['admin', 'auxiliar', 'mecanico'], textvariable=self.var_rol, state='readonly')
        self.combo_rol.grid(row=6, column=1, sticky='ew', pady=2)

        # Botones
        btns = ttk.Frame(form)
        btns.grid(row=7, column=0, columnspan=2, pady=(10,0))

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_usuario)
        self.btn_nuevo.grid(row=0, column=0, padx=4)

        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_usuario)
        self.btn_guardar.grid(row=0, column=1, padx=4)

        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_usuario)
        self.btn_editar.grid(row=0, column=2, padx=4)

        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_usuario)
        self.btn_actualizar.grid(row=0, column=3, padx=4)

        self.btn_eliminar = ttk.Button(btns, text="Eliminar", command=self.eliminar_usuario)
        self.btn_eliminar.grid(row=1, column=0, padx=4, pady=(5,0))

        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion)
        self.btn_cancelar.grid(row=1, column=1, padx=4, pady=(5,0))

        ttk.Button(btns, text="Cambiar contraseña", command=self.cambiar_contrasena).grid(row=1, column=2, columnspan=2, pady=(5,0))

        # Listado
        right = ttk.Frame(frm)
        right.pack(side='left', fill='both', expand=True)

        searchfrm = ttk.Frame(right, padding=(0,0,0,6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Buscar (usuario o id):").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(searchfrm, textvariable=self.search_var).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_usuarios).pack(side='left', padx=6)

        cols = ("id","username","nombre","apellido","email","telefono","rol")
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Usuario")
        self.tree.heading("nombre", text="Nombre") 
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("email", text="Email")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("rol", text="ROL")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("username", width=70, anchor="center")
        self.tree.column("nombre", width=100) 
        self.tree.column("apellido", width=100)
        self.tree.column("email", width=120)
        self.tree.column("telefono", width=70, anchor="center")
        self.tree.column("rol", width=60, anchor="center")
        
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        if modo == "nuevo":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="normal")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
        elif modo == "editar":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="normal")
            self.btn_eliminar.config(state="disabled")
        elif modo in ("salvar", "cancelar", "remover", "inicio"):
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="disabled")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
        elif modo == "buscar":
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="normal")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="normal")

        for entry in (self.entry_username, self.entry_nombre, self.entry_apellido,
                      self.entry_email, self.entry_telefono):
            entry.config(state=estado) # type: ignore
        self.combo_rol.config(state="readonly" if estado == "normal" else "disabled") # type: ignore

    def limpiar_form(self):
        self.var_id.set('')
        self.var_username.set('')
        self.var_nombre.set('')
        self.var_apellido.set('')
        self.var_email.set('')
        self.var_telefono.set('')
        self.var_rol.set('auxiliar')

    def nuevo_usuario(self):
        self.limpiar_form()
        self.set_estado("nuevo")

    def guardar_usuario(self):
        username = self.var_username.get().strip()
        if not username:
            messagebox.showwarning("Validación", "El usuario (username) es requerido.")
            return
        password = simpledialog.askstring("Contraseña", f"Ingrese contraseña para {username}", show='*')
        if not password:
            return
        ok, msg = self.db.crear_usuario(username, password,
                                        self.var_nombre.get().strip(),
                                        self.var_apellido.get().strip(),
                                        self.var_email.get().strip(),
                                        self.var_telefono.get().strip(),
                                        self.var_rol.get().strip())
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_usuarios()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_usuario(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un usuario.")
            return
        self.set_estado("editar")

    def actualizar_usuario(self):
        if not self.var_id.get():
            return
        ok, msg = self.db.actualizar_usuario(int(self.var_id.get()),
                                             self.var_nombre.get().strip(),
                                             self.var_apellido.get().strip(),
                                             self.var_email.get().strip(),
                                             self.var_telefono.get().strip(),
                                             self.var_rol.get().strip())
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_usuarios()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_usuario(self):
        if not self.var_id.get():
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este usuario?"):
            ok, msg = self.db.eliminar_usuario(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_usuarios()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cambiar_contrasena(self):
        if not self.var_id.get():
            return
        nueva = simpledialog.askstring("Nueva contraseña", "Ingrese la nueva contraseña:", show='*')
        if not nueva:
            return
        ok, msg = self.db.actualizar_contrasena(int(self.var_id.get()), nueva)
        if ok:
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def cargar_usuarios(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.db.listar_usuarios()
        for r in rows:
            self.tree.insert('', 'end', values=(r['id'], r['username'], r['nombre'] or '',
                                                r['apellido'] or '', r['email'] or '',
                                                r['telefono'] or '', r['rol'] or '',
                                                r['creado_en']))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], 'values')
        self.var_id.set(values[0])
        self.var_username.set(values[1])
        self.var_nombre.set(values[2])
        self.var_apellido.set(values[3])
        self.var_email.set(values[4])
        self.var_telefono.set(values[5])
        self.var_rol.set(values[6])
        self.set_estado("buscar")

    def buscar(self):
        q = self.search_var.get().strip()
        if not q:
            self.cargar_usuarios()
            return
        user = None
        if q.isdigit():
            user = self.db.buscar_usuario_por_id(int(q))
        if not user:
            user = self.db.buscar_usuario_por_username(q)
        if not user:
            messagebox.showinfo("Buscar", "Usuario no encontrado")
            return
        self.var_id.set(user['id'])
        self.var_username.set(user['username'])
        self.var_nombre.set(user.get('nombre',''))
        self.var_apellido.set(user.get('apellido',''))
        self.var_email.set(user.get('email',''))
        self.var_telefono.set(user.get('telefono',''))
        self.var_rol.set(user.get('rol','auxiliar'))
        self.set_estado("buscar")
