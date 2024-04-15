from clase_sms_ccd import Clase_SMS
from datetime import datetime, timedelta
from tkinter import messagebox
from customtkinter import *
import pandas as pd
import warnings
import threading
import time

warnings.filterwarnings("ignore")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    
    def salir():
        app.destroy()

    def verificar_thread(thread):
        if thread.is_alive():
            app.after(1000, verificar_thread, thread)
        else:
            boton1.configure(state="normal")
            boton2.configure(state="normal")
            boton3.configure(state="normal")
            boton4.configure(state="normal")
            boton_salir.configure(state="normal")

    def iniciar_proceso(accion):
        if accion == 1:
            thread = threading.Thread(target=accion_boton1)
        elif accion == 2:
            thread = threading.Thread(target=accion_boton2)
        elif accion == 3:
            thread = threading.Thread(target=accion_boton3)
        elif accion == 4:
            thread = threading.Thread(target=accion_boton4)
        else:
            pass
        boton1.configure(state="disabled")
        boton2.configure(state="disabled")
        boton3.configure(state="disabled")
        boton4.configure(state="disabled")
        boton_salir.configure(state="disabled")
        
        thread.start()
        app.after(1000, verificar_thread, thread)

    def accion_boton1():
        global inicio
        progressbar.start()
        try:
            inicio = time.time()
            reporte.traer_archivos()
            reporte.preparar_zfir60()
            messagebox.showinfo("PASO 1", "COMPLETADO")
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            progressbar.stop()

    def accion_boton2():
        global inicio_sap
        progressbar.start()
        try:
            reporte.exportar_deudores()
            os.startfile(resource_path("./bases/Deudores.xlsx"))
            inicio_sap = time.time()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            progressbar.stop()

    def accion_boton3():
        global fin_sap
        progressbar.start()
        try:
            fin_sap = time.time()
            reporte.preparar_fbl5n()
            reporte.preparar_recaudacion()
            messagebox.showinfo("PASO 2", "COMPLETADO")
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            progressbar.stop()

    def accion_boton4():
        global fin
        progressbar.start()
        try:
            reporte.exportar_archivos_txt()
            fin = time.time()
            tiempo_sap = fin_sap - inicio_sap
            tiempo_total = fin - inicio
            tiempo_proceso = tiempo_total - tiempo_sap
            messagebox.showinfo("SMS C&CD", "MENSAJES LISTOS!\n"
                                + "\nTiempo Proceso: " + str(round(tiempo_proceso, 2)) + " segundos."
                                + "\nTiempo SAP: " + str(round(tiempo_sap, 2)) + " segundos."
                                + "\nTiempo Total: " + str(round(tiempo_total, 2)) + " segundos.")
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            progressbar.stop()

    def generar_reporte():
        global reporte
        excel_rutas = resource_path("./RUTAS.xlsx")
        df_rutas = pd.read_excel(excel_rutas)
        fecha_hoy = datetime.today()
        fecha_ayer = fecha_hoy - timedelta(days=1)
        fecha_ayer = fecha_ayer.strftime("%Y%m%d")
        fecha_hoy = datetime.today().strftime("%Y%m%d")
        fecha_hoy_txt = datetime.today().strftime("%d.%m.%Y")
        ruta_zfir60 = df_rutas["RUTA"][0]
        ruta_modelo = df_rutas["RUTA"][1]
        ruta_dacxanalista = df_rutas["RUTA"][2]
        
        reporte = Clase_SMS(fecha_hoy, fecha_ayer, fecha_hoy_txt, ruta_zfir60, ruta_modelo, ruta_dacxanalista)

    def crear_app():
        global app, boton1, boton2, boton3, boton4, progressbar, boton_salir
        generar_reporte()
        app = CTk()
        app.title("SMS C&CD")
        app.iconbitmap(resource_path("./images/icono.ico"))
        app.resizable(False, False)
        set_appearance_mode("light")
        
        main_frame = CTkFrame(app)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand=True)
        
        frame_title = CTkFrame(main_frame)
        frame_title.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        titulo = CTkLabel(frame_title, text="Mensajes de Texto C&CD", font=("Arial",25,"bold"))
        titulo.pack(fill="both", expand=True, padx=(20,20), ipady=20, anchor="center")
        
        frame_botones = CTkFrame(main_frame)
        frame_botones.grid(row=1, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        boton1 = CTkButton(frame_botones, text=">>> PASO 1 <<<", font=("Calibri",17), text_color="black", 
                            fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                            width=25, corner_radius=10, command=lambda: iniciar_proceso(1))
        boton1.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 0))
        
        boton2 = CTkButton(frame_botones, text="EXPORTAR DEUDORES SAP", font=("Calibri",17), text_color="black", 
                            fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                            width=25, corner_radius=10, command=lambda: iniciar_proceso(2))
        boton2.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 0))
        
        boton3 = CTkButton(frame_botones, text=">>> PASO 2 <<<", font=("Calibri",17), text_color="black", 
                            fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                            width=25, corner_radius=10, command=lambda: iniciar_proceso(3))
        boton3.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 0))
        
        boton4 = CTkButton(frame_botones, text="EXPORTAR ARCHIVOS TXT", font=("Calibri",17), text_color="black", 
                            fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                            width=25, corner_radius=10, command=lambda: iniciar_proceso(4))
        boton4.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 20))
        
        progressbar = CTkProgressBar(main_frame, mode="indeterminate", orientation="horizontal", 
                                        progress_color="#d11515", height=10, border_width=0)
        progressbar.grid(row=2, column=0, padx=(20, 20), pady=(10, 0), sticky="nsew")
        
        boton_salir = CTkButton(main_frame, text="SALIR", font=("Calibri",17), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                                width=10, corner_radius=10, command=salir)
        boton_salir.grid(row=3, column=0, padx=(150, 150), pady=(20, 20), sticky="nsew")
        
        app.mainloop()

    crear_app()

if __name__ == "__main__":
    main()