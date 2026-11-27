import os
import pandas as pd

def cargar_perfiles_w():
    """
    Carga el archivo CSV con la base de datos de perfiles W comerciales.
    """
    ruta_csv = os.path.join("data", "perfiles_w.csv")
    if os.path.exists(ruta_csv):
        df = pd.read_csv(ruta_csv)
        return df
    else:
        # DataFrame vacío por defecto si el archivo no se encuentra
        return pd.DataFrame(columns=["perfil", "Ag", "d", "tw", "bf", "tf", "rx", "ry", "Zx", "Sx"])