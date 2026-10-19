"""Interfaz de gestión de vehículos."""

import tkinter as tk
from tkinter import ttk, messagebox
from DB.dbVehiculos import DBVehiculo
from DB.dbCliente import DBCliente 
from conexion import ConexionDB

class VehiculosUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        self.con = ConexionDB()
        self.dbVehiculos = DBVehiculo(self.con)
        self.dbClientes = DBCliente(self.con) 

        # Verificar rol ANTES de construir UI
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        
        if rol == 'mecanico':
            ttk.Label(self.frame, text="Acceso denegado: Los mecánicos no pueden gestionar vehículos", 
                    font=("Segoe UI", 12), foreground="red").pack(expand=True)
            return

        # Variables
        self.var_matricula = tk.StringVar()
        self.var_cliente_id = tk.StringVar()
        self.var_cliente_nombre = tk.StringVar()
        self.var_cliente = tk.StringVar()
        self.var_marca = tk.StringVar()
        self.var_modelo = tk.StringVar()
        self.var_ano = tk.StringVar()
        self.var_color = tk.StringVar()
        self.var_combustible = tk.StringVar()
        self.var_buscar = tk.StringVar()

        self.build_ui()
        self.cargar_vehiculos()
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
        form = ttk.LabelFrame(self.frame, text="Datos Vehículo", padding=9)
        form.pack(side='left', fill='y', padx=(0,9))

        ttk.Label(form, text="Matrícula:").grid(row=0, column=0, sticky='w')
        self.entry_matricula = ttk.Entry(form, textvariable=self.var_matricula)
        self.entry_matricula.grid(row=0, column=1, pady=2)

        self.entry_cliente_id = ttk.Entry(form, textvariable=self.var_cliente_id, state='readonly')
        self.entry_cliente_id.place(x=282,y=24, width=22)

        ttk.Label(form, text="Cliente:").grid(row=1, column=0, sticky='w')
        self.combo_cliente = ttk.Combobox(form, textvariable=self.var_cliente_nombre, state='readonly')
        self.combo_cliente.grid(row=1, column=1, pady=2)
        self.combo_cliente.bind('<<ComboboxSelected>>', self.on_cliente_selected)  # Nuevo evento
        self.cargar_clientes()

        ttk.Label(form, text="Marca:").grid(row=2, column=0, sticky='w')
        self.entry_marca = ttk.Entry(form, textvariable=self.var_marca)
        self.entry_marca.grid(row=2, column=1, pady=2)

        ttk.Label(form, text="Modelo:").grid(row=3, column=0, sticky='w')
        self.entry_modelo = ttk.Entry(form, textvariable=self.var_modelo)
        self.entry_modelo.grid(row=3, column=1, pady=2)

        ttk.Label(form, text="Año:").grid(row=4, column=0, sticky='w')
        self.entry_ano = ttk.Entry(form, textvariable=self.var_ano)
        self.entry_ano.grid(row=4, column=1, pady=2)

        ttk.Label(form, text="Color:").grid(row=5, column=0, sticky='w')
        self.entry_color = ttk.Entry(form, textvariable=self.var_color)
        self.entry_color.grid(row=5, column=1, pady=2)

        ttk.Label(form, text="Combustible:").grid(row=6, column=0, sticky='w')
        self.combo_combustible = ttk.Combobox(form, 
                                            values=['Gasolina', 'Diésel', 'Eléctrico', 'Híbrido', 'Gas'], 
                                            textvariable=self.var_combustible,
                                            state='readonly')
        self.combo_combustible.grid(row=6, column=1, pady=2)

        # Botones
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

        # Tabla
        right = ttk.Frame(self.frame)
        right.pack(side='left', fill='both', expand=True)

        # Campo de búsqueda
        search_frame = ttk.Frame(right, padding=(0, 0, 0, 10))
        search_frame.pack(fill='x')
        
        ttk.Label(search_frame, text="Buscar (Matrícula o Marca):").pack(side='left', padx=(0, 5))
        self.entry_buscar = ttk.Entry(search_frame, textvariable=self.var_buscar, width=30)
        self.entry_buscar.pack(side='left', padx=(0, 5))
        self.entry_buscar.bind('<Return>', lambda e: self.buscar())
        
        ttk.Button(search_frame, text="Buscar", command=self.buscar).pack(side='left', padx=(0, 5))
        ttk.Button(search_frame, text="Mostrar Todos", command=self.mostrar_todos).pack(side='left')

        cols = ("matricula", "cliente_id", "cliente_nombre", "marca", "modelo", "año", "color", "tipo_combustible")
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        
        # Configurar columnas
        self.tree.heading("matricula", text="Matrícula")
        self.tree.heading("cliente_id", text="ID")
        self.tree.heading("cliente_nombre", text="Cliente") 
        self.tree.heading("marca", text="Marca")
        self.tree.heading("modelo", text="Modelo")
        self.tree.heading("año", text="Año")
        self.tree.heading("color", text="Color")
        self.tree.heading("tipo_combustible", text="Combustible")
        
        self.tree.column("matricula", width=60, anchor="center")
        self.tree.column("cliente_id", width=40, anchor="center")
        self.tree.column("cliente_nombre", width=120) 
        self.tree.column("marca", width=80)
        self.tree.column("modelo", width=80)
        self.tree.column("año", width=60, anchor="center")
        self.tree.column("color", width=60)
        self.tree.column("tipo_combustible", width=90)
        
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def cargar_clientes(self):
        """Cargar clientes en el combobox y validar si hay clientes"""
        clientes = self.dbClientes.listar_clientes()
        
        if not clientes:
            self.combo_cliente['values'] = ["-- NO HAY CLIENTES --"]
            self.combo_cliente.set("-- NO HAY CLIENTES --")
            self.combo_cliente.config(state="disabled")
            self.var_cliente_id.set("")
            return False
        else:
            self.combo_cliente.config(state="readonly")
        
        self.lista_clientes = []
        nombres_clientes = []
        for c in clientes:
            nombre_completo = f"{c['nombre']} {c['apellido_paterno']} {c['apellido_materno']}"
            nombres_clientes.append(nombre_completo)
            self.lista_clientes.append({
                'id': c['cliente_id'],
                'nombre_completo': nombre_completo
            })
        
        self.combo_cliente['values'] = nombres_clientes
        return True

    def on_cliente_selected(self, event):
        """Cuando se selecciona un cliente del combobox, actualizar el ID"""
        nombre_seleccionado = self.var_cliente_nombre.get()
        
        # Buscar el ID del cliente seleccionado
        for cliente in self.lista_clientes:
            if cliente['nombre_completo'] == nombre_seleccionado:
                self.var_cliente_id.set(str(cliente['id']))
                break

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
            if rol == 'auxiliar':
                self.btn_editar.config(state="disabled")
                self.btn_actualizar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")

            if not self.cargar_clientes():
                self.btn_guardar.config(state="disabled")
                messagebox.showwarning("Validación", "No hay clientes registrados. Debe registrar al menos un cliente antes de agregar vehículos.")

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
        if rol == 'auxiliar':
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
            self.btn_buscar.config(state="normal")
        if rol == 'auxiliar':
                self.btn_editar.config(state="disabled")
                self.btn_actualizar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")

        # Aplicar estado a los campos editables
        for entry in (self.entry_matricula, self.entry_marca, self.entry_modelo, 
                      self.entry_ano, self.entry_color):
            entry.config(state=estado)
        
        self.combo_cliente.config(state="readonly" if estado == "normal" else "disabled")
        self.combo_combustible.config(state="readonly" if estado == "normal" else "disabled")

    def limpiar(self):
        self.var_matricula.set('')
        self.var_cliente_id.set('')
        self.var_cliente_nombre.set('')
        self.var_marca.set('')
        self.var_modelo.set('')
        self.var_ano.set('')
        self.var_color.set('')
        self.var_combustible.set('')

    def nuevo(self):
        self.limpiar()
        self.set_estado("nuevo")

    def obtener_cliente_id_por_nombre(self, nombre_completo):
        """Obtener el cliente_id a partir del nombre completo mostrado en el combobox"""
        clientes = self.dbClientes.listar_clientes()
        for c in clientes:
            nombre_completo_cliente = f"{c['nombre']} {c['apellido_paterno']} {c['apellido_materno']}"
            if nombre_completo_cliente == nombre_completo:
                return c['cliente_id']
        return None

    def guardar(self):
        """Guardar NUEVO vehículo"""
        if not self.lista_clientes:
            messagebox.showerror("Error", "No hay clientes registrados. Registre al menos un cliente primero.")
            return
            
        matricula = self.var_matricula.get().strip()
        cliente_id = self.var_cliente_id.get().strip()
        cliente_nombre = self.var_cliente_nombre.get().strip()
        marca = self.var_marca.get().strip()
        modelo = self.var_modelo.get().strip()
        ano = self.var_ano.get().strip()
        color = self.var_color.get().strip()
        combustible = self.var_combustible.get().strip()

        if not all([matricula, cliente_id, cliente_nombre, marca, modelo, ano, color, combustible]):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return
        
        # Validar que la matrícula no exista
        vehiculo_existente = self.dbVehiculos.buscar_vehiculo_por_matricula(matricula)
        if vehiculo_existente:
            messagebox.showerror("Error", f"Ya existe un vehículo con la matrícula: {matricula}")
            return
        
        # Validar que el año sea numérico
        if not ano.isdigit():
            messagebox.showerror("Error", "El año debe ser un número")
            return
        
        # Obtener el ID del cliente
        cliente_id = self.obtener_cliente_id_por_nombre(cliente_nombre)
        if not cliente_id:
            messagebox.showerror("Error", "Cliente no válido")
            return
        
        ok, msg = self.dbVehiculos.crear_vehiculo(matricula, cliente_id, marca, modelo, int(ano), color, combustible)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_vehiculos()
            self.limpiar()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar(self):
        """Activar modo edición para vehículo existente"""
        if not self.var_matricula.get():
            messagebox.showwarning("Validación", "Seleccione un vehículo primero")
            return
        self.set_estado("editar")

    def actualizar(self):
        """Actualizar vehículo existente"""
        if not self.var_matricula.get():
            messagebox.showwarning("Validación", "Seleccione un vehículo primero")
            return
        
        matricula_original = self.var_matricula.get().strip()
        nueva_matricula = self.var_matricula.get().strip()
        cliente_nombre = self.var_cliente.get().strip()
        marca = self.var_marca.get().strip()
        modelo = self.var_modelo.get().strip()
        ano = self.var_ano.get().strip()
        color = self.var_color.get().strip()
        combustible = self.var_combustible.get().strip()

        if not all([nueva_matricula, cliente_nombre, marca, modelo, ano, color, combustible]):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return
        
        # Validar que el año sea numérico
        if not ano.isdigit():
            messagebox.showerror("Error", "El año debe ser un número")
            return
        
        # Verificar si la nueva matrícula ya existe en otro vehículo
        if nueva_matricula != matricula_original:
            vehiculo_existente = self.dbVehiculos.buscar_vehiculo_por_matricula(nueva_matricula)
            if vehiculo_existente:
                messagebox.showerror("Error", f"Ya existe otro vehículo con la matrícula: {nueva_matricula}")
                return
        
        # Obtener el ID del cliente
        cliente_id = self.obtener_cliente_id_por_nombre(cliente_nombre)
        if not cliente_id:
            messagebox.showerror("Error", "Cliente no válido")
            return
        
        ok, msg = self.dbVehiculos.actualizar_vehiculo(
            matricula_original, nueva_matricula, cliente_id, marca, modelo, int(ano), color, combustible
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_vehiculos()
            self.limpiar()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.var_matricula.get():
            messagebox.showwarning("Validación", "Seleccione un vehículo primero")
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este vehículo?"):
            ok, msg = self.dbVehiculos.eliminar_vehiculo(self.var_matricula.get())
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_vehiculos()
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
        
        # Buscar por matrícula (exacta)
        vehiculo_por_matricula = self.dbVehiculos.buscar_vehiculo_por_matricula(criterio)
        if vehiculo_por_matricula:
            resultados = [vehiculo_por_matricula]
        
        # Si no se encontró por matrícula, buscar por marca
        if not resultados:
            resultados = self.dbVehiculos.buscar_vehiculo_por_marca(criterio)
        
        if not resultados:
            messagebox.showinfo("Buscar", "No se encontraron vehículos")
            return
        
        # Mostrar resultados en la tabla
        for vehiculo in resultados:
            self.tree.insert('', 'end', values=(
                vehiculo["matricula"],
                vehiculo.get("cliente_nombre", ""),
                vehiculo["marca"],
                vehiculo["modelo"],
                vehiculo["año"],
                vehiculo["color"],
                vehiculo["tipo_combustible"],
                vehiculo["creado_en"]
            ))
        
        # Si hay un solo resultado, llenar el formulario
        if len(resultados) == 1:
            v = resultados[0]
            self.var_matricula.set(v['matricula'])
            self.var_cliente.set(v.get('cliente_nombre', ''))
            self.var_marca.set(v.get('marca', ''))
            self.var_modelo.set(v.get('modelo', ''))
            self.var_ano.set(str(v.get('año', '')))
            self.var_color.set(v.get('color', ''))
            self.var_combustible.set(v.get('tipo_combustible', ''))
            self.set_estado("buscar")
            
            # Seleccionar en la tabla
            for item in self.tree.get_children():
                if self.tree.item(item, 'values')[0] == v['matricula']:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break

    def mostrar_todos(self):
        self.var_buscar.set('')
        self.cargar_vehiculos()
        self.limpiar()
        self.set_estado("inicio")

    def cargar_vehiculos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        vehiculos = self.dbVehiculos.listar_vehiculos()
        for v in vehiculos:
            self.tree.insert('', 'end', values=(
                v["matricula"],
                v["cliente_id"],
                v.get("cliente_nombre", ""),
                v["marca"],
                v["modelo"],
                v["año"],
                v["color"],
                v["tipo_combustible"],
                v["creado_en"]
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], 'values')
        self.var_matricula.set(values[0])
        self.var_cliente_id.set(values[1])  
        self.var_cliente_nombre.set(values[2])  
        self.var_marca.set(values[3])
        self.var_modelo.set(values[4])
        self.var_ano.set(values[5])
        self.var_color.set(values[6])
        self.var_combustible.set(values[7])
        self.set_estado("buscar")
