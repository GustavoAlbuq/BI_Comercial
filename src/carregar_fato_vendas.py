from getpass import getpass
from pathlib import Path
from decimal import Decimal

import pandas as pd
import psycopg


RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO = RAIZ / "dados" / "tratados" / "fato_vendas_preparada.csv"

ESPERADO_ITENS = 11091
ESPERADO_PEDIDOS = 6000


def main():
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {ARQUIVO}"
        )

    df = pd.read_csv(
        ARQUIVO,
        sep=";",
        encoding="utf-8-sig",
        dtype={"id_venda": str},
    )

    if len(df) != ESPERADO_ITENS:
        raise ValueError(
            f"Esperados {ESPERADO_ITENS} itens; "
            f"encontrados {len(df)}."
        )

    if df["id_venda"].nunique() != ESPERADO_PEDIDOS:
        raise ValueError(
            f"Esperados {ESPERADO_PEDIDOS} pedidos."
        )

    colunas_chave = [
        "id_cliente",
        "id_produto",
        "id_vendedor",
        "id_data",
    ]

    if df[colunas_chave].isna().any().any():
        raise ValueError("Existem chaves estrangeiras vazias.")

    if (df["quantidade"] <= 0).any():
        raise ValueError("Existem quantidades invalidas.")

    for coluna in [
        "preco_unitario",
        "desconto_valor",
        "custo_unitario",
    ]:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="raise",
        )

    if (
        df["desconto_valor"]
        > df["quantidade"] * df["preco_unitario"]
    ).any():
        raise ValueError("Existem descontos acima do subtotal.")

    senha = getpass("Senha do usuario postgres: ")

    sql = """
        INSERT INTO fato_vendas (
            id_venda,
            id_cliente,
            id_produto,
            id_vendedor,
            id_data,
            quantidade,
            preco_unitario,
            desconto_valor,
            custo_unitario
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    print("Conectando ao banco bi_comercial...")

    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="bi_comercial",
        user="postgres",
        password=senha,
        connect_timeout=5,
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            banco = cursor.fetchone()[0]

            if banco != "bi_comercial":
                raise RuntimeError(
                    f"Banco inesperado: {banco}"
                )

            cursor.execute(
                "SELECT COUNT(*) FROM fato_vendas"
            )
            atual = cursor.fetchone()[0]

            if atual != 0:
                raise RuntimeError(
                    f"fato_vendas ja possui {atual} registros. "
                    "Carga cancelada para evitar duplicacao."
                )

            # Confirmar que todas as chaves existem no banco.
            verificacoes = [
                ("dim_cliente", "id_cliente", "id_cliente"),
                ("dim_produto", "id_produto", "id_produto"),
                ("dim_vendedor", "id_vendedor", "id_vendedor"),
                ("dim_data", "id_data", "id_data"),
            ]

            for tabela, coluna, coluna_df in verificacoes:
                cursor.execute(
                    f"SELECT {coluna} FROM {tabela}"
                )
                ids_validos = {
                    linha[0] for linha in cursor.fetchall()
                }
                ids_usados = set(df[coluna_df].astype(int))

                if not ids_usados.issubset(ids_validos):
                    raise ValueError(
                        f"Chaves invalidas para {tabela}."
                    )

            registros = []

            for linha in df.itertuples(index=False):
                registros.append((
                    str(linha.id_venda),
                    int(linha.id_cliente),
                    int(linha.id_produto),
                    int(linha.id_vendedor),
                    int(linha.id_data),
                    int(linha.quantidade),
                    Decimal(str(linha.preco_unitario)),
                    Decimal(str(linha.desconto_valor)),
                    Decimal(str(linha.custo_unitario)),
                ))

            cursor.executemany(sql, registros)

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT id_venda)
                FROM fato_vendas
                """
            )
            total_itens, total_pedidos = cursor.fetchone()

            if total_itens != ESPERADO_ITENS:
                raise RuntimeError(
                    f"Total inesperado de itens: {total_itens}"
                )

            if total_pedidos != ESPERADO_PEDIDOS:
                raise RuntimeError(
                    f"Total inesperado de pedidos: {total_pedidos}"
                )

    print("\nCARGA CONCLUIDA E VALIDADA!")
    print(f"Itens carregados: {ESPERADO_ITENS}")
    print(f"Pedidos distintos: {ESPERADO_PEDIDOS}")
    print("As colunas calculadas serao geradas pelo PostgreSQL.")


if __name__ == "__main__":
    main()