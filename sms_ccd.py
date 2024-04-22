from clase_sms_ccd import Clase_SMS
from datetime import datetime, timedelta
from tkinter import messagebox
from customtkinter import *
from resource_path import *
import pandas as pd
import warnings
import threading
import time

warnings.filterwarnings("ignore")

class App_SMS():    
    def salir(self):
        self.app.destroy()
    
    def deshabilitar_botones(self):
        self.boton1.configure(state="disabled")
        self.boton2.configure(state="disabled")
        self.boton3.configure(state="disabled")
        self.boton4.configure(state="disabled")
        self.boton_salir.configure(state="disabled")
    
    def habilitar_botones(self):
        self.boton1.configure(state="normal")
        self.boton2.configure(state="normal")
        self.boton3.configure(state="normal")
        self.boton4.configure(state="normal")
        self.boton_salir.configure(state="normal")
    
    def verificar_thread(self, thread):
        if thread.is_alive():
            self.app.after(1000, self.verificar_thread, thread)
        else:
            self.habilitar_botones()
    
    def iniciar_proceso(self, accion):
        self.deshabilitar_botones()
        if accion == 1:
            thread = threading.Thread(target=self.accion_boton1)
        elif accion == 2:
            thread = threading.Thread(target=self.accion_boton2)
        elif accion == 3:
            thread = threading.Thread(target=self.accion_boton3)
        elif accion == 4:
            thread = threading.Thread(target=self.accion_boton4)
        else:
            return        
        thread.start()
        self.app.after(1000, self.verificar_thread, thread)
    
    def accion_boton1(self):
        self.progressbar.start()
        try:
            self.inicio = time.time()
            self.reporte.actualizar_base_celulares()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton2(self):
        self.progressbar.start()
        try:
            self.reporte.exportar_deudores()
            self.inicio_sap = time.time()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton3(self):
        self.progressbar.start()
        try:
            self.fin_sap = time.time()
            self.reporte.preparar_fbl5n()
            self.reporte.preparar_recaudacion()
            self.reporte.preparar_modelo()
            self.reporte.preparar_zfir60()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton4(self):
        self.progressbar.start()
        try:
            self.reporte.exportar_archivos_txt()
            self.fin = time.time()
            tiempo_sap = self.fin_sap - self.inicio_sap
            tiempo_total = self.fin - self.inicio
            tiempo_proceso = tiempo_total - tiempo_sap
            messagebox.showinfo("INFO", "TIEMPOS DE EJECUCIÓN: \n"
                                + "\nTiempo Proceso: " + str(round(tiempo_proceso, 2)) + " segundos."
                                + "\nTiempo SAP: " + str(round(tiempo_sap, 2)) + " segundos."
                                + "\nTiempo Total: " + str(round(tiempo_total, 2)) + " segundos.")
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def generar_reporte(self):
        try:
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
            self.reporte = Clase_SMS(fecha_hoy, fecha_ayer, fecha_hoy_txt, ruta_zfir60, ruta_modelo, ruta_dacxanalista)
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e)
                                + "\n\nAsegúrese de tener el archivo 'RUTAS.xlsx' en la misma carpeta que el ejecutable.")
            self.app.destroy()
    
    def crear_app(self):        
        self.app = CTk()
        self.app.title("SMS C&CD")
        icon_path = resource_path("./images/icono.ico")
        if os.path.isfile(icon_path):
            self.app.iconbitmap(icon_path)
        else:
            messagebox.showwarning("ADVERTENCIA", "No se encontró el archivo 'icono.ico' en la ruta: " + icon_path)
        self.app.resizable(False, False)
        set_appearance_mode("light")
        
        main_frame = CTkFrame(self.app)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand=True)
        
        frame_title = CTkFrame(main_frame)
        frame_title.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        titulo = CTkLabel(frame_title, text="Mensajes de Texto C&CD", font=("Arial",25,"bold"))
        titulo.pack(fill="both", expand=True, padx=(20, 20), ipady=20, anchor="center")
        
        frame_botones = CTkFrame(main_frame)
        frame_botones.grid(row=1, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        
        self.boton1 = CTkButton(frame_botones, text="ACTUALIZAR CELULARES", font=("Calibri",17), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                                width=25, corner_radius=10, command=lambda: self.iniciar_proceso(1))
        self.boton1.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 0))
        
        self.boton2 = CTkButton(frame_botones, text="EXPORTAR DEUDORES SAP", font=("Calibri",17), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                                width=25, corner_radius=10, command=lambda: self.iniciar_proceso(2))
        self.boton2.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 0))
        
        frame_checkbox = CTkFrame(frame_botones)
        frame_checkbox.pack(anchor="center", fill="both", expand=True, padx=(20, 20), pady=(20, 0))
        
        label_exportar = CTkLabel(frame_checkbox, text="SELECCIONAR FORMATO:", font=("Calibri",17,"bold"))
        label_exportar.pack(side="top", anchor="w", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(10, 0))
        
        self.var_hoja_calculo = BooleanVar()
        self.var_hoja_calculo.set(True)
        self.var_hoja_calculo.trace("w", lambda *args: self.var_fichero_local.set(not self.var_hoja_calculo.get()))
        checkbox_hoja = CTkCheckBox(frame_checkbox, text="Hoja de cálculo", font=("Calibri",17), 
                                    border_color="#d11515", border_width=2, fg_color="#d11515", 
                                    hover_color="#d11515", variable=self.var_hoja_calculo)
        checkbox_hoja.pack(side="left", anchor="w", fill="both", expand=True, ipady=10, padx=(20, 10), pady=(0, 10))
        
        self.var_fichero_local = BooleanVar()
        self.var_fichero_local.set(False)
        self.var_fichero_local.trace("w", lambda *args: self.var_hoja_calculo.set(not self.var_fichero_local.get()))
        checkbox_fichero = CTkCheckBox(frame_checkbox, text="Fichero local", font=("Calibri",17), 
                                    border_color="#d11515", border_width=2, fg_color="#d11515", 
                                    hover_color="#d11515", variable=self.var_fichero_local)
        checkbox_fichero.pack(side="right", anchor="w", fill="both", expand=True, ipady=10, padx=(10, 20), pady=(0, 10))
        
        self.boton3 = CTkButton(frame_botones, text="PREPARAR BASES", font=("Calibri",17), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                                width=25, corner_radius=10, command=lambda: self.iniciar_proceso(3))
        self.boton3.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 0))
        
        self.boton4 = CTkButton(frame_botones, text="EXPORTAR TXT", font=("Calibri",17), text_color="black", 
                                fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                                width=25, corner_radius=10, command=lambda: self.iniciar_proceso(4))
        self.boton4.pack(anchor="center", fill="both", expand=True, ipady=10, padx=(20, 20), pady=(20, 20))
        
        self.progressbar = CTkProgressBar(main_frame, mode="indeterminate", orientation="horizontal", 
                                            progress_color="#d11515", height=10, border_width=0)
        self.progressbar.grid(row=2, column=0, padx=(20, 20), pady=(10, 0), sticky="nsew")
        
        self.boton_salir = CTkButton(main_frame, text="SALIR", font=("Calibri",17), text_color="black", 
                                    fg_color="transparent", border_color="black", border_width=3, hover_color="#d11515", 
                                    width=10, corner_radius=10, command=self.salir)
        self.boton_salir.grid(row=3, column=0, padx=(150, 150), pady=(20, 20), sticky="nsew")
        
        self.app.mainloop()

def main():
    app = App_SMS()
    app.generar_reporte()
    app.crear_app()

if __name__ == "__main__":
    main()