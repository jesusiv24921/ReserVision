import os
import pandas as pd
import pyodbc

# Dirección de la base de datos y proyecto
basepath = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(basepath, '..'))
bd = os.path.join(project_root, 'data', 'input', 'proyecto.accdb')

class CargaDatos:
    """
    Clase encargada de gestionar la conexión con una base de datos Access y cargar datos de distintas tablas en DataFrames.
    """

    def __init__(self) -> None:
        """
        Constructor de la clase CargaDatos. Configura la cadena de conexión a la base de datos.
        """
        self.conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + bd + ';'
        )

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
            with pyodbc.connect(self.conn_str) as conn:
                query = f"SELECT * FROM {table_name}"
                df_total = pd.read_sql(query, conn)
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




