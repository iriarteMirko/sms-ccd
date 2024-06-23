from ..database.conexion import get_rutas, set_ruta
from customtkinter import CTk, filedialog
from tkinter import messagebox


def verificar_rutas() -> list[str] | None:
    try:
        rutas: list[tuple[str, str]] = get_rutas()
        rutas_general = [ruta[1] for ruta in rutas if ruta[1] is not None]
        rutas_vacias = [ruta[0] for ruta in rutas if not ruta[1]]
        if rutas_vacias:
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

def seleccionar_archivo(nombre: str, ventana: CTk) -> None:
    try:
        ventana.attributes("-disabled", True)
        ruta: str = filedialog.askopenfilename(
            initialdir="/",
            title="Seleccionar archivo " + nombre,
            filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
        set_ruta(ruta, nombre)
        ventana.attributes("-disabled", False)
        ventana.attributes("-topmost", True)
    except Exception as ex:
        messagebox.showerror("Error", "Error al seleccionar el archivo:" + str(ex))

def seleccionar_carpeta(nombre: str, ventana: CTk) -> None:
    try:
        ventana.attributes("-disabled", True)
        ruta: str = filedialog.askdirectory(
            initialdir="/",
            title="Seleccionar carpeta " + nombre
        )
        set_ruta(ruta, nombre)
        ventana.attributes("-disabled", False)
        ventana.attributes("-topmost", True)
    except Exception as ex:
        messagebox.showerror("Error", "Error al seleccionar la carpeta:" + str(ex))