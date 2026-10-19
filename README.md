# Sistema de Gestión de Taller Mecánico

Aplicación de escritorio para digitalizar la operación de un taller
automotriz: clientes, vehículos, reparaciones, piezas e inventario, y
usuarios con roles.

Construida con Python, `tkinter`/`ttk` y MySQL (`mysql-connector-python`).

## Módulos

| Módulo | Descripción |
|---|---|
| `app/app.py` | Login, menú y pestañas según el rol. |
| `app/conexion.py` | Conexión a MySQL (`ConexionDB`). |
| `app/DB/` | Acceso a datos, una clase por entidad. |
| `app/UI/` | Interfaces gráficas, una por módulo. |
| `app/1bdTallerMecanico.sql` | Esquema de la base de datos. |

### Pestañas

- **Usuarios**: alta, edición, baja y cambio de contraseña (solo `admin`).
- **Clientes**: alta, edición y baja; cada cliente queda ligado al usuario
  que lo registró.
- **Vehículos**: alta, edición y baja por matrícula.
- **Reparaciones**: alta, edición y baja; descuenta y restaura existencias
  de piezas dentro de una transacción.
- **Piezas**: alta, edición y baja de piezas e inventario (solo `admin`).

## Roles

| Rol | Acceso |
|---|---|
| `admin` | Todos los módulos. |
| `auxiliar` | Clientes y vehículos. |
| `mecanico` | Reparaciones (sin editar, eliminar ni actualizar). |

## Requisitos

- Python 3.10 o superior.
- MySQL 8 (o MariaDB compatible).
- Dependencias de `requirements.txt`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crear la base de datos e importar el esquema:

```bash
mysql -u root -p < app/1bdTallerMecanico.sql
```

El script crea la base `dbtaller_mecanico`, que es la que usa la aplicación.
Si tu MySQL tiene contraseña, ajusta `conexion.py` o `DB_CONFIG` en
`app/app.py`.

## Ejecución

Los módulos se importan de forma absoluta (`from conexion import ...`,
`from DB...`), así que hay que ejecutar desde la carpeta `app/`:

```bash
cd app
python app.py
```

### Cuentas de ejemplo

La base no incluye usuarios. Desde la pantalla de login, el botón
**"Crear cuenta (demo)"** crea (si no existen):

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | admin |
| `auxiliar` | `auxiliar123` | auxiliar |
| `mecanico` | `mecanico123` | mecanico |

## Estructura

```
Sistema_Gestion_TallerMecanico/
├── README.md
├── requirements.txt
├── LICENSE
└── app/
    ├── app.py
    ├── conexion.py
    ├── 1bdTallerMecanico.sql
    ├── DB/
    │   ├── dbCliente.py
    │   ├── dbPiezas.py
    │   ├── dbReparaciones.py
    │   ├── dbUsuario.py
    │   └── dbVehiculos.py
    └── UI/
        ├── clientes.py
        ├── piezas.py
        ├── reparaciones.py
        ├── usuarios.py
        └── vehiculos.py
```

## Limitaciones conocidas

- Las contraseñas se guardan como SHA-256 **sin sal**. Para producción se
  recomienda `bcrypt` o `argon2`.
- Las credenciales de MySQL están vacías por defecto en `conexion.py` y en
  `DB_CONFIG` de `app.py`.
- El esquema usa `ON DELETE CASCADE`: borrar un cliente elimina sus vehículos
  y las reparaciones de esos vehículos; borrar un vehículo elimina sus
  reparaciones. `eliminar_usuario` bloquea el borrado si el usuario tiene
  clientes asignados para evitar la cadena completa.
- `actualizar_usuario` no modifica el `username`; la interfaz permite
  editarlo pero el cambio no se guarda.
- La validación de RFC solo comprueba que tenga al menos 13 caracteres; la
  columna admite 13.
- La columna `estado` de `reparaciones` existe en la base, pero la interfaz
  no la edita.
- No hay pruebas automatizadas; la verificación es manual con MySQL y GUI.

## Créditos

Desarrollo original: AlexWhite / AlexSo11.
