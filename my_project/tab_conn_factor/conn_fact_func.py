import plotly.graph_objs as go

def normalize_column_by_group(df, group_col, value_col):
    """
    Normaliza una columna por grupo dentro de un DataFrame. 
    Cada grupo se normaliza de forma independiente entre 0 y 1.
    
    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos a normalizar.
        group_col (str): La columna que define los grupos (por ejemplo, 'IDENTIFICADOR').
        value_col (str): La columna de valores que se desea normalizar.
    
    Returns:
        pd.DataFrame: El DataFrame con la columna normalizada añadida.
    """
    df[value_col + '_norm'] = df.groupby(group_col)[value_col].transform(
        lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0
    )
    return df