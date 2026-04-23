import pandas as pd

def process_data(file_path):
    """Processa os dados do arquivo CSV e retorna um DataFrame."""
    # Leitura do arquivo CSV usando pandas
    df = pd.read_csv(file_path)    
 
    return df