import os
import pandas as pd
from sqlalchemy import create_engine

# Conexión a PostgreSQL en Heroku
DATABASE_URL = "postgresql://ua6siia5pprrj4:pcff596760bbde68775ea4a456382c0deed86e209c4ec8d95558c8589cf64a722@ceqbglof0h8enj.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d16ctrn3e0v21m"
engine = create_engine(DATABASE_URL)

class CargaDatos:
    """
    Clase encargada de gestionar la conexión con una base de datos PostgreSQL y cargar datos de distintas tablas en DataFrames.
    """

    def __init__(self) -> None:
        """
        Constructor de la clase CargaDatos. Configura la conexión a la base de datos PostgreSQL.
        """
        self.engine = engine

    def carga_function(self, table_name: str) -> pd.DataFrame:
        """
        Carga los datos de la tabla especificada en un DataFrame de pandas.

        Parámetros:
        -----------
        table_name : str
            Nombre de la tabla que se desea cargar.

        Retorna:
        --------
        pd.DataFrame
            DataFrame que contiene los datos de la tabla.
        """
        try:
            query = f"SELECT * FROM {table_name}"
            df_total = pd.read_sql(query, self.engine)
            
            # Convertir la columna 'fecha' a datetime si la tabla es 'pwf' para asegurar comparaciones correctas
            if table_name == 'pwf' and 'fecha' in df_total.columns:
                df_total['fecha'] = pd.to_datetime(df_total['fecha'], errors='coerce')

        except Exception as e:
            print(f"Error al cargar los datos de la tabla {table_name}: {e}")
            return pd.DataFrame()

        return df_total

    def data_cargar(self, data: str) -> pd.DataFrame:
        """
        Devuelve un DataFrame con los datos de la tabla solicitada según el parámetro `data`.

        Parámetros:
        -----------
        data : str
            Nombre de la tabla cuyos datos se desean cargar.

        Retorna:
        --------
        pd.DataFrame
            DataFrame que contiene los datos de la tabla.
        """
        tablas = {
            'controles_diarios': 'controles_diarios',
            'coordenadas': 'coordenadas',
            'data_estatica': 'data_estatica',
            'kr': 'kr',
            'pip': 'pip',
            'produccion_mes': 'produccion_mes',
            'pwf': 'pwf',
            'relacion_iny_prod': 'relacion_iny_prod',
            'inyeccion_diaria': 'inyeccion_diaria'
        }

        if data in tablas:
            return self.carga_function(tablas[data])
        else:
            print(f"Error: La tabla {data} no está disponible.")
            return pd.DataFrame()



# cargador = CargaDatos()

# df_controles_diarios = cargador.data_cargar("pwf")

# print("Datos de 'controles_diarios':")
# print(df_controles_diarios.head())
