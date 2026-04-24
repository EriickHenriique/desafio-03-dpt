import pandas as pd

def read_data(file_path):
    """Lê os dados do arquivo CSV e retorna um DataFrame."""
    # Leitura do arquivo CSV usando pandas
    df = pd.read_csv(file_path)    
 
    return df