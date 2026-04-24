from utils.ddl import create_tables
from utils.insert import connect_to_db, insert_star_schema
from utils.modeling import model_star_schema
from utils.reading import read_data
from utils.cleaning import clean_data

class DataPipeline:
    """Classe que representa a pipeline de dados para ler, modelar e inserir os dados no banco de dados PostgreSQL."""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def run(self):
        # Etapa 1: Leitura dos dados
        df = read_data(self.file_path)

        # Etapa 2: Limpeza dos dados
        df = clean_data(df)

        # Etapa 3: Modelagem do star schema
        star_schema = model_star_schema(df)

        # Etapa 4: Conexão com o banco de dados PostgreSQL
        engine = connect_to_db()

        # Etapa 5: Criação das tabelas no banco de dados
        create_tables(engine)

        # Etapa 6: Inserção dos dados no banco de dados
        insert_star_schema(star_schema, engine)


if __name__ == "__main__":
    file_path = "data/electronics_sales_raw.csv" 
    pipeline = DataPipeline(file_path)
    pipeline.run()