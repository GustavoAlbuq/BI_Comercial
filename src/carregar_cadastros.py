from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg


RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados" / "originais"

ARQUIVOS = {
    "clientes": PASTA_DADOS / "clientes.csv",
    "produtos": PASTA_DADOS / "produtos.csv",
    "vendedores": PASTA_DADOS / "vendedores.csv",
}

ESPERADOS = {
    "dim_cliente": 300,
    "dim_produto": 60,
    "dim_vendedor": 5,
}


def ler_csv(caminho):
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    return pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
    )


def main():
    # Ler e validar os arquivos antes de abrir a transacao.
    clientes = ler_csv(ARQUIVOS["clientes"])
    produtos = ler_csv(ARQUIVOS["produtos"])
    vendedores = ler_csv(ARQUIVOS["vendedores"])

    dados = [
        ("clientes", clientes, 300),
        ("produtos", produtos, 60),
        ("vendedores", vendedores, 5),
    ]

    for nome, df, quantidade in dados:
        if len(df) != quantidade:
            raise ValueError(
                f"{nome}: esperados {quantidade} registros, "
                f"encontrados {len(df)}."
            )

        if df.isna().any().any():
            raise ValueError(
                f"{nome}: existem valores ausentes."
            )

    # Converter datas para o tipo date do Python.
    clientes["data_cadastro"] = pd.to_datetime(
        clientes["data_cadastro"],
        errors="raise",
    ).dt.date

    vendedores["data_admissao"] = pd.to_datetime(
        vendedores["data_admissao"],
        errors="raise",
    ).dt.date

    senha = getpass("Senha do usuario postgres: ")

    comandos = {
        "dim_cliente": (
            """
            INSERT INTO dim_cliente (
                codigo_cliente_origem,
                nome_cliente,
                cidade,
                data_cadastro,
                status_cliente
            ) VALUES (
                %(codigo_cliente_origem)s,
                %(nome_cliente)s,
                %(cidade)s,
                %(data_cadastro)s,
                %(status_cliente)s
            )
            """,
            clientes,
        ),
        "dim_produto": (
            """
            INSERT INTO dim_produto (
                codigo_produto_origem,
                nome_produto,
                categoria,
                marca,
                tamanho
            ) VALUES (
                %(codigo_produto_origem)s,
                %(nome_produto)s,
                %(categoria)s,
                %(marca)s,
                %(tamanho)s
            )
            """,
            produtos,
        ),
        "dim_vendedor": (
            """
            INSERT INTO dim_vendedor (
                codigo_vendedor_origem,
                nome_vendedor,
                data_admissao,
                status_vendedor
            ) VALUES (
                %(codigo_vendedor_origem)s,
                %(nome_vendedor)s,
                %(data_admissao)s,
                %(status_vendedor)s
            )
            """,
            vendedores,
        ),
    }

    print("\nConectando ao banco bi_comercial...")

    # A transacao so confirma as insercoes se tudo der certo.
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="bi_comercial",
        user="postgres",
        password=senha,
        connect_timeout=5,
    ) as conexao:

        with conexao.cursor() as cursor:

            # Protecao contra carga duplicada ou banco inesperado.
            cursor.execute("SELECT current_database()")
            banco = cursor.fetchone()[0]

            if banco != "bi_comercial":
                raise RuntimeError(
                    f"Banco incorreto: {banco}"
                )

            for tabela, esperado in ESPERADOS.items():
                cursor.execute(
                    f"SELECT COUNT(*) FROM {tabela}"
                )
                atual = cursor.fetchone()[0]

                if atual != 0:
                    raise RuntimeError(
                        f"{tabela} ja possui {atual} registros. "
                        "Carga cancelada para evitar duplicacao."
                    )

            # Inserir os registros em cada dimensao.
            for tabela, (sql, df) in comandos.items():
                cursor.executemany(
                    sql,
                    df.to_dict(orient="records"),
                )
                print(
                    f"Inseridos em {tabela}: {len(df)}"
                )

            # Conferir as quantidades dentro da transacao.
            for tabela, esperado in ESPERADOS.items():
                cursor.execute(
                    f"SELECT COUNT(*) FROM {tabela}"
                )
                atual = cursor.fetchone()[0]

                if atual != esperado:
                    raise RuntimeError(
                        f"Validacao falhou em {tabela}: "
                        f"esperados {esperado}, encontrados {atual}."
                    )

    # Chegando aqui, a transacao foi confirmada.
    print("\nCarga concluida e validada!")
    print("Banco: bi_comercial")
    print("dim_cliente: 300 registros")
    print("dim_produto: 60 registros")
    print("dim_vendedor: 5 registros")


if __name__ == "__main__":
    main()