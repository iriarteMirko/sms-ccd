from datetime import datetime
import pandas as pd


class SMS_APOYO():
    def __init__(
        self, 
        ruta_regla: str, 
        ruta_dacxanalista: str, 
        ruta_base_celulares: str, 
        ruta_vacaciones: str, 
        ruta_apoyos: str, 
        apoyos_txt: str
        ) -> None:
        self.fecha_hoy: str = datetime.now().strftime("%d.%m.%Y")
        self.ruta_regla: str = ruta_regla
        self.ruta_dacxanalista: str = ruta_dacxanalista
        self.ruta_celulares: str = ruta_base_celulares
        self.ruta_vacaciones: str = ruta_vacaciones
        self.ruta_apoyos: str = ruta_apoyos
        self.apoyos_txt: str = apoyos_txt
    
    def depurar_dacx(self) -> None:
        columnas: list[str] = ["DEUDOR", "NOMBRE", "RUC", "ANALISTA_ACT", "TIPO_DAC", "ESTADO"]
        no_analistas: list[str] = ["REGION NORTE", "REGION SUR", "WALTER LOPEZ", "SIN INFORMACION"]
        no_estados: list[str] = ["LIQUIDADO", "PROCESO DE LIQUIDACIÓN"]
        
        df_dacx: pd.DataFrame = pd.read_excel(self.ruta_dacxanalista, sheet_name="Base_NUEVA", usecols=columnas)
        df_dacx = df_dacx.rename(columns={"ANALISTA_ACT": "ANALISTA", "TIPO_DAC": "TIPO"})
        df_dacx = df_dacx[~df_dacx["ANALISTA"].isin(no_analistas) & ~df_dacx["ESTADO"].isin(no_estados)]
        df_dacx["DEUDOR"] = df_dacx["DEUDOR"].astype("Int64").astype(str)
        df_dacx["RUC"] = df_dacx["RUC"].astype("Int64").astype(str)
        df_dacx.dropna(subset=["DEUDOR"], inplace=True)
        df_dacx.drop_duplicates(subset=["DEUDOR"], inplace=True)
        df_dacx.reset_index(drop=True, inplace=True)
        self.df_dacx: pd.DataFrame = df_dacx
        self.list_analistas: list[str] = df_dacx["ANALISTA"].unique()
    
    def actualizar_apoyos(self) -> None:
        df_apoyos: pd.DataFrame = pd.read_excel(self.ruta_apoyos, sheet_name="GENERAL", usecols=["DEUDOR", "APOYO1", "APOYO2", "APOYO3"])
        df_apoyos["DEUDOR"] = df_apoyos["DEUDOR"].astype("Int64").astype(str)
        df_apoyos: pd.DataFrame = pd.merge(df_apoyos, self.df_dacx, on="DEUDOR", how="right")
        df_apoyos = df_apoyos[["DEUDOR", "NOMBRE", "ANALISTA", "APOYO1", "APOYO2", "APOYO3", "ESTADO", "TIPO"]]
        df_apoyos.dropna(subset=["DEUDOR"], inplace=True)
        df_apoyos.drop_duplicates(subset=["DEUDOR"], inplace=True)
        df_apoyos.sort_values(by="DEUDOR", inplace=True, ignore_index=True)
        df_apoyos.reset_index(drop=True, inplace=True)
        df_apoyos.to_excel(self.ruta_apoyos, sheet_name="GENERAL", index=False)
        
        with pd.ExcelWriter(self.ruta_apoyos) as writer:
            df_temp: pd.DataFrame = df_apoyos.copy()
            df_apoyos.to_excel(writer, sheet_name="GENERAL", index=False)
            for analista in self.list_analistas:
                df_apoyos = df_temp[df_temp["ANALISTA"] == analista]
                df_apoyos.sort_values(by="DEUDOR", inplace=True, ignore_index=True)
                df_apoyos.reset_index(drop=True, inplace=True)
                df_apoyos.to_excel(writer, sheet_name=analista, index=False)
    
    def depurar_celulares(self) -> None:
        df_celulares: pd.DataFrame = pd.read_excel(self.ruta_celulares)
        df_celulares["DEUDOR"] = df_celulares["DEUDOR"].astype("Int64").astype(str)
        df_celulares["CELULAR"] = df_celulares["CELULAR"].astype("Int64").astype(str)
        df_celulares = df_celulares[["DEUDOR", "CELULAR"]]
        df_celulares["CELULAR"] = df_celulares[df_celulares["CELULAR"].str.len() == 9]["CELULAR"]
        df_celulares.dropna(subset=["CELULAR"], inplace=True)
        df_celulares["CELULAR"] = "51" + df_celulares["CELULAR"]
        df_celulares.reset_index(drop=True, inplace=True)
        self.df_celulares: pd.DataFrame = df_celulares
    
    def cruzar_data(self) -> None:
        df_apoyos: pd.DataFrame = pd.read_excel(self.ruta_apoyos, sheet_name="GENERAL", usecols=["DEUDOR", "ANALISTA", "APOYO1", "APOYO2", "APOYO3"])
        df_apoyos["DEUDOR"] = df_apoyos["DEUDOR"].astype("Int64").astype(str)
        df_cruce: pd.DataFrame = pd.merge(self.df_celulares, df_apoyos, on="DEUDOR", how="left")
        df_cruce.dropna(subset=["ANALISTA","CELULAR"], inplace=True)
        df_cruce.reset_index(drop=True, inplace=True)
        self.df_cruce: pd.DataFrame = df_cruce
    
    def obtener_texto(self) -> None:
        df_texto: pd.DataFrame = pd.read_excel(self.ruta_regla, sheet_name="TEXTO_APOYO")
        self.texto1: str = df_texto["TEXTO"][0]
        self.texto2: str = df_texto["TEXTO"][1]
        self.texto3: str = df_texto["TEXTO"][2]
        self.texto4: str = df_texto["TEXTO"][3]
    
    def formato_fecha(self, fecha: str) -> datetime:
        fecha_formato: datetime = datetime.strptime(fecha, "%d.%m.%Y")
        return fecha_formato
    
    def generar_texto(self, analistas: list[str], vacaciones: dict[str, str]) -> None:
        self.df_cruce = self.df_cruce[self.df_cruce["ANALISTA"].isin(analistas)]
        self.df_cruce["FECHA_RETORNO"] = self.df_cruce["ANALISTA"].map(vacaciones)
        self.df_cruce["APOYO"] = self.df_cruce[["APOYO1", "APOYO2", "APOYO3"]].apply(
            lambda x: x[0] if x[0] not in (analistas) 
            else (x[1] if x[1] not in (analistas) else x[2]), axis=1)
        self.df_cruce["FECHA_RETORNO"] = self.df_cruce["FECHA_RETORNO"].str.replace(".", "/")
        self.df_cruce.reset_index(drop=True, inplace=True)
        self.df_cruce = self.df_cruce[["CELULAR", "ANALISTA", "FECHA_RETORNO","APOYO"]]
        self.df_cruce["TEXTO"] = self.df_cruce.apply(lambda row: f'{row["CELULAR"]}{self.texto1}{row["ANALISTA"]}{self.texto2}{row["FECHA_RETORNO"]}{self.texto3}{row["APOYO"]}{self.texto4}', axis=1)
        self.lista_apoyos: list[str] = self.df_cruce["TEXTO"].to_list()
    
    def exportar_txt(self) -> None:
        with open(self.apoyos_txt, "w") as f:
            for item in self.lista_apoyos:
                f.write("%s\n" % item)
    
    def generar_sms(self) -> list[bool, int]:
        df_vacaciones: pd.DataFrame = pd.read_excel(self.ruta_vacaciones, sheet_name="VACACIONES")
        df_vacaciones.dropna(inplace=True)
        
        dict_analistas: dict[str, list[str]] = df_vacaciones.set_index("ANALISTA").T.to_dict("list")
        vacaciones: dict[str, str] = {}
        
        for analista, fechas in dict_analistas.items():
            if self.formato_fecha(fechas[0]) <= self.formato_fecha(self.fecha_hoy) <= self.formato_fecha(fechas[1]):
                vacaciones.update({analista: fechas[1]})
        
        if vacaciones == {}:
            return [False, 0]
        else:
            analistas: list[str] = list(vacaciones.keys())
            self.depurar_dacx()
            self.actualizar_apoyos()
            self.depurar_celulares()
            self.cruzar_data()
            self.obtener_texto()
            self.generar_texto(analistas, vacaciones)
            self.exportar_txt()
            return [True, len(self.lista_apoyos)]