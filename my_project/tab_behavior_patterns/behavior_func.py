import pandas as pd

class SeleccionarPruebas:
    """
    Clase que proporciona métodos estáticos para seleccionar la última prueba o Pwf por mes de un DataFrame,
    en función de una fecha seleccionada.
    """

    @staticmethod
    def seleccionar_ultima_prueba_por_mes(df, fecha_seleccionada):
        """
        Selecciona la última prueba disponible por pozo para un mes determinado en función de la fecha seleccionada.

        La función filtra las pruebas anteriores o iguales a la fecha seleccionada y devuelve la última prueba disponible 
        para cada pozo. Si no se proporciona una fecha, se utilizará una fecha por defecto.

        Args:
            df (pd.DataFrame): DataFrame que contiene las pruebas, con las columnas 'IDENTIFICADOR' y 'FECHA'.
            fecha_seleccionada (pd.Timestamp or str): Fecha seleccionada como referencia para filtrar las pruebas.

        Returns:
            pd.DataFrame: DataFrame que contiene la última prueba disponible por pozo.
        """
        resultados = []

        # Verificar si la fecha seleccionada es None y asignar una fecha por defecto
        if fecha_seleccionada is None:
            fecha_seleccionada = pd.Timestamp('2024-01-01')

        # Asegurarse de que la fecha seleccionada esté en formato datetime
        fecha_seleccionada = pd.to_datetime(fecha_seleccionada) + pd.offsets.MonthEnd(0)

        # Obtener la lista de pozos únicos en el DataFrame
        pozos_unicos = df['IDENTIFICADOR'].unique()

        # Iterar sobre cada pozo para seleccionar la última prueba por mes
        for pozo in pozos_unicos:
            df_pozo = df[df['IDENTIFICADOR'] == pozo]
            df_filtrado = df_pozo[df_pozo['FECHA'] <= fecha_seleccionada]

            # Seleccionar la última prueba disponible si existe
            if not df_filtrado.empty:
                ultima_prueba = df_filtrado.sort_values(by='FECHA', ascending=False).iloc[0]
                resultados.append(ultima_prueba)

        # Retornar el resultado en formato de DataFrame
        return pd.DataFrame(resultados)

    @staticmethod
    def seleccionar_ultima_pwf_por_mes(df, fecha_seleccionada):
        """
        Selecciona el último valor de Pwf disponible por pozo para un mes determinado en función de la fecha seleccionada.

        La función filtra las pruebas anteriores o iguales a la fecha seleccionada y devuelve el último Pwf disponible 
        para cada pozo. Si no se proporciona una fecha, se utilizará una fecha por defecto.

        Args:
            df (pd.DataFrame): DataFrame que contiene las pruebas de Pwf, con las columnas 'pozo' y 'fecha'.
            fecha_seleccionada (pd.Timestamp or str): Fecha seleccionada como referencia para filtrar las pruebas de Pwf.

        Returns:
            pd.DataFrame: DataFrame que contiene el último valor de Pwf disponible por pozo.
        """
        resultados = []

        # Verificar si la fecha seleccionada es None y asignar una fecha por defecto
        if fecha_seleccionada is None:
            fecha_seleccionada = pd.Timestamp('2024-01-01')

        # Asegurarse de que la fecha seleccionada esté en formato datetime
        fecha_seleccionada = pd.to_datetime(fecha_seleccionada) + pd.offsets.MonthEnd(0)

        # Obtener la lista de pozos únicos en el DataFrame
        pozos_unicos = df['pozo'].unique()

        # Iterar sobre cada pozo para seleccionar el último Pwf por mes
        for pozo in pozos_unicos:
            df_pozo = df[df['pozo'] == pozo]
            df_filtrado = df_pozo[df_pozo['fecha'] <= fecha_seleccionada]

            # Seleccionar el último Pwf disponible si existe
            if not df_filtrado.empty:
                ultima_pwf = df_filtrado.sort_values(by='fecha', ascending=False).iloc[0]
                resultados.append(ultima_pwf)

        # Retornar el resultado en formato de DataFrame
        return pd.DataFrame(resultados)

