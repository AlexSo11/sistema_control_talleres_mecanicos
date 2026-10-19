"""Interfaz de gestión de reparaciones."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from DB.dbReparaciones import DBReparacion
from DB.dbPiezas import DBPieza
from DB.dbVehiculos import DBVehiculo
from conexion import ConexionDB

class ReparacionesUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        self.con = ConexionDB()
        self.dbReparaciones = DBReparacion(self.con)
        self.dbPiezas = DBPieza(self.con)
        self.dbVehiculos = DBVehiculo(self.con)

        # Variables principales
        self.var_folio = tk.StringVar()
        self.var_matricula = tk.StringVar()
        self.var_usuario = tk.StringVar()
        self.var_fecha_entrada = tk.StringVar()
        self.var_fecha_salida = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_buscar = tk.StringVar()

        # Variables para piezas
        self.var_pieza_id = tk.StringVar()
        self.var_pieza_nombre = tk.StringVar()
        self.var_pieza_cantidad = tk.StringVar()
        self.var_pieza_stock = tk.StringVar()

        # Lista temporal de piezas
        self.piezas_temporales = []
        
        # Estado de edición
        self.modo_edicion = False

        # Establecer usuario actual
        if self.usuario_actual:
            self.var_usuario.set(self.usuario_actual.get('username', ''))

        # Construir interfaz
        self.build_ui()
        
        # Cargar datos
        try:
            self.cargar_vehiculos()
            self.cargar_piezas()
            self.cargar_reparaciones()
        except Exception as e:
            print(f"Error al cargar datos: {e}")
        
        # Aplicar restricciones de rol
        self.aplicar_restricciones_rol()
        
        # Estado inicial
        self.set_estado("inicio")

    def build_ui(self):
        # Frame principal
        main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)

        # Frame izquierdo
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Frame derecho
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        # --- FORMULARIO IZQUIERDO ---
        # Datos de reparación
        form_reparacion = ttk.LabelFrame(left_frame, text="Datos Reparación", padding=10)
        form_reparacion.pack(fill='x', pady=(0,10))
        form_reparacion.columnconfigure(1, weight=1)

        ttk.Label(form_reparacion, text="Folio:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_folio = ttk.Entry(form_reparacion, textvariable=self.var_folio, state='readonly')
        self.entry_folio.grid(row=0, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_reparacion, text="Matrícula:").grid(row=1, column=0, sticky='w', pady=2)
        self.combo_matricula = ttk.Combobox(form_reparacion, textvariable=self.var_matricula, state='readonly')
        self.combo_matricula.grid(row=1, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_reparacion, text="Usuario:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_usuario = ttk.Entry(form_reparacion, textvariable=self.var_usuario, state='readonly')
        self.entry_usuario.grid(row=2, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_reparacion, text="Fecha Entrada:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_fecha_entrada = ttk.Entry(form_reparacion, textvariable=self.var_fecha_entrada)
        self.entry_fecha_entrada.grid(row=3, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_reparacion, text="Fecha Salida:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_fecha_salida = ttk.Entry(form_reparacion, textvariable=self.var_fecha_salida)
        self.entry_fecha_salida.grid(row=4, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_reparacion, text="Descripción:").grid(row=5, column=0, sticky='nw', pady=2)
        self.text_descripcion = tk.Text(form_reparacion, width=25, height=3)
        self.text_descripcion.grid(row=5, column=1, pady=2, sticky='ew', padx=(5,0))

        # Gestión de piezas
        form_piezas = ttk.LabelFrame(left_frame, text="Gestión de Piezas", padding=10)
        form_piezas.pack(fill='x', pady=(0,10))
        form_piezas.columnconfigure(1, weight=1)

        ttk.Label(form_piezas, text="Pieza:").grid(row=0, column=0, sticky='w', pady=2)
        self.combo_pieza = ttk.Combobox(form_piezas, textvariable=self.var_pieza_nombre, state='readonly')
        self.combo_pieza.grid(row=0, column=1, pady=2, sticky='ew', padx=(5,0))
        self.combo_pieza.bind('<<ComboboxSelected>>', self.on_pieza_selected)

        ttk.Label(form_piezas, text="ID Pieza:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_pieza_id = ttk.Entry(form_piezas, textvariable=self.var_pieza_id, state='readonly')
        self.entry_pieza_id.grid(row=1, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_piezas, text="Stock:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_pieza_stock = ttk.Entry(form_piezas, textvariable=self.var_pieza_stock, state='readonly')
        self.entry_pieza_stock.grid(row=2, column=1, pady=2, sticky='ew', padx=(5,0))

        ttk.Label(form_piezas, text="Cantidad:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_pieza_cantidad = ttk.Entry(form_piezas, textvariable=self.var_pieza_cantidad)
        self.entry_pieza_cantidad.grid(row=3, column=1, pady=2, sticky='ew', padx=(5,0))

        # Botones de piezas
        piezas_btns = ttk.Frame(form_piezas)
        piezas_btns.grid(row=4, column=0, columnspan=2, pady=(10,5))
        ttk.Button(piezas_btns, text="Agregar Pieza", command=self.agregar_pieza).pack(side='left', padx=2)
        ttk.Button(piezas_btns, text="Quitar Pieza", command=self.quitar_pieza).pack(side='left', padx=2)

        # Lista de piezas
        ttk.Label(form_piezas, text="Piezas en reparación:").grid(row=5, column=0, sticky='w', pady=(10,0), columnspan=2)
        frame_lista_piezas = ttk.Frame(form_piezas)
        frame_lista_piezas.grid(row=6, column=0, columnspan=2, pady=5, sticky='ew')
        frame_lista_piezas.columnconfigure(0, weight=1)
        
        self.lista_piezas = tk.Listbox(frame_lista_piezas, height=4)
        self.lista_piezas.grid(row=0, column=0, sticky='nsew')
        
        scrollbar_piezas = ttk.Scrollbar(frame_lista_piezas, orient="vertical", command=self.lista_piezas.yview)
        scrollbar_piezas.grid(row=0, column=1, sticky='ns')
        self.lista_piezas.configure(yscrollcommand=scrollbar_piezas.set)

        # Botones de acciones
        btns_frame = ttk.LabelFrame(left_frame, text="Acciones", padding=10)
        btns_frame.pack(fill='x')

        btns_principal = ttk.Frame(btns_frame)
        btns_principal.pack()

        self.btn_nuevo = ttk.Button(btns_principal, text="Nuevo", command=self.nuevo, width=10)
        self.btn_nuevo.grid(row=0, column=0, padx=2, pady=2)

        self.btn_guardar = ttk.Button(btns_principal, text="Guardar", command=self.guardar, width=10)
        self.btn_guardar.grid(row=0, column=1, padx=2, pady=2)

        self.btn_cancelar = ttk.Button(btns_principal, text="Cancelar", command=self.cancelar, width=10)
        self.btn_cancelar.grid(row=0, column=2, padx=2, pady=2)

        self.btn_editar = ttk.Button(btns_principal, text="Editar", command=self.editar, width=10)
        self.btn_editar.grid(row=1, column=0, padx=2, pady=2)

        self.btn_eliminar = ttk.Button(btns_principal, text="Eliminar", command=self.eliminar, width=10)
        self.btn_eliminar.grid(row=1, column=1, padx=2, pady=2)
        
        self.btn_actualizar = ttk.Button(btns_principal, text="Actualizar", command=self.actualizar, width=10)
        self.btn_actualizar.grid(row=1, column=2, padx=2, pady=2)

        # --- PANEL DERECHO ---
        # Búsqueda
        search_frame = ttk.Frame(right_frame, padding=(0,0,0,10))
        search_frame.pack(fill='x')

        ttk.Label(search_frame, text="Buscar por Folio:").pack(side='left', padx=(0,5))
        self.entry_buscar = ttk.Entry(search_frame, textvariable=self.var_buscar, width=20)
        self.entry_buscar.pack(side='left', padx=(0,5))
        self.entry_buscar.bind('<Return>', lambda e: self.buscar())

        ttk.Button(search_frame, text="Buscar", command=self.buscar).pack(side='left', padx=(0,5))
        ttk.Button(search_frame, text="Mostrar Todos", command=self.mostrar_todos).pack(side='left')

        # Treeview
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        cols = ("folio", "matricula", "marca", "modelo", "fecha_entrada", "fecha_salida", "usuario", "total_piezas")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

        self.tree.heading("folio", text="Folio")
        self.tree.heading("matricula", text="Matrícula")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("modelo", text="Modelo")
        self.tree.heading("fecha_entrada", text="Fecha Entrada")
        self.tree.heading("fecha_salida", text="Fecha Salida")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("total_piezas", text="Piezas")

        self.tree.column("folio", width=60, anchor="center")
        self.tree.column("matricula", width=100, anchor="center")
        self.tree.column("marca", width=80)
        self.tree.column("modelo", width=80)
        self.tree.column("fecha_entrada", width=100)
        self.tree.column("fecha_salida", width=100)
        self.tree.column("usuario", width=100)
        self.tree.column("total_piezas", width=60, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def aplicar_restricciones_rol(self):
        """Aplicar restricciones según el rol del usuario"""
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        
        # Para mecanico, aplicar restricciones en botones
        if rol == 'mecanico':
            # Mecánico solo puede: Nuevo, Guardar, Buscar
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")

    def cargar_vehiculos(self):
        vehiculos = self.dbVehiculos.listar_vehiculos()
        matriculas = [v['matricula'] for v in vehiculos]
        self.combo_matricula['values'] = matriculas

    def cargar_piezas(self):
        piezas = self.dbPiezas.listar_piezas()
        self.lista_piezas_completa = piezas
        nombres_piezas = [f"{p['descripcion']} (Stock: {p['existencias']})" for p in piezas]
        self.combo_pieza['values'] = nombres_piezas

    def on_pieza_selected(self, event):
        nombre_seleccionado = self.var_pieza_nombre.get()
        for pieza in self.lista_piezas_completa:
            nombre_completo = f"{pieza['descripcion']} (Stock: {pieza['existencias']})"
            if nombre_completo == nombre_seleccionado:
                self.var_pieza_id.set(str(pieza['pieza_id']))
                self.var_pieza_stock.set(str(pieza['existencias']))
                break

    def agregar_pieza(self):
        if not self.var_pieza_id.get() or not self.var_pieza_cantidad.get():
            messagebox.showwarning("Validación", "Seleccione una pieza y especifique la cantidad")
            return

        try:
            pieza_id = int(self.var_pieza_id.get())
            cantidad = int(self.var_pieza_cantidad.get())
            stock = int(self.var_pieza_stock.get())

            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return

            # En modo edición, considerar las piezas ya asignadas
            stock_disponible = stock
            if self.modo_edicion:
                # Buscar si esta pieza ya está en la reparación
                pieza_existente = next((p for p in self.piezas_temporales if p['pieza_id'] == pieza_id), None)
                if pieza_existente:
                    # El stock disponible es el stock actual + la cantidad que ya tenía asignada
                    stock_disponible = stock + pieza_existente['cantidad']
                else:
                    stock_disponible = stock

            if cantidad > stock_disponible:
                messagebox.showerror("Error", f"No hay suficiente stock disponible. Stock: {stock_disponible}")
                return

            # Si la pieza ya existe en la lista, actualizar cantidad
            for item in self.piezas_temporales:
                if item['pieza_id'] == pieza_id:
                    item['cantidad'] = cantidad
                    self.actualizar_lista_piezas()
                    
                    # Limpiar campos de pieza
                    self.var_pieza_nombre.set('')
                    self.var_pieza_id.set('')
                    self.var_pieza_stock.set('')
                    self.var_pieza_cantidad.set('')
                    return

            # Buscar información de la pieza
            pieza_info = None
            for pieza in self.lista_piezas_completa:
                if pieza['pieza_id'] == pieza_id:
                    pieza_info = pieza
                    break

            if pieza_info:
                self.piezas_temporales.append({
                    'pieza_id': pieza_id,
                    'descripcion': pieza_info['descripcion'],
                    'cantidad': cantidad,
                    'stock_actual': stock
                })

                # Actualizar lista visual
                self.actualizar_lista_piezas()

                # Limpiar campos de pieza
                self.var_pieza_nombre.set('')
                self.var_pieza_id.set('')
                self.var_pieza_stock.set('')
                self.var_pieza_cantidad.set('')

        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")

    def quitar_pieza(self):
        seleccion = self.lista_piezas.curselection()
        if not seleccion:
            messagebox.showwarning("Validación", "Seleccione una pieza de la lista para quitar")
            return

        index = seleccion[0]
        if 0 <= index < len(self.piezas_temporales):
            self.piezas_temporales.pop(index)
            self.actualizar_lista_piezas()

    def actualizar_lista_piezas(self):
        self.lista_piezas.delete(0, tk.END)
        for pieza in self.piezas_temporales:
            self.lista_piezas.insert(tk.END, f"{pieza['descripcion']} - Cant: {pieza['cantidad']}")

    def set_estado(self, modo):
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        
        if rol == 'auxiliar':
            return  # Auxiliar no tiene acceso

        self.modo_edicion = (modo == "editar")

        if modo == "nuevo":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="normal")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")

            if rol == 'mecanico':
                self.btn_editar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")
                self.btn_actualizar.config(state="disabled")

            # Validar que existan vehículos y piezas
            vehiculos = self.dbVehiculos.listar_vehiculos()
            piezas = self.dbPiezas.listar_piezas()
            
            if not vehiculos:
                messagebox.showwarning("Validación", "No hay vehículos registrados. Debe registrar al menos un vehículo antes de crear reparaciones.")
                self.btn_guardar.config(state="disabled")
            
            if not piezas:
                messagebox.showwarning("Validación", "No hay piezas registradas. Debe registrar al menos una pieza antes de crear reparaciones.")
                self.btn_guardar.config(state="disabled")

        elif modo == "editar":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_actualizar.config(state="normal")
            if rol == 'mecanico':
                self.btn_editar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")
                self.btn_actualizar.config(state="disabled")

        elif modo in ("salvar", "cancelar", "remover", "inicio"):
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="disabled")
            self.btn_editar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            if rol == 'mecanico':
                self.btn_editar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")
                self.btn_actualizar.config(state="disabled")

        elif modo == "buscar":
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="normal")
            self.btn_eliminar.config(state="normal")
            self.btn_actualizar.config(state="disabled")
            if rol == 'mecanico':
                self.btn_editar.config(state="disabled")
                self.btn_eliminar.config(state="disabled")
                self.btn_actualizar.config(state="disabled")

        if rol != 'auxiliar':
            self.combo_matricula.config(state="readonly" if estado == "normal" else "disabled")
            self.entry_fecha_entrada.config(state=estado)
            self.entry_fecha_salida.config(state=estado)
            self.text_descripcion.config(state=estado)
            
            # Campos de piezas
            self.combo_pieza.config(state="readonly" if estado == "normal" else "disabled")
            self.entry_pieza_cantidad.config(state=estado)

    def limpiar(self):
        self.var_folio.set('')
        self.var_matricula.set('')
        self.var_fecha_entrada.set(datetime.now().strftime("%Y-%m-%d"))
        self.var_fecha_salida.set('')
        self.text_descripcion.delete(1.0, tk.END)
        self.piezas_temporales = []
        self.actualizar_lista_piezas()
        self.modo_edicion = False
        
        # Limpiar campos de pieza
        self.var_pieza_nombre.set('')
        self.var_pieza_id.set('')
        self.var_pieza_stock.set('')
        self.var_pieza_cantidad.set('')

    def nuevo(self):
        self.limpiar()
        self.set_estado("nuevo")

    def guardar(self):
        # Validaciones básicas
        if not all([self.var_matricula.get(), self.var_fecha_entrada.get()]):
            messagebox.showwarning("Validación", "Matrícula y fecha de entrada son obligatorios")
            return

        if not self.piezas_temporales:
            messagebox.showwarning("Validación", "Debe agregar al menos una pieza a la reparación")
            return

        # Validar que todas las piezas tengan cantidad > 0
        for pieza in self.piezas_temporales:
            if pieza['cantidad'] <= 0:
                messagebox.showerror("Error", f"La cantidad para {pieza['descripcion']} debe ser mayor a 0")
                return

        # Validar fechas
        try:
            fecha_entrada = datetime.strptime(self.var_fecha_entrada.get(), "%Y-%m-%d")
            fecha_salida = None
            if self.var_fecha_salida.get():
                fecha_salida = datetime.strptime(self.var_fecha_salida.get(), "%Y-%m-%d")
                if fecha_salida < fecha_entrada:
                    messagebox.showerror("Error", "La fecha de salida no puede ser anterior a la fecha de entrada")
                    return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        # Preparar datos
        descripcion = self.text_descripcion.get(1.0, tk.END).strip()
        usuario_id = self.usuario_actual.get('id') if self.usuario_actual else None

        if not usuario_id:
            messagebox.showerror("Error", "No se pudo identificar al usuario actual")
            return

        # Crear reparación
        exito, mensaje = self.dbReparaciones.crear_reparacion(
            self.var_matricula.get(),
            usuario_id,
            self.var_fecha_entrada.get(),
            self.var_fecha_salida.get() or None,
            descripcion,
            self.piezas_temporales
        )

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar()
            self.set_estado("inicio")
            self.cargar_reparaciones()
        else:
            messagebox.showerror("Error", mensaje)

    def actualizar(self):
        """Actualizar una reparación existente"""
        if not self.var_folio.get():
            messagebox.showwarning("Validación", "No hay reparación seleccionada para actualizar")
            return

        # Validaciones básicas
        if not all([self.var_matricula.get(), self.var_fecha_entrada.get()]):
            messagebox.showwarning("Validación", "Matrícula y fecha de entrada son obligatorios")
            return

        if not self.piezas_temporales:
            messagebox.showwarning("Validación", "Debe agregar al menos una pieza a la reparación")
            return

        # Validar que todas las piezas tengan cantidad > 0
        for pieza in self.piezas_temporales:
            if pieza['cantidad'] <= 0:
                messagebox.showerror("Error", f"La cantidad para {pieza['descripcion']} debe ser mayor a 0")
                return

        # Validar fechas
        try:
            fecha_entrada = datetime.strptime(self.var_fecha_entrada.get(), "%Y-%m-%d")
            fecha_salida = None
            if self.var_fecha_salida.get():
                fecha_salida = datetime.strptime(self.var_fecha_salida.get(), "%Y-%m-%d")
                if fecha_salida < fecha_entrada:
                    messagebox.showerror("Error", "La fecha de salida no puede ser anterior a la fecha de entrada")
                    return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        # Preparar datos
        descripcion = self.text_descripcion.get(1.0, tk.END).strip()

        # Confirmar actualización
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea actualizar esta reparación? Se ajustarán los inventarios de piezas."):
            return

        # Actualizar reparación
        exito, mensaje = self.dbReparaciones.actualizar_reparacion(
            int(self.var_folio.get()),
            self.var_matricula.get(),
            self.var_fecha_entrada.get(),
            self.var_fecha_salida.get() or None,
            descripcion,
            self.piezas_temporales
        )

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar()
            self.set_estado("inicio")
            self.cargar_reparaciones()
        else:
            messagebox.showerror("Error", mensaje)

    def cancelar(self):
        self.limpiar()
        self.set_estado("inicio")

    def editar(self):
        if not self.var_folio.get():
            messagebox.showwarning("Validación", "Seleccione una reparación para editar")
            return

        # Cargar las piezas actuales de la reparación en la lista temporal
        folio = int(self.var_folio.get())
        piezas_actuales = self.dbReparaciones.obtener_piezas_reparacion(folio)
        
        self.piezas_temporales = []
        for pieza in piezas_actuales:
            self.piezas_temporales.append({
                'pieza_id': pieza['pieza_id'],
                'descripcion': pieza['descripcion'],
                'cantidad': pieza['cantidad'],
                'stock_actual': pieza['stock_actual']
            })

        self.actualizar_lista_piezas()
        self.set_estado("editar")

    def eliminar(self):
        if not self.var_folio.get():
            messagebox.showwarning("Validación", "Seleccione una reparación para eliminar")
            return

        folio = self.var_folio.get()
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar la reparación {folio}?"):
            exito, mensaje = self.dbReparaciones.eliminar_reparacion(int(folio))
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar()
                self.cargar_reparaciones()
            else:
                messagebox.showerror("Error", mensaje)

    def cargar_reparaciones(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        reparaciones = self.dbReparaciones.listar_reparaciones()
        for rep in reparaciones:
            self.tree.insert("", tk.END, values=(
                rep['folio'],
                rep['matricula'],
                rep.get('marca', ''),
                rep.get('modelo', ''),
                rep['fecha_entrada'],
                rep['fecha_salida'] or '',
                rep.get('usuario_nombre', ''),
                rep.get('total_piezas', 0)
            ))

    def on_tree_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        
        if valores:
            self.var_folio.set(valores[0])
            self.var_matricula.set(valores[1])
            self.var_fecha_entrada.set(valores[4])
            self.var_fecha_salida.set(valores[5])
            self.var_usuario.set(valores[6])
            
            # Cargar descripción completa
            reparacion = self.dbReparaciones.buscar_reparacion_por_folio(int(valores[0]))
            if reparacion:
                self.text_descripcion.delete(1.0, tk.END)
                self.text_descripcion.insert(1.0, reparacion.get('descripcion', ''))
            
            # Limpiar lista temporal de piezas
            self.piezas_temporales = []
            self.actualizar_lista_piezas()
            
            self.set_estado("buscar")

    def buscar(self):
        texto = self.var_buscar.get().strip()
        if not texto:
            self.mostrar_todos()
            return

        try:
            folio = int(texto)
            reparacion = self.dbReparaciones.buscar_reparacion_por_folio(folio)
            if reparacion:
                # Limpiar treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Mostrar solo la reparación encontrada
                self.tree.insert("", tk.END, values=(
                    reparacion['folio'],
                    reparacion['matricula'],
                    reparacion.get('marca', ''),
                    reparacion.get('modelo', ''),
                    reparacion['fecha_entrada'],
                    reparacion['fecha_salida'] or '',
                    reparacion.get('usuario_nombre', ''),
                    len(self.dbReparaciones.obtener_piezas_reparacion(folio))
                ))
            else:
                messagebox.showinfo("Búsqueda", "No se encontró ninguna reparación con ese folio")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número de folio válido")

    def mostrar_todos(self):
        self.var_buscar.set('')
        self.cargar_reparaciones()
