from ..utils.resource_path import *
from ..models.sms_apoyo import SMS_APOYO
from datetime import datetime, timedelta
import pandas as pd


class SMS_CCD():
    def __init__(self, rutas: list[str]) -> None:
        self.ruta_regla: str = resource_path("src/utils/REGLA.xlsx")
        
        fecha_hoy: datetime = datetime.today()
        fecha_ayer: datetime = fecha_hoy - timedelta(days=1)
        self.fecha_ayer: str = fecha_ayer.strftime("%Y%m%d")
        self.fecha_hoy: str = fecha_hoy.strftime("%Y%m%d")
        self.fecha_hoy_txt: str = fecha_hoy.strftime("%d.%m.%Y")
        
        self.ruta_dacxanalista: str = rutas[0]
        self.ruta_modelo: str = rutas[1] + "/Modelo de Evaluación de Pedidos de Equipos_"+self.fecha_hoy+".xlsx"
        self.ruta_zfir60: str = rutas[2] + "/ZFIR60_"+self.fecha_hoy+".xlsx"
        sms_ccd: str = rutas[3]
        
        self.bases: str = sms_ccd + "/BASES"
        self.ruta_base_celulares: str = self.bases + "/Base_Celulares_CCD.xlsx"
        self.reporte_recaudacion: str = self.bases + "/Reporte_Recaudacion_"+self.fecha_hoy+".csv"
        self.fbl5n_hoja: str = self.bases + "/FBL5N_HOJA.xlsx"
        self.fbl5n_fichero: str = self.bases + "/FBL5N_FICHERO.xlsx"
        self.deudores: str = self.bases + "/Deudores.xlsx"
        
        self.cargas: str = sms_ccd + "/CARGAS"
        self.ld_txt: str = self.cargas + "/LD "+self.fecha_hoy_txt+".txt"
        self.nivel_1_txt: str = self.cargas + "/Nivel 1 "+self.fecha_hoy_txt+".txt"
        self.apoyos_txt: str = self.cargas + "/Apoyos "+self.fecha_hoy_txt+".txt"
        
        vacaciones: str = rutas[4]
        self.ruta_vacaciones: str = vacaciones + "/VACACIONES.xlsx"
        self.ruta_apoyos: str = vacaciones + "/APOYOS_CCD.xlsx"
        
        self.contador: int = 0
    
    def abrir_archivo(self, path: str) -> None:
        os.startfile(resource_path(path))
    
    def actualizar_base_celulares(self) -> list[int]:
        df_base_celulares: pd.DataFrame = pd.read_excel(self.ruta_base_celulares)
        df_dacxanalista: pd.DataFrame = pd.read_excel(self.ruta_dacxanalista, sheet_name="Base_NUEVA")
        df_dac_tipos: pd.DataFrame = pd.read_excel(self.ruta_regla, sheet_name="NO_VALIDOS")
        
        lista_tipo_dac_no_validos: list[str] = df_dac_tipos["TIPOS_NO_VALIDOS"].to_list()
        columnas_requeridas: list[str] = ["DEUDOR", "NOMBRE", "REGION", "ANALISTA_ACT", "TIPO_DAC", "ESTADO"]
        
        df_dacxanalista = df_dacxanalista[columnas_requeridas]
        df_dacxanalista = df_dacxanalista[~df_dacxanalista["TIPO_DAC"].isin(lista_tipo_dac_no_validos)]
        df_dacxanalista = df_dacxanalista[df_dacxanalista["ESTADO"].isin(["OPERATIVO CON MOVIMIENTO", "OPERATIVO SIN MOVIMIENTO"])]
        df_dacxanalista = df_dacxanalista.merge(df_base_celulares, on="DEUDOR", how="right")
        df_dacxanalista = df_dacxanalista.rename(columns={
            "NOMBRE_x": "NOMBRE",
            "REGION_x": "REGION",
            "ANALISTA_ACT_x": "ANALISTA_ACT",
            "TIPO_DAC_x": "TIPO_DAC",
            "ESTADO_x": "ESTADO"
        })
        df_dacxanalista = df_dacxanalista[columnas_requeridas + ["CELULAR"]]
        df_dacxanalista["CELULAR"] = df_dacxanalista["CELULAR"].astype("Int64")
        df_dacxanalista.dropna(subset=["NOMBRE"], inplace=True)
        df_dacxanalista["CELULAR"] = df_dacxanalista["CELULAR"].fillna(0)
        df_dacxanalista.reset_index(drop=True, inplace=True)
        df_dacxanalista.to_excel(self.ruta_base_celulares, index=False)
        # Preparar base celulares
        df_celulares = df_dacxanalista[["DEUDOR", "NOMBRE", "CELULAR"]]
        total_deudores: int = df_celulares.shape[0]
        df_celulares = df_celulares[df_celulares["CELULAR"]!=0]
        df_celulares.reset_index(drop=True, inplace=True)
        total_celulares: int = df_celulares.shape[0]
        # Limpiar nombres
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("á", "a")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("é", "e")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("í", "i")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("ó", "o")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("ú", "u")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("ñ", "n")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Á", "A")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("É", "E")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Í", "I")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Ó", "O")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Ú", "U")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("Ñ", "N")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("  ", " ")
        df_celulares["NOMBRE"] = df_celulares["NOMBRE"].str.replace("  ", " ")
        
        self.df_celulares: pd.DataFrame = df_celulares
        resultados: list[int] = [total_deudores, total_celulares]
        return resultados
    
    def generar_texto(self, row: pd.Series) -> str:
        df_texto: pd.DataFrame = pd.read_excel(self.ruta_regla, sheet_name="TEXTO")
        if self.contador == 0:
            if row["TIPO"] == "DISPONIBLE":
                return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][0]}{row["NOMBRE"]}{df_texto["TEXTO_2"][0]}{row["TOTAL"]}{df_texto["TEXTO_3"][0]}'
            elif row["TIPO"] == "SOBREGIRO":
                return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][1]}{row["NOMBRE"]}{df_texto["TEXTO_2"][1]}{row["TOTAL"]}{df_texto["TEXTO_3"][1]}'
            elif row["TIPO"] == "SIN_LINEA":
                return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][2]}{row["NOMBRE"]}{df_texto["TEXTO_2"][2]}'
        elif self.contador == 1:
            if row["TIPO"] == "DISPONIBLE":
                return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][3]}{row["NOMBRE"]}{df_texto["TEXTO_2"][3]}{row["TOTAL"]}{df_texto["TEXTO_3"][3]}'
            elif row["TIPO"] == "SOBREGIRO":
                return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][4]}{row["NOMBRE"]}{df_texto["TEXTO_2"][4]}{row["TOTAL"]}{df_texto["TEXTO_3"][4]}'
            elif row["TIPO"] == "SIN_LINEA":
                return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][5]}{row["NOMBRE"]}{df_texto["TEXTO_2"][5]}'
        else:
            return f'51{row["CELULAR"]}{df_texto["TEXTO_1"][6]}{row["Total Vencida"]}{df_texto["TEXTO_2"][6]}'
    
    def exportar_deudores(self) -> None:
        archivos: list[str] = os.listdir(self.bases)
        for archivo in archivos:
            if "Reporte_Recaudacion_" in archivo and self.fecha_hoy not in archivo:
                os.remove(f'{self.bases}/{archivo}')
        
        df_recaudacion: pd.DataFrame = pd.read_csv(self.reporte_recaudacion, encoding="latin1")
        df_recaudacion = df_recaudacion.drop("USER_ID", axis=1)
        df_recaudacion = df_recaudacion[df_recaudacion["FECHA_RECAUDACION"] == int(self.fecha_ayer)]
        df_recaudacion[["SAP"]].to_excel(self.deudores, index=False)
        df_recaudacion.reset_index(drop=True, inplace=True)
        self.df_recaudacion: pd.DataFrame = df_recaudacion
        self.abrir_archivo(self.deudores)
    
    def preparar_fbl5n_hoja_calculo(self) -> None:
        df_fbl5n: pd.DataFrame = pd.read_excel(self.fbl5n_hoja)
        df_fbl5n = df_fbl5n[df_fbl5n["Cuenta"].notna()]
        df_fbl5n = df_fbl5n[df_fbl5n["ACC"] == "PE07"]
        df_fbl5n = df_fbl5n[["Cuenta","Importe en ML"]]
        df_fbl5n["Importe en ML"] = df_fbl5n["Importe en ML"] * -1
        df_fbl5n = df_fbl5n.groupby("Cuenta")["Importe en ML"].sum().reset_index()
        df_fbl5n.set_index("Cuenta", inplace=True)
        self.df_fbl5n: pd.DataFrame = df_fbl5n
    
    def preparar_fbl5n_fichero_local(self) -> None:
        df_fbl5n: pd.DataFrame = pd.read_excel(self.fbl5n_fichero)
        df_fbl5n = df_fbl5n.iloc[:, 3:] # Elimina las 3 primeras columnas
        df_fbl5n = df_fbl5n.iloc[7:, :] # Elimina las 7 primeras filas
        df_fbl5n = df_fbl5n.drop(df_fbl5n.index[1]) # Elimina la segunda fila (después de eliminar las 7 primeras)
        df_fbl5n = df_fbl5n.iloc[:-3, :] # Elimina las 3 últimas filas
        df_fbl5n.columns = df_fbl5n.iloc[0] # Nuevo encabezado
        df_fbl5n = df_fbl5n[1:]
        df_fbl5n = df_fbl5n[df_fbl5n["Cuenta"].notna()]
        df_fbl5n = df_fbl5n[df_fbl5n["ACC"] == "PE07"]
        df_fbl5n = df_fbl5n.rename(columns={"     Importe en ML":"Importe en ML"})
        df_fbl5n = df_fbl5n[["Cuenta","Importe en ML"]]
        df_fbl5n["Importe en ML"] = df_fbl5n["Importe en ML"] * -1
        df_fbl5n = df_fbl5n.groupby("Cuenta")["Importe en ML"].sum().reset_index()
        df_fbl5n.set_index("Cuenta", inplace=True)
        self.df_fbl5n: pd.DataFrame = df_fbl5n
    
    def preparar_recaudacion(self) -> None:
        self.df_recaudacion["FALTA"] = self.df_recaudacion["SAP"].map(self.df_fbl5n["Importe en ML"])
        self.df_recaudacion["FALTA"].fillna(0, inplace=True)
        self.df_recaudacion["RESTA"] = self.df_recaudacion["LIMITE_CREDITICIO"] - self.df_recaudacion["SALDO_ACTUAL"]
        self.df_recaudacion["TOTAL"] = self.df_recaudacion["FALTA"] + self.df_recaudacion["RESTA"]
        
        df_cruce_recaudacion: pd.DataFrame = self.df_celulares.merge(self.df_recaudacion, left_on="DEUDOR", right_on="SAP", how="left")
        df_cruce_recaudacion = df_cruce_recaudacion[["CELULAR", "NOMBRE", "TOTAL"]]
        df_cruce_recaudacion["TOTAL"].fillna(0, inplace=True)
        df_cruce_recaudacion = df_cruce_recaudacion.sort_values(by="TOTAL", ascending=True)
        df_cruce_recaudacion["TIPO"] = df_cruce_recaudacion["TOTAL"].apply(
            lambda x: "DISPONIBLE" if x > 0 else ("SIN_LINEA" if x == 0 else "SOBREGIRO"))
        df_cruce_recaudacion["TOTAL"] = df_cruce_recaudacion["TOTAL"].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        df_cruce_recaudacion.reset_index(drop=True, inplace=True)
        
        df_cruce_recaudacion["TEXTO"] = df_cruce_recaudacion.apply(self.generar_texto, axis=1)
        self.df_cruce_recaudacion: pd.DataFrame = df_cruce_recaudacion
        self.contador += 1
    
    def preparar_modelo(self) -> None:
        df_modelo: pd.DataFrame = pd.read_excel(self.ruta_modelo, sheet_name="Base")
        columnas_modelo: list[str] = ["DEUDOR", "NOMBRE", "LINEA DISPONIBLE EQUIPOS RESTANTE"]
        df_modelo = df_modelo[columnas_modelo]
        
        df_cruce_modelo: pd.DataFrame = self.df_celulares.merge(df_modelo, left_on="DEUDOR", right_on="DEUDOR", how="inner")
        df_cruce_modelo = df_cruce_modelo[["CELULAR", "NOMBRE_x", "LINEA DISPONIBLE EQUIPOS RESTANTE"]]
        df_cruce_modelo = df_cruce_modelo.rename(columns={"NOMBRE_x": "NOMBRE", "LINEA DISPONIBLE EQUIPOS RESTANTE": "TOTAL"})
        df_cruce_modelo = df_cruce_modelo.sort_values(by="TOTAL", ascending=True)
        df_cruce_modelo["TIPO"] = df_cruce_modelo["TOTAL"].apply(
            lambda x: "DISPONIBLE" if x > 0 else ("SIN_LINEA" if x == 0 else "SOBREGIRO"))
        df_cruce_modelo["TOTAL"] = df_cruce_modelo["TOTAL"].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        df_cruce_modelo.reset_index(drop=True, inplace=True)
        
        df_cruce_modelo["TEXTO"] = df_cruce_modelo.apply(self.generar_texto, axis=1)
        self.df_cruce_modelo: pd.DataFrame = df_cruce_modelo
        self.contador += 1
    
    def preparar_zfir60(self) -> None:
        df_zfir60: pd.DataFrame = pd.read_excel(self.ruta_zfir60, sheet_name="Sheet1")
        df_zfir60 = df_zfir60[["Cliente Pa", "Total Vencida"]]
        df_zfir60["Total Vencida"] = df_zfir60["Total Vencida"].clip(lower=0)
        df_zfir60 = df_zfir60.groupby("Cliente Pa")["Total Vencida"].sum().reset_index()
        
        df_cruce_zfir60: pd.DataFrame = self.df_celulares.merge(df_zfir60, left_on="DEUDOR", right_on="Cliente Pa", how="left")
        df_cruce_zfir60 = df_cruce_zfir60[["CELULAR", "Total Vencida"]]
        df_cruce_zfir60 = df_cruce_zfir60[df_cruce_zfir60["Total Vencida"] != 0]
        df_cruce_zfir60 = df_cruce_zfir60.sort_values(by="Total Vencida", ascending=False)
        df_cruce_zfir60["Total Vencida"] = df_cruce_zfir60["Total Vencida"].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        df_cruce_zfir60.reset_index(drop=True, inplace=True)
        
        df_cruce_zfir60["TEXTO"] = df_cruce_zfir60.apply(self.generar_texto, axis=1)
        self.df_cruce_zfir60: pd.DataFrame = df_cruce_zfir60
        self.contador = 0
    
    def return_resultados(self) -> list[int]:
        resultados: list[int] = [self.df_cruce_modelo.shape[0], self.df_cruce_recaudacion.shape[0], self.df_cruce_zfir60.shape[0]]
        return resultados
    
    def exportar_archivos_txt(self) -> list[str]:
        # Nivel 1
        lista_nivel_1: list[str] = self.df_cruce_zfir60["TEXTO"].to_list()
        with open(self.nivel_1_txt, "w") as f:
            for item in lista_nivel_1:
                f.write("%s\n" % item)
        # LD
        df_ld: pd.DataFrame = pd.concat([self.df_cruce_modelo, self.df_cruce_recaudacion], ignore_index=True)
        lista_ld: list[str] = df_ld["TEXTO"].to_list()
        with open(self.ld_txt, "w") as f:
            for item in lista_ld:
                f.write("%s\n" % item)
        # Resultados
        resultados: list[str] = [str(len(lista_nivel_1)), str(len(lista_ld))]
        return resultados
    
    def generar_apoyos(self) -> list[bool, int]:
        reporte: SMS_APOYO = SMS_APOYO(self.ruta_regla, self.ruta_dacxanalista, self.ruta_base_celulares, self.ruta_vacaciones, self.ruta_apoyos, self.apoyos_txt)
        apoyos: list[bool, int] = reporte.generar_sms()
        return apoyos