from sms_ccd import SMS_CCD
from tkinter import messagebox, Entry
from customtkinter import CTk, CTkFrame, CTkButton, CTkCheckBox, CTkLabel, CTkProgressBar
from customtkinter import set_appearance_mode, BooleanVar
from resource_path import *
import threading
import time


class App_SMS():
    def salir(self):
        self.app.destroy()
    
    def deshabilitar_botones(self):
        self.boton1.configure(state="disabled")
        self.boton2.configure(state="disabled")
        self.checkbox_hoja.configure(state="disabled")
        self.checkbox_fichero.configure(state="disabled")
        self.boton3.configure(state="disabled")
        self.boton4.configure(state="disabled")
        self.boton_salir.configure(state="disabled")
    
    def habilitar_botones(self):
        self.boton1.configure(state="normal")
        self.boton2.configure(state="normal")
        self.checkbox_hoja.configure(state="normal")
        self.checkbox_fichero.configure(state="normal")
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
            inicio = time.time()
            resultados = self.reporte.actualizar_base_celulares()
            fin = time.time()
            self.proceso1 = fin - inicio
            total_deudores = resultados[0]
            total_celulares = resultados[1]
            if total_deudores == total_celulares:
                messagebox.showinfo("INFO", "Todos los socios["+str(total_deudores)+"] cuentan con celulares.")
            else:
                messagebox.showinfo(
                    "INFO", "BASE DE CELULARES ACTUALIZADA!\n"
                    + "\n- CON CELULAR: " + str(total_celulares) 
                    + "\n- SIN CELULAR: " + str(total_deudores-total_celulares)
                    + "\n- TOTAL: " + str(total_deudores))
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton2(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            self.reporte.exportar_deudores()
            fin = time.time()
            self.proceso2 = fin - inicio
            self.inicio_sap = time.time()
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton3(self):
        self.fin_sap = time.time()
        self.progressbar.start()
        try:
            inicio = time.time()
            if self.var_hoja_calculo.get() == True:
                self.reporte.preparar_fbl5n_hoja_calculo()
            else:
                self.reporte.preparar_fbl5n_fichero_local()
            self.reporte.preparar_recaudacion()
            self.reporte.preparar_modelo()
            self.reporte.preparar_zfir60()
            resultados = self.reporte.return_resultados()
            fin = time.time()
            self.proceso3 = fin - inicio
            ld_equipos = resultados[0]
            ld_recaudacion = resultados[1]
            zfir60 = resultados[2]
            messagebox.showinfo(
                "INFO", "REGISTROS VALIDADOS:\n" 
                + "\n- En LD de EQUIPOS: " + str(ld_equipos)
                + "\n- En LD de RECAUDACION: " + str(ld_recaudacion)
                + "\n- Con Deuda Vencida (ZFIR60): " + str(zfir60))
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def accion_boton4(self):
        self.progressbar.start()
        try:
            inicio = time.time()
            lista_nivel_1, lista_ld = self.reporte.exportar_archivos_txt()
            fin = time.time()
            proceso4 = fin - inicio
            self.tiempo_proceso = round((self.proceso1 + self.proceso2 + self.proceso3 + proceso4),2)
            tiempo_sap = round((self.fin_sap - self.inicio_sap),2)
            self.tiempo_total = round((self.tiempo_proceso + tiempo_sap),2)
            
            self.entry_nivel1.configure(state="normal")
            self.entry_nivel1.delete(0, "end")
            self.entry_nivel1.insert(0, lista_nivel_1)
            self.entry_nivel1.configure(state="readonly")
            self.entry_ld.configure(state="normal")
            self.entry_ld.delete(0, "end")
            self.entry_ld.insert(0, lista_ld)
            self.entry_ld.configure(state="readonly")
            
            self.entry_total.configure(state="normal")
            self.entry_total.delete(0, "end")
            self.entry_total.insert(0, str(self.tiempo_total) + " s")
            self.entry_total.configure(state="readonly")
            # Mensajes listos
            messagebox.showinfo(
                "SMS C&CD", "MENSAJES LISTOS:"
                + "\n- LD: " + lista_ld + " destinatarios." 
                + "\n- Nivel 1: " + lista_nivel_1 + " destinatarios."
                + "\n\nTIEMPOS DE EJECUCIÓN:"
                + "\n- Proceso: " + str(self.tiempo_proceso) + " segundos."
                + "\n- SAP: " + str(tiempo_sap) + " segundos."
                + "\n- Total: " + str(self.tiempo_total) + " segundos.")
            os.startfile(resource_path("./CARGAS/"))
        except Exception as e:
            messagebox.showerror("ERROR", "Algo salió mal. Por favor, intente nuevamente.\nDetalles: " + str(e))
        finally:
            self.progressbar.stop()
    
    def crear_app(self):
        self.app = CTk()
        self.app.title("SMS C&CD")
        icon_path = resource_path("./icono.ico")
        if os.path.isfile(icon_path):
            self.app.iconbitmap(icon_path)
        else:
            messagebox.showwarning("ADVERTENCIA", "No se encontró el archivo 'icono.ico' en la ruta: " + icon_path)
        self.app.resizable(False, False)
        set_appearance_mode("light")
        
        main_frame = CTkFrame(self.app)
        main_frame.pack_propagate("True")
        main_frame.pack(fill="both", expand=True)
        
        frame_botones = CTkFrame(main_frame)
        frame_botones.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        self.boton1 = CTkButton(
            frame_botones, text="1: Actualizar Números", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(1))
        self.boton1.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        self.boton2 = CTkButton(
            frame_botones, text="2: Exportar Deudores", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(2))
        self.boton2.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        frame_checkbox = CTkFrame(frame_botones, border_width=2, border_color="black")
        frame_checkbox.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        label_exportar = CTkLabel(frame_checkbox, text="Seleccionar formato SAP:", font=("Calibri",12,"bold"))
        label_exportar.pack(padx=10, pady=5)
        
        self.var_hoja_calculo = BooleanVar()
        self.var_hoja_calculo.set(True)
        self.var_hoja_calculo.trace("w", lambda *args: self.var_fichero_local.set(not self.var_hoja_calculo.get()))
        self.checkbox_hoja = CTkCheckBox(
            frame_checkbox, text="Hoja", font=("Calibri",12), width=5, 
            border_color="#d11515", border_width=2, fg_color="#d11515", 
            hover_color="#d11515", variable=self.var_hoja_calculo)
        self.checkbox_hoja.pack(side="left", padx=(30,10), pady=(0, 10))
        
        self.var_fichero_local = BooleanVar()
        self.var_fichero_local.set(False)
        self.var_fichero_local.trace("w", lambda *args: self.var_hoja_calculo.set(not self.var_fichero_local.get()))
        self.checkbox_fichero = CTkCheckBox(
            frame_checkbox, text="Fichero", font=("Calibri",12), width=5, 
            border_color="#d11515", border_width=2, fg_color="#d11515", 
            hover_color="#d11515", variable=self.var_fichero_local)
        self.checkbox_fichero.pack(side="left", padx=(10,30), pady=(0, 10))
        
        self.boton3 = CTkButton(
            frame_botones, text="3: Preparar Bases", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(3))
        self.boton3.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        self.boton4 = CTkButton(
            frame_botones, text="4: Exportar TXT", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=200, corner_radius=5, command=lambda: self.iniciar_proceso(4))
        self.boton4.pack(fill="both", expand=True, ipady=2, padx=10, pady=(10, 0))
        
        self.boton_salir = CTkButton(
            frame_botones, text="Salir", font=("Calibri",12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=100, height=10, corner_radius=5, command=self.salir)
        self.boton_salir.pack(ipady=2, padx=50, pady=10)
        
        frame_output = CTkFrame(main_frame)
        frame_output.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        label_nivel1 = CTkLabel(frame_output, text="Nivel 1: ", font=("Calibri",12))
        label_nivel1.grid(row=0, column=0, padx=(10,0), pady=(5,0), sticky="e")
        self.entry_nivel1 = Entry(frame_output, font=("Calibri",12), width=5, state="readonly")
        self.entry_nivel1.grid(row=0, column=1, padx=(0,10), pady=(5,0), sticky="w")
        
        label_ld = CTkLabel(frame_output, text="LD: ", font=("Calibri",12))
        label_ld.grid(row=1, column=0, padx=(10,0), pady=(0,5), sticky="e")
        self.entry_ld = Entry(frame_output, font=("Calibri",12), width=5, state="readonly")
        self.entry_ld.grid(row=1, column=1, padx=(0,10), pady=(0,5), sticky="w")
        
        label_total = CTkLabel(frame_output, text="Duración: ", font=("Calibri",12))
        label_total.grid(row=0, column=2, padx=(10,0), pady=(5,0), sticky="e")
        self.entry_total = Entry(frame_output, font=("Calibri",12), width=6, state="readonly")
        self.entry_total.grid(row=0, column=3, padx=(0,10), pady=(5,0), sticky="w")
        
        self.boton_config = CTkButton(
            frame_output, text="Configurar Rutas", font=("Calibri", 12), text_color="black", 
            fg_color="transparent", border_color="black", border_width=2, hover_color="#d11515", 
            width=25, corner_radius=5, command=self.salir)
        self.boton_config.grid(row=1, rowspan=2, column=2, columnspan=2, padx=(10,10), pady=5, sticky="ns")
        
        self.progressbar = CTkProgressBar(
            main_frame, mode="indeterminate", orientation="horizontal", 
            progress_color="#d11515", height=7, border_width=0)
        self.progressbar.pack(fill="x", expand=True, padx=10, pady=10)
        
        self.app.mainloop()
    
    def generar_reporte(self):
        try:
            self.reporte = SMS_CCD()
            self.crear_app()
        except Exception as e:
            messagebox.showerror(
                "ERROR", 
                "Algo salió mal. Por favor, intente nuevamente.\n\nDetalles: " + str(e) + 
                "\n\nAsegúrese de tener el archivo 'RUTAS.xlsx' en la misma carpeta que el ejecutable.")