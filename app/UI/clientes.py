"""Interfaz de gestión de clientes."""

import tkinter as tk
from tkinter import ttk, messagebox
from DB.dbCliente import DBCliente
from DB.dbUsuario import DBUsuario
from conexion import ConexionDB

class ClientesUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        self.con = ConexionDB()
        self.dbClientes = DBCliente(self.con)
        self.dbUsuarios = DBUsuario(self.con)

        # Verificar si es mecánico ANTES de construir UI
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        
        if rol == 'mecanico':
            # Mecánico no puede acceder a clientes
            ttk.Label(self.frame, text="Acceso denegado: Los mecánicos no pueden gestionar clientes", 
                    font=("Segoe UI", 12), foreground="red").pack(expand=True)
            return

        # Variables
        self.var_id = tk.StringVar()
        self.var_usuario = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_ap = tk.StringVar()
        self.var_am = tk.StringVar()
        self.var_tel = tk.StringVar()
        self.var_rfc = tk.StringVar()
        self.var_buscar = tk.StringVar()

        self.build_ui()
        self.cargar_clientes()
        self.aplicar_restricciones_rol()
        self.set_estado("inicio")

    def aplicar_restricciones_rol(self):
        """Aplicar restricciones según el rol del usuario"""
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        
        if rol == 'auxiliar':# Auxiliar solo puede: Nuevo, Guardar, Buscar
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")

    def build_ui(self):
        form = ttk.LabelFrame(self.frame, text="Datos Cliente", padding=9)
        form.pack(side='left', fill='y', padx=(0,9))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w')
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly')
        self.entry_id.grid(row=0, column=1, pady=2)

        ttk.Label(form, text="Usuario:").grid(row=1, column=0, sticky='w')
        # Campo de usuario bloqueado con el usuario logeado
        if self.usuario_actual:
            self.var_usuario.set(self.usuario_actual.get('username', ''))
        self.entry_usuario = ttk.Entry(form, textvariable=self.var_usuario, state='readonly')
        self.entry_usuario.grid(row=1, column=1, pady=2)

        ttk.Label(form, text="Nombre:").grid(row=2, column=0, sticky='w')
        self.entry_nombre = ttk.Entry(form, textvariable=self.var_nombre)
        self.entry_nombre.grid(row=2, column=1, pady=2)

        ttk.Label(form, text="Apellido Paterno:").grid(row=3, column=0, sticky='w')
        self.entry_ap = ttk.Entry(form, textvariable=self.var_ap)
        self.entry_ap.grid(row=3, column=1, pady=2)

        ttk.Label(form, text="Apellido Materno:").grid(row=4, column=0, sticky='w')
        self.entry_am = ttk.Entry(form, textvariable=self.var_am)
        self.entry_am.grid(row=4, column=1, pady=2)

        ttk.Label(form, text="Teléfono:").grid(row=5, column=0, sticky='w')
        self.entry_tel = ttk.Entry(form, textvariable=self.var_tel)
        self.entry_tel.grid(row=5, column=1, pady=2)

        ttk.Label(form, text="RFC:").grid(row=6, column=0, sticky='w')
        self.entry_rfc = ttk.Entry(form, textvariable=self.var_rfc)
        self.entry_rfc.grid(row=6, column=1, pady=2)

        # botones
        btns = ttk.Frame(form)
        btns.grid(row=7, column=0, columnspan=2, pady=(10,0))
        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo)
        self.btn_nuevo.grid(row=0, column=0, padx=4)
        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar)
        self.btn_guardar.grid(row=0, column=1, padx=4)
        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar)
        self.btn_editar.grid(row=0, column=2, padx=4)
        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar)
        self.btn_actualizar.grid(row=0, column=3, padx=4)
        self.btn_eliminar = ttk.Button(btns, text="Eliminar", command=self.eliminar)
        self.btn_eliminar.grid(row=1, column=0, padx=4, pady=(5,0))
        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar)
        self.btn_cancelar.grid(row=1, column=1, padx=4, pady=(5,0))
        self.btn_buscar = ttk.Button(btns, text="Buscar", command=self.buscar)
        self.btn_buscar.grid(row=1, column=2, padx=5, pady=(5,0))

        # tabla
        right = ttk.Frame(self.frame)
        right.pack(side='left', fill='both', expand=True)

        search_frame = ttk.Frame(right, padding=(0, 0, 0, 10))
        search_frame.pack(fill='x')
        
        ttk.Label(search_frame, text="Buscar (ID o Nombre):").pack(side='left', padx=(0, 5))
        self.entry_buscar = ttk.Entry(search_frame, textvariable=self.var_buscar, width=30)
        self.entry_buscar.pack(side='left', padx=(0, 5))
        self.entry_buscar.bind('<Return>', lambda e: self.buscar())
        
        ttk.Button(search_frame, text="Buscar", command=self.buscar).pack(side='left', padx=(0, 5))
        ttk.Button(search_frame, text="Mostrar Todos", command=self.mostrar_todos).pack(side='left')

        # Treeview
        cols = ("cliente_id", "usuario_nombre", "nombre", "apellido_paterno", "apellido_materno", "telefono", "rfc", "creado_en")
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        
        # Configurar columnas
        self.tree.heading("cliente_id", text="ID")
        self.tree.heading("usuario_nombre", text="Usuario")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido_paterno", text="Apellido Paterno")
        self.tree.heading("apellido_materno", text="Apellido Materno")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("rfc", text="RFC")
        self.tree.heading("creado_en", text="Creado En")
        
        self.tree.column("cliente_id", width=40, anchor="center")
        self.tree.column("usuario_nombre", width=100)
        self.tree.column("nombre", width=100)
        self.tree.column("apellido_paterno", width=110)
        self.tree.column("apellido_materno", width=110)
        self.tree.column("telefono", width=90)
        self.tree.column("rfc", width=100)
        self.tree.column("creado_en", width=120)
        
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'

        if modo == "nuevo":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="normal")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_buscar.config(state="disabled")
        elif modo == "editar":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="normal")
            self.btn_eliminar.config(state="disabled")
            self.btn_buscar.config(state="disabled")
        elif modo in ("salvar", "cancelar", "remover", "inicio"):
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="disabled")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_buscar.config(state="normal")
        elif modo == "buscar":
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="normal")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="normal")
            self.btn_buscar.config(state="normal")

        if rol == 'auxiliar':
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")

        for entry in (self.entry_nombre, self.entry_ap, self.entry_am, self.entry_rfc, self.entry_tel):
            entry.config(state=estado)

    def limpiar(self):
        self.var_id.set('')
        if self.usuario_actual:
            self.var_usuario.set(self.usuario_actual.get('username', ''))
        self.var_nombre.set('')
        self.var_ap.set('')
        self.var_am.set('')
        self.var_tel.set('')
        self.var_rfc.set('')

    def nuevo(self):
        self.limpiar()
        self.set_estado("nuevo")

    def guardar(self):
        """Guardar NUEVO cliente"""
        usuario = self.var_usuario.get().strip()
        nombre = self.var_nombre.get().strip()
        ap = self.var_ap.get().strip()
        am = self.var_am.get().strip()
        telefono = self.var_tel.get().strip()
        rfc = self.var_rfc.get().strip()

        if not all([usuario, nombre, ap, am, telefono, rfc]):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return
        
        if len(rfc) < 13:
            messagebox.showwarning("Validación", "RFC debe de incluir 13 digitos")
            return
        
        # Obtener el ID del usuario logeado
        if self.usuario_actual:
            user_id = self.usuario_actual.get('id')
        else:
            messagebox.showerror("Error", "No hay usuario logeado")
            return
        
        # Verificar si ya existe un cliente con el mismo RFC
        clientes_existentes = self.dbClientes.listar_clientes()
        for cliente in clientes_existentes:
            if cliente['rfc'] == rfc:
                messagebox.showerror("Error", f"Ya existe un cliente con el RFC: {rfc}")
                return
        
        ok, msg = self.dbClientes.crear_cliente(user_id, nombre, ap, am, telefono, rfc)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_clientes()
            self.limpiar()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar(self):
        """Activar modo edición para cliente existente"""
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Seleccione un cliente primero")
            return
        self.set_estado("editar")

    def actualizar(self):
        """Actualizar cliente existente"""
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Seleccione un cliente primero")
            return
        
        usuario = self.var_usuario.get().strip()
        nombre = self.var_nombre.get().strip()
        ap = self.var_ap.get().strip()
        am = self.var_am.get().strip()
        telefono = self.var_tel.get().strip()
        rfc = self.var_rfc.get().strip()

        if not all([usuario, nombre, ap, am, telefono, rfc]):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return
        if len(rfc) < 13:
            messagebox.showwarning("Validación", "RFC debe de incluir 13 digitos")
            return
        # Obtener el ID del usuario logeado
        if self.usuario_actual:
            user_id = self.usuario_actual.get('id')
        else:
            messagebox.showerror("Error", "No hay usuario logeado")
            return
        
        # Verificar si el RFC ya existe en otro cliente
        clientes_existentes = self.dbClientes.listar_clientes()
        for cliente in clientes_existentes:
            if cliente['rfc'] == rfc and str(cliente['cliente_id']) != self.var_id.get():
                messagebox.showerror("Error", f"Ya existe otro cliente con el RFC: {rfc}")
                return
        
        ok, msg = self.dbClientes.actualizar_cliente(
            int(self.var_id.get()), user_id, nombre, ap, am, telefono, rfc
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_clientes()
            self.limpiar()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Seleccione un cliente primero")
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este cliente?"):
            ok, msg = self.dbClientes.eliminar_cliente(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_clientes()
                self.limpiar()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar(self):
        self.limpiar()
        self.set_estado("cancelar")

    def buscar(self):
        criterio = self.var_buscar.get().strip()
        if not criterio:
            messagebox.showwarning("Validación", "Ingrese un criterio de búsqueda")
            return
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        resultados = []
        
        if criterio.isdigit():
            cliente_por_id = self.dbClientes.buscar_cliente_por_id_con_usuario(int(criterio))
            if cliente_por_id:
                resultados = [cliente_por_id]
        
        if not resultados:
            # Buscar por nombre en los resultados con usuario
            todos_clientes = self.dbClientes.listar_clientes_con_usuario()
            resultados = [c for c in todos_clientes if criterio.lower() in c['nombre'].lower()]
        
        if not resultados:
            messagebox.showinfo("Buscar", "No se encontraron clientes")
            return
        
        for cliente in resultados:
            self.tree.insert('', 'end', values=(
                cliente["cliente_id"],
                cliente.get("usuario_nombre", ""),
                cliente["nombre"], 
                cliente["apellido_paterno"],
                cliente["apellido_materno"],
                cliente["telefono"],
                cliente["rfc"],
                cliente["creado_en"]
            ))
        
        if len(resultados) == 1:
            c = resultados[0]
            self.var_id.set(c['cliente_id'])
            self.var_usuario.set(c.get('usuario_nombre', ''))
            self.var_nombre.set(c.get('nombre', ''))
            self.var_ap.set(c.get('apellido_paterno', ''))
            self.var_am.set(c.get('apellido_materno', ''))
            self.var_tel.set(c.get('telefono', ''))
            self.var_rfc.set(c.get('rfc', ''))
            self.set_estado("buscar")
            
            for item in self.tree.get_children():
                if str(self.tree.item(item, 'values')[0]) == str(c['cliente_id']):
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break

    def mostrar_todos(self):
        self.var_buscar.set('')
        self.cargar_clientes()
        self.limpiar()
        self.set_estado("inicio")

    def cargar_clientes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Usar el nuevo método que incluye el nombre de usuario
        clientes = self.dbClientes.listar_clientes_con_usuario()
        for c in clientes:
            self.tree.insert('', 'end', values=(
                c["cliente_id"],
                c.get("usuario_nombre", ""),
                c["nombre"], 
                c["apellido_paterno"],
                c["apellido_materno"],
                c["telefono"],
                c["rfc"],
                c["creado_en"]
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], 'values')
        self.var_id.set(values[0])
        self.var_usuario.set(values[1])  # Ahora es el nombre de usuario, no el ID
        self.var_nombre.set(values[2])
        self.var_ap.set(values[3])
        self.var_am.set(values[4])
        self.var_tel.set(values[5])
        self.var_rfc.set(values[6])
        self.set_estado("buscar")
