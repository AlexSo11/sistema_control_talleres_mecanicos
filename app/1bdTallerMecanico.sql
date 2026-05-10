-- crear_bd_tallerMecanico.sql
CREATE DATABASE IF NOT EXISTS dbtaller_mecanico;
USE dbtaller_mecanico;

-- Eliminar tablas si existen (en orden inverso por las claves foráneas)
DROP TABLE IF EXISTS reparacion_piezas;
DROP TABLE IF EXISTS reparaciones;
DROP TABLE IF EXISTS piezas;
DROP TABLE IF EXISTS vehiculos;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS usuarios;

-- Crear tablas
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(150),
    telefono VARCHAR(30),
    rol ENUM('admin', 'auxiliar', 'mecanico') DEFAULT 'auxiliar',  -- ENUM para validación
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE clientes (
    cliente_id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    rfc VARCHAR(13) NOT NULL UNIQUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE vehiculos (
    matricula VARCHAR(20) PRIMARY KEY,
    cliente_id INT NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    año INT NOT NULL,
    color VARCHAR(30),
    tipo_combustible ENUM('Gasolina', 'Diésel', 'Eléctrico', 'Híbrido', 'Gas'),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE piezas (
    pieza_id INT AUTO_INCREMENT PRIMARY KEY,
    numero_serie VARCHAR(100) UNIQUE NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    existencias INT NOT NULL DEFAULT 0,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE reparaciones (
    folio INT AUTO_INCREMENT PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL,
    usuario_id INT NOT NULL,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE,
    descripcion TEXT,
    estado ENUM('pendiente', 'en_proceso', 'completada') DEFAULT 'pendiente',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matricula) REFERENCES vehiculos(matricula) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE reparacion_piezas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    folio_reparacion INT NOT NULL,
    pieza_id INT NOT NULL,
    cantidad INT NOT NULL,
    FOREIGN KEY (folio_reparacion) REFERENCES reparaciones(folio) ON DELETE CASCADE,
    FOREIGN KEY (pieza_id) REFERENCES piezas(pieza_id) ON DELETE CASCADE
) ENGINE=InnoDB;
