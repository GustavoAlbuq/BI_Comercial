from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg


RAIZ = Path(__file__).resolve().parent.parent
ORIGINAIS = RAIZ / "dados" / "originais"
TRATADOS = RAIZ / "dados" / "tratados"
TRATADOS.mkdir(parents=True, exist_ok=True)

ARQUIVO_SAIDA = TRATADOS / "fato_vendas_preparada.csv"


def ler_csv(nome):
    return pd.read_csv(
        ORIGINAIS / nome,
        sep=";",
        encoding="utf-8-sig",
    )


def carregar_mapa(cursor, tabela, coluna_origem, coluna_id):
    cursor.execute(
        f"SELECT {coluna_origem}, {coluna_id} FROM {tabela}"
    )
    return dict(cursor.fetchall())


def main():
    vendas = ler_csv("vendas_itens.csv")
    clientes = ler_csv("clientes.csv")
    produtos = ler_csv("produtos.csv")
    vendedores = ler_csv("vendedores.csv")

    print("Informe a senha do usuario postgres.")
    senha = getpass("Senha: ")

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

            mapa_clientes = carregar_mapa(
                cursor,
                "dim_cliente",
                "codigo_cliente_origem",
                "id_cliente",
            )

            mapa_produtos = carregar_mapa(
                cursor,
                "dim_produto",
                "codigo_produto_origem",
                "id_produto",
            )

            mapa_vendedores = carregar_mapa(
                cursor,
                "dim_vendedor",
                "codigo_vendedor_origem",
                "id_vendedor",
            )

            cursor.execute(
                "SELECT data_completa, id_data FROM dim_data"
            )
            mapa_datas = {
                pd.Timestamp(data).strftime("%Y-%m-%d"): id_data
                for data, id_data in cursor.fetchall()
            }

    # A conexao foi usada apenas para consultas.
    vendas["data_venda"] = pd.to_datetime(
        vendas["data_venda"],
        errors="raise",
    ).dt.strftime("%Y-%m-%d")

    vendas["id_cliente"] = vendas[
        "codigo_cliente_origem"
    ].map(mapa_clientes)

    vendas["id_produto"] = vendas[
        "codigo_produto_origem"
    ].map(mapa_produtos)

    vendas["id_vendedor"] = vendas[
        "codigo_vendedor_origem"
    ].map(mapa_vendedores)

    vendas["id_data"] = vendas[
        "data_venda"
    ].map(mapa_datas)

    chaves = [
        "id_cliente",
        "id_produto",
        "id_vendedor",
        "id_data",
    ]

    if vendas[chaves].isna().any().any():
        faltantes = vendas[chaves].isna().sum()
        raise ValueError(
            "Existem chaves sem correspondencia:\n"
            + faltantes.to_string()
        )

    # Selecionar somente as colunas necessárias para a fato.
    fato = vendas[[
        "id_venda",
        "id_cliente",
        "id_produto",
        "id_vendedor",
        "id_data",
        "quantidade",
        "preco_unitario",
        "desconto_valor",
        "custo_unitario",
    ]].copy()

    # Validar quantidades antes de salvar.
    if len(fato) != 11091:
        raise ValueError(
            f"Esperados 11091 itens; encontrados {len(fato)}."
        )

    if fato["id_venda"].nunique() != 6000:
        raise ValueError(
            "Quantidade inesperada de pedidos distintos."
        )

    fato.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    print("\nPREPARACAO CONCLUIDA")
    print(f"Banco consultado: {banco}")
    print(f"Itens preparados: {len(fato)}")
    print(f"Pedidos distintos: {fato['id_venda'].nunique()}")
    print(f"Chaves sem correspondencia: 0")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print("Nenhum dado foi inserido no PostgreSQL.")


if __name__ == "__main__":
    main()