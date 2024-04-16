import pandas as pd
import shutil

class Clase_SMS:
    def __init__(self, fecha_hoy, fecha_ayer, fecha_hoy_txt, ruta_zfir60, ruta_modelo, ruta_dacxanalista):
        self.fecha_hoy = fecha_hoy
        self.fecha_ayer = fecha_ayer
        self.fecha_hoy_txt = fecha_hoy_txt
        
        self.ruta_zfir60 = ruta_zfir60 + "/ZFIR60_" + self.fecha_hoy + ".xlsx"
        self.ruta_modelo = ruta_modelo + "/Modelo de Evaluación de Pedidos de Equipos_" + self.fecha_hoy + ".xlsx"
        
        self.fbl5n = "./bases/FBL5N.xlsx"
        self.reporte_recaudacion = "./bases/Reporte_Recaudacion_" + self.fecha_hoy + ".csv"
        self.deudores = "./bases/Deudores.xlsx"
        
        self.modelo = "./modelo-zfir-recaudacion/Modelo de Evaluación de Pedidos de Equipos_" + self.fecha_hoy + ".xlsx"
        self.zfir = "./modelo-zfir-recaudacion/Zfir" + self.fecha_hoy + ".xlsx"
        self.recaudacion = "./modelo-zfir-recaudacion/Recaudacion_" + self.fecha_hoy + ".xlsx"
        
        self.ruta_dacxanalista = ruta_dacxanalista + "/Nuevo_DACxANALISTA.xlsx"
        self.ruta_base_celulares = "./bases/Base_Celulares_CCD.xlsx"
        
        self.ld = "./archivos-txt/LD " + self.fecha_hoy_txt + ".txt"
        self.nivel_1 = "./archivos-txt/Nivel 1 " + self.fecha_hoy_txt + ".txt"

    def traer_archivos(self):
        shutil.copy(self.ruta_modelo, self.modelo)

    def preparar_zfir60(self):
        df_zfir60 = pd.read_excel(self.ruta_zfir60, sheet_name="Sheet1")
        df_zfir60 = df_zfir60[["Cliente Pa", "Total Vencida"]]
        df_zfir60["Total Vencida"] = df_zfir60["Total Vencida"].clip(lower=0)
        df_zfir60 = df_zfir60.groupby("Cliente Pa")["Total Vencida"].sum().reset_index()
        df_zfir60.to_excel(self.zfir, sheet_name="BASE", index=False)

    def exportar_deudores(self):
        global df_recaudacion
        df_recaudacion = pd.read_csv(self.reporte_recaudacion, encoding="latin1")
        df_recaudacion = df_recaudacion.drop("USER_ID", axis=1)
        df_recaudacion = df_recaudacion[df_recaudacion["FECHA_RECAUDACION"] == int(self.fecha_ayer)]
        df_recaudacion[["SAP"]].to_excel(self.deudores, index=False)

    def preparar_fbl5n(self):
        global df_fbl5n
        df_fbl5n = pd.read_excel(self.fbl5n)
        df_fbl5n = df_fbl5n[df_fbl5n["Cuenta"].notna()]
        df_fbl5n = df_fbl5n[df_fbl5n["ACC"] == "PE07"]
        df_fbl5n = df_fbl5n[["Cuenta","Importe en ML"]]
        df_fbl5n["Importe en ML"] = df_fbl5n["Importe en ML"] * -1
        df_fbl5n = df_fbl5n.groupby("Cuenta")["Importe en ML"].sum().reset_index()

    def preparar_recaudacion(self):
        df_fbl5n.set_index("Cuenta", inplace=True)
        df_recaudacion["FALTA"] = df_recaudacion["SAP"].map(df_fbl5n["Importe en ML"])
        df_recaudacion["FALTA"] = df_recaudacion["FALTA"].fillna(0)
        df_fbl5n.reset_index(inplace=True)
        df_recaudacion["RESTA"] = df_recaudacion["LIMITE_CREDITICIO"] - df_recaudacion["SALDO_ACTUAL"]
        df_recaudacion["TOTAL"] = df_recaudacion["FALTA"] + df_recaudacion["RESTA"]
        df_recaudacion.to_excel(self.recaudacion, sheet_name="BASE", index=False)

    def exportar_archivos_txt(self):
        pass