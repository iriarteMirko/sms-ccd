from ..utils.resource_path import resource_path
from tkinter import messagebox
import sqlite3 as sql

def conexionSQLite():
    try:
        conexion = sql.connect(resource_path("src/database/rutas.db"))
        return conexion
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al conectar a la base de datos: " + str(ex))

def ejecutar_query(query, parametros=None):
    conexion = conexionSQLite()
    try:
        cursor = conexion.cursor()
        if parametros is None:
            cursor.execute(query)
        else:
            cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        return resultados
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al ejecutar la consulta: " + str(ex))
    finally:
        cursor.close()
        conexion.close

def get_rutas():
    try:
        query = "SELECT NOMBRE,RUTA FROM RUTAS"
        resultados = ejecutar_query(query)
        return resultados
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al obtener las rutas: " + str(ex))

def set_ruta(ruta, nombre):
    try:
        query = "UPDATE RUTAS SET RUTA = ? WHERE NOMBRE = ?"
        parametros = (ruta, nombre)
        ejecutar_query(query, parametros)
    except sql.Error as ex:
        messagebox.showerror("Error", "Error al actualizar la ruta: " + str(ex))