import pandas as pd
from .models import SalesData
from loguru import logger

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa os dados do DataFrame, removendo linhas com valores ausentes e duplicadas"""
    
    # Verifica e remove linhas duplicadas com base em 'order_id'
    duplicated_rows = df.duplicated(subset=['order_id'], keep=False).sum()
    if duplicated_rows > 0:
        logger.warning(f"Atenção: Existem {duplicated_rows} linhas duplicadas com base em 'order_id'.")
        df = df.drop_duplicates(subset=["order_id"], keep="first")
        logger.info(f"Linhas duplicadas removidas. Total de linhas após limpeza: {len(df)}")
    else:
        logger.info("Nenhuma linha duplicada encontrada com base em 'order_id'.")
    
    df['order_id'] = df['order_id'].astype(str)
    
    valid_rows = []
    error_count = 0

    # Valida cada linha do DataFrame usando o modelo SalesData
    for index, row in df.iterrows():
        try:
            # Valida a linha usando o modelo SalesData
            validated_row = SalesData(**row.to_dict())
            valid_rows.append(validated_row)
        except Exception as e:
            logger.error(f"Erro ao validar linha {index}: {e}")
            error_count += 1

    if error_count > 0:
        logger.warning(f"Foram encontrados {error_count} erros de validação.")

    return pd.DataFrame([row.model_dump() for row in valid_rows])

