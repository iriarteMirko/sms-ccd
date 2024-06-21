from ..database.conexion import get_rutas, set_ruta
from customtkinter import filedialog
from tkinter import messagebox


def verificar_rutas() -> list[str] | None:
    try:
        rutas: list[tuple[str, str]] = get_rutas()
        rutas_general: list[str] = []
        rutas_vacias: list[str] = []
        for ruta in rutas:
            if ruta[1] == None or ruta[1] == "":
                rutas_vacias.append(ruta[0])
                if ruta[1] == None:
                    ruta[1] = ""
            rutas_general.append(ruta[1])
        if len(rutas_vacias) != 0:
            messagebox.showwarning(
                "ADVERTENCIA", 
                "Las siguientes rutas no han sido seleccionadas:" 
                + "\n("+", ".join(rutas_vacias)+")\n"
                + "\nPor favor seleccione las rutas faltantes.")
            return None
        else:
            return rutas_general
    except Exception as ex:
        messagebox.showerror("Error", "Error al verificar las rutas:" + str(ex))

def seleccionar_archivo(nombre: str) -> None:
    try:
        ruta: str = filedialog.askopenfilename(
            initialdir="/",
            title="Seleccionar archivo " + nombre,
            filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
        set_ruta(ruta, nombre)
    except Exception as ex:
        messagebox.showerror("Error", "Error al seleccionar el archivo:" + str(ex))

def seleccionar_carpeta(nombre: str) -> None:
    try:
        ruta: str = filedialog.askdirectory(
            initialdir="/",
            title="Seleccionar carpeta " + nombre
        )
        set_ruta(ruta, nombre)
    except Exception as ex:
        messagebox.showerror("Error", "Error al seleccionar la carpeta:" + str(ex))