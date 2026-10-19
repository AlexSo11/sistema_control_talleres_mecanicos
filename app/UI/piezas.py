"""Interfaz de gestión de piezas e inventario."""

import tkinter as tk
from tkinter import ttk, messagebox
from DB.dbPiezas import DBPieza
from conexion import ConexionDB

class PiezasUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        self.con = ConexionDB()
        self.dbPiezas = DBPieza(self.con)

        # Variables
        self.var_id = tk.StringVar()
        self.var_numero_serie = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_precio = tk.StringVar()
        self.var_existencias = tk.StringVar()
        self.var_buscar = tk.StringVar()

        self.build_ui()
        self.cargar_piezas()
        self.aplicar_restricciones_rol()
        self.set_estado("inicio")

    def aplicar_restricciones_rol(self):
        """Aplicar restricciones según el rol del usuario"""
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        
        if rol != 'admin':
            # Solo admin puede acceder a piezas
            for widget in self.frame.winfo_children():
                widget.destroy()
            ttk.Label(self.frame, text="Acceso denegado: Solo administradores pueden gestionar piezas", 
                     font=("Segoe UI", 12), foreground="red").pack(expand=True)
            return

    def build_ui(self):
        # Frame principal dividido
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True)

        # Formulario izquierdo
        form = ttk.LabelFrame(main_frame, text="Datos Pieza", padding=10)
        form.pack(side='left', fill='y', padx=(0,10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, pady=2, sticky='ew')

        ttk.Label(form, text="Número de Serie:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_numero_serie = ttk.Entry(form, textvariable=self.var_numero_serie, width=30)
        self.entry_numero_serie.grid(row=1, column=1, pady=2, sticky='ew')

        ttk.Label(form, text="Descripción:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_descripcion = ttk.Entry(form, textvariable=self.var_descripcion, width=30)
        self.entry_descripcion.grid(row=2, column=1, pady=2, sticky='ew')

        ttk.Label(form, text="Precio:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_precio = ttk.Entry(form, textvariable=self.var_precio, width=30)
        self.entry_precio.grid(row=3, column=1, pady=2, sticky='ew')

        ttk.Label(form, text="Existencias:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_existencias = ttk.Entry(form, textvariable=self.var_existencias, width=30)
        self.entry_existencias.grid(row=4, column=1, pady=2, sticky='ew')

        # Botones
        btns = ttk.Frame(form)
        btns.grid(row=5, column=0, columnspan=2, pady=(15,5))

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo)
        self.btn_nuevo.grid(row=0, column=0, padx=3)

        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar)
        self.btn_guardar.grid(row=0, column=1, padx=3)

        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar)
        self.btn_editar.grid(row=0, column=2, padx=3)

        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar)
        self.btn_actualizar.grid(row=0, column=3, padx=3)

        self.btn_eliminar = ttk.Button(btns, text="Eliminar", command=self.eliminar)
        self.btn_eliminar.grid(row=1, column=0, padx=3, pady=(5,0))

        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar)
        self.btn_cancelar.grid(row=1, column=1, padx=3, pady=(5,0))

        # Frame derecho (lista y búsqueda)
        right = ttk.Frame(main_frame)
        right.pack(side='left', fill='both', expand=True)

        # Búsqueda
        search_frame = ttk.Frame(right, padding=(0,0,0,10))
        search_frame.pack(fill='x')

        ttk.Label(search_frame, text="Buscar (ID o Descripción):").pack(side='left', padx=(0,5))
        self.entry_buscar = ttk.Entry(search_frame, textvariable=self.var_buscar, width=25)
        self.entry_buscar.pack(side='left', padx=(0,5))
        self.entry_buscar.bind('<Return>', lambda e: self.buscar())

        ttk.Button(search_frame, text="Buscar", command=self.buscar).pack(side='left', padx=(0,5))
        ttk.Button(search_frame, text="Mostrar Todos", command=self.mostrar_todos).pack(side='left')

        # Treeview
        cols = ("pieza_id", "numero_serie", "descripcion", "precio", "existencias", "creado_en")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)

        self.tree.heading("pieza_id", text="ID")
        self.tree.heading("numero_serie", text="Número Serie")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("existencias", text="Existencias")
        self.tree.heading("creado_en", text="Creado En")

        self.tree.column("pieza_id", width=50, anchor="center")
        self.tree.column("numero_serie", width=120)
        self.tree.column("descripcion", width=200)
        self.tree.column("precio", width=80, anchor="e")
        self.tree.column("existencias", width=80, anchor="center")
        self.tree.column("creado_en", width=120)

        scrollbar = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        rol = self.usuario_actual.get('rol', 'auxiliar') if self.usuario_actual else 'auxiliar'
        if rol != 'admin':
            return  # Solo admin tiene acceso
        
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

        for entry in (self.entry_numero_serie, self.entry_descripcion, self.entry_precio, self.entry_existencias):
            entry.config(state=estado)

    def limpiar(self):
        self.var_id.set('')
        self.var_numero_serie.set('')
        self.var_descripcion.set('')
        self.var_precio.set('')
        self.var_existencias.set('')

    def nuevo(self):
        self.limpiar()
        self.set_estado("nuevo")

    def guardar(self):
        numero_serie = self.var_numero_serie.get().strip()
        descripcion = self.var_descripcion.get().strip()
        precio = self.var_precio.get().strip()
        existencias = self.var_existencias.get().strip()

        if not all([numero_serie, descripcion, precio, existencias]):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return

        try:
            precio_float = float(precio)
            existencias_int = int(existencias)
            
            if existencias_int < 0:
                messagebox.showerror("Error", "No se puede registrar una pieza con stock negativo")
                return
                
            if precio_float < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo")
                return

        except ValueError:
            messagebox.showerror("Error", "Precio y existencias deben ser números válidos")
            return

        ok, msg = self.dbPiezas.crear_pieza(numero_serie, descripcion, precio_float, existencias_int)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_piezas()
            self.limpiar()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Seleccione una pieza primero")
            return
        self.set_estado("editar")

    def actualizar(self):
        if not self.var_id.get():
            return

        numero_serie = self.var_numero_serie.get().strip()
        descripcion = self.var_descripcion.get().strip()
        precio = self.var_precio.get().strip()
        existencias = self.var_existencias.get().strip()

        if not all([numero_serie, descripcion, precio, existencias]):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return

        try:
            precio_float = float(precio)
            existencias_int = int(existencias)
            
            if existencias_int < 0:
                messagebox.showerror("Error", "No se puede registrar una pieza con stock negativo")
                return
                
            if precio_float < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo")
                return

        except ValueError:
            messagebox.showerror("Error", "Precio y existencias deben ser números válidos")
            return

        ok, msg = self.dbPiezas.actualizar_pieza(
            int(self.var_id.get()), numero_serie, descripcion, precio_float, existencias_int
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_piezas()
            self.limpiar()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Seleccione una pieza primero")
            return
        
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar esta pieza?"):
            ok, msg = self.dbPiezas.eliminar_pieza(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_piezas()
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
            pieza = self.dbPiezas.buscar_pieza_por_id(int(criterio))
            if pieza:
                resultados = [pieza]
        
        if not resultados:
            resultados = self.dbPiezas.buscar_pieza_por_nombre(criterio)
        
        if not resultados:
            messagebox.showinfo("Buscar", "No se encontraron piezas")
            return
        
        for pieza in resultados:
            self.tree.insert('', 'end', values=(
                pieza["pieza_id"],
                pieza["numero_serie"],
                pieza["descripcion"],
                f"${pieza['precio']:.2f}",
                pieza["existencias"],
                pieza["creado_en"]
            ))

        if len(resultados) == 1:
            p = resultados[0]
            self.var_id.set(p['pieza_id'])
            self.var_numero_serie.set(p['numero_serie'])
            self.var_descripcion.set(p['descripcion'])
            self.var_precio.set(str(p['precio']))
            self.var_existencias.set(str(p['existencias']))
            self.set_estado("buscar")

    def mostrar_todos(self):
        self.var_buscar.set('')
        self.cargar_piezas()
        self.limpiar()
        self.set_estado("inicio")

    def cargar_piezas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        piezas = self.dbPiezas.listar_piezas()
        for p in piezas:
            self.tree.insert('', 'end', values=(
                p["pieza_id"],
                p["numero_serie"],
                p["descripcion"],
                f"${p['precio']:.2f}",
                p["existencias"],
                p["creado_en"]
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], 'values')
        self.var_id.set(values[0])
        self.var_numero_serie.set(values[1])
        self.var_descripcion.set(values[2])
        # Remover el símbolo $ del precio para edición
        precio_sin_dolar = values[3].replace('$', '') if '$' in values[3] else values[3]
        self.var_precio.set(precio_sin_dolar)
        self.var_existencias.set(values[4])
        self.set_estado("buscar")
