# Desafio 03 — Pipeline ETL de Vendas de Eletrônicos

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5%2B-yellow?logo=duckdb)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-orange?logo=tableau)

Projeto de Engenharia de Dados desenvolvido como parte do desafio da comunidade **[Dados por Todos](https://www.linkedin.com/company/dadosportodos/)**. O objetivo é construir um pipeline ETL completo — desde a ingestão de dados brutos em CSV até a modelagem analítica em star schema no PostgreSQL — gerando uma base sólida para análise no Tableau.

---

## Sobre o Projeto

O dataset contém **7.000 registros de vendas de eletrônicos** com 25 atributos por pedido, cobrindo informações de clientes, produtos, canais de venda, representantes comerciais e métricas financeiras.

O pipeline transforma esses dados brutos em um **star schema** pronto para análise, respondendo perguntas de negócio como:

- Qual canal de vendas gera maior receita líquida?
- Qual região tem melhor desempenho por representante?
- Como o desconto impacta o faturamento por categoria?
- Quais clientes têm maior risco de churn?
- Qual a tendência de vendas por mês, trimestre e ano?

---

## Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.13 | Orquestração do pipeline |
| Pandas | ≥ 3.0 | Extração e manipulação de dados |
| DuckDB | ≥ 1.5 | Transformação SQL em memória |
| Pydantic | ≥ 2.13 | Validação de dados |
| SQLAlchemy | ≥ 2.0 | DDL e conexão com PostgreSQL |
| Loguru | ≥ 0.7 | Logging estruturado |
| PostgreSQL | 17 | Banco de dados analítico (via Docker) |
| Tableau | — | Visualização e dashboard |
| uv | — | Gerenciador de dependências |

---

## Arquitetura do Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐     ┌────────────────────┐     ┌───────────┐
│  CSV Bruto  │────▶│   Extract    │────▶│  Clean & Validate   │────▶│  Transform (DuckDB)│────▶│  Load     │
│             │     │ (pandas)     │     │  (Pydantic)         │     │  Star Schema       │     │ PostgreSQL│
└─────────────┘     └──────────────┘     └─────────────────────┘     └────────────────────┘     └─────┬─────┘
                                                                                                        │
                                                                                               ┌────────▼──────┐
                                                                                               │    Tableau    │
                                                                                               │   Dashboard   │
                                                                                               └───────────────┘
```

### Etapas do Pipeline

| Etapa | Arquivo | Descrição |
|---|---|---|
| **Extract** | `src/utils/reading.py` | Leitura do CSV com pandas |
| **Clean** | `src/utils/cleaning.py` | Remoção de duplicatas por `order_id`, strip de strings |
| **Validate** | `src/utils/models.py` | Validação linha a linha com Pydantic: tipos, nulos, negativos, consistência de datas |
| **Transform** | `src/utils/modeling.py` | Criação do star schema via SQL no DuckDB (em memória) |
| **Load DDL** | `src/utils/ddl.py` | Definição e criação das tabelas no PostgreSQL via SQLAlchemy |
| **Load Data** | `src/utils/insert.py` | Inserção dos dados com truncate → insert, em ordem de dependência |
| **Orquestração** | `src/main.py` | Classe `DataPipeline` que executa todas as etapas em sequência |

---

## Modelagem — Star Schema

```
                        ┌──────────────────┐
                        │   dim_customer   │
                        │──────────────────│
                        │ customer_id (PK) │
                        │ customer_name    │
                        │ customer_segment │
                        │ first_purchase   │
                        │ last_purchase    │
                        │ monthly_burn     │
                        │ churn_flag       │
                        └────────┬─────────┘
                                 │
┌──────────────────┐    ┌────────▼─────────────────────────────────┐    ┌──────────────────┐
│   dim_product    │    │               fact_sales                 │    │   dim_channel    │
│──────────────────│    │──────────────────────────────────────────│    │──────────────────│
│ product_id  (PK) │◀───│ order_id          (PK)                   │───▶│ channel_id  (PK) │
│ product_name     │    │ customer_id       (FK → dim_customer)    │    │ sales_channel    │
│ category         │    │ product_id        (FK → dim_product)     │    │ payment_method   │
│ sub_category     │    │ channel_id        (FK → dim_channel)     │    └──────────────────┘
│ brand            │    │ sales_rep_id      (FK → dim_sales_rep)   │
└──────────────────┘    │ region_id         (FK → dim_region)      │    ┌──────────────────┐
                        │ date_id           (FK → dim_date)        │───▶│  dim_sales_rep   │
┌──────────────────┐    │ quantity                                  │    │──────────────────│
│    dim_region    │    │ unit_price                                │    │ sales_rep_id (PK)│
│──────────────────│    │ discount_pct                              │    │ sales_rep        │
│ region_id   (PK) │◀───│ gross_amount  = unit_price × qty         │    └──────────────────┘
│ region           │    │ net_amount    = gross × (1 - discount)   │
└──────────────────┘    │ operating_expenses                        │    ┌──────────────────┐
                        │ cash_balance                              │    │    dim_date      │
                        │ debt_balance                              │───▶│──────────────────│
                        │ customer_type                             │    │ date_id     (PK) │
                        └──────────────────────────────────────────┘    │ year             │
                                                                         │ quarter          │
                                                                         │ month            │
                                                                         │ day              │
                                                                         │ day_of_week      │
                                                                         │ day_name         │
                                                                         │ month_name       │
                                                                         └──────────────────┘
```

---

## Estrutura do Projeto

```
desafio-03-dpt/
├── data/
│   └── electronics_sales_raw.csv   # Dataset bruto (7.000 linhas × 25 colunas)
├── notebook/
│   └── Analise_Exploratoria.ipynb  # Análise exploratória dos dados
├── src/
│   ├── main.py                     # Orquestrador do pipeline (classe DataPipeline)
│   └── utils/
│       ├── reading.py              # Etapa Extract: leitura do CSV
│       ├── cleaning.py             # Etapa Clean: deduplicação e validação
│       ├── models.py               # Schema Pydantic para validação
│       ├── modeling.py             # Etapa Transform: star schema via DuckDB
│       ├── ddl.py                  # Etapa Load DDL: definição das tabelas
│       └── insert.py               # Etapa Load: inserção no PostgreSQL
├── .env_example                    # Template de variáveis de ambiente
├── docker-compose.yml              # Serviço PostgreSQL 17
├── pyproject.toml                  # Dependências do projeto
└── README.md
```

---

## Como Executar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- [uv](https://docs.astral.sh/uv/) (recomendado) ou pip
- Python 3.13+

### Passo a passo

**1. Clone o repositório**

```bash
git clone https://github.com/<seu-usuario>/desafio-03-dpt.git
cd desafio-03-dpt
```

**2. Configure as variáveis de ambiente**

```bash
cp .env_example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=nome_do_banco
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**3. Suba o PostgreSQL com Docker**

```bash
docker compose up -d
```

**4. Instale as dependências**

```bash
# Com uv (recomendado)
uv sync

# Ou com pip
pip install -e .
```

**5. Execute o pipeline**

```bash
python src/main.py
```

O pipeline irá:
1. Ler o CSV em `data/electronics_sales_raw.csv`
2. Limpar e validar os dados
3. Modelar o star schema com DuckDB
4. Criar as tabelas no PostgreSQL
5. Inserir todos os dados

---

## Análise Exploratória

O notebook [`notebook/Analise_Exploratoria.ipynb`](notebook/Analise_Exploratoria.ipynb) contém a análise exploratória inicial do dataset, incluindo distribuições, valores nulos, outliers e correlações entre variáveis.

```bash
# Para abrir o notebook
jupyter notebook notebook/Analise_Exploratoria.ipynb
```

---

## Checklist do Desafio

- [x] Estudo preliminar e entendimento do projeto
- [x] Definição do fluxo do pipeline: CSV → tratamento → modelagem → saída para o dashboard
- [x] Identificação das perguntas de negócio
- [x] Extração: leitura do arquivo `.csv` para um DataFrame
- [x] Validação de consistência entre colunas numéricas (quantidade, valor unitário, desconto)
- [x] Padronização de tipos de dados (datas → `datetime`, monetários → `float`)
- [x] Limpeza: remoção de espaços extras, registros duplicados e inválidos
- [x] Modelagem analítica (star schema) com DuckDB + carga no PostgreSQL
- [ ] Dashboard no Tableau
- [ ] Post no LinkedIn marcando @dadosportodos, @vbluuiza e @lauraalmeidaaa
- [ ] Formulário de conclusão

---

## Comunidade

Este projeto faz parte do ecossistema **[Dados por Todos](https://www.linkedin.com/company/dadosportodos/)** — uma comunidade criada para aprender junto: construir, testar, trocar ideias e evoluir em conjunto.
