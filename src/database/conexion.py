from ..utils.resource_path import resource_path
from tkinter import messagebox
import sqlite3 as sql

def get_conexion() -> sql.Connection:
    try:
        conexion: sql.Connection = sql.connect(resource_path("src/database/rutas.db"))
        return conexion
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al conectar a la base de datos: " + str(ex))

def get_rutas() -> list[tuple[str, str]]:
    try:
        query: str = "SELECT NOMBRE,RUTA FROM RUTAS"
        conexion: sql.Connection = get_conexion()
        cursor: sql.Cursor = conexion.cursor()
        cursor.execute(query)
        resultados: list[tuple[str, str]] = cursor.fetchall()
        return resultados
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al obtener las rutas: " + str(ex))
    finally:
        cursor.close()
        conexion.close()

def set_ruta(ruta: str, nombre: str) -> None:
    try:
        query: str = """UPDATE RUTAS SET RUTA = '""" + ruta + """' WHERE NOMBRE = '""" + nombre + """'"""
        conexion: sql.Connection = get_conexion()
        cursor: sql.Cursor = conexion.cursor()
        cursor.execute(query)
        conexion.commit()
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al actualizar la ruta: " + str(ex))
    finally:
        cursor.close()
        conexion.close()