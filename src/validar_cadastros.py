from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados" / "originais"

arquivos = {
    "clientes": "clientes.csv",
    "produtos": "produtos.csv",
    "vendedores": "vendedores.csv",
}

for nome, arquivo in arquivos.items():
    caminho = PASTA_DADOS / arquivo
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")

    print(f"\n{'=' * 45}")
    print(f"ARQUIVO: {arquivo}")
    print(f"Quantidade de linhas: {len(df)}")
    print(f"Quantidade de colunas: {len(df.columns)}")
    print(f"Colunas: {list(df.columns)}")
    print(f"Linhas totalmente duplicadas: {df.duplicated().sum()}")
    print("\nValores ausentes por coluna:")
    print(df.isna().sum().to_string())
    print("\nPrimeiras 3 linhas:")
    print(df.head(3).to_string(index=False))

    coluna_codigo = {
        "clientes": "codigo_cliente_origem",
        "produtos": "codigo_produto_origem",
        "vendedores": "codigo_vendedor_origem",
    }[nome]

    print(
        f"\nCódigos duplicados: "
        f"{df[coluna_codigo].duplicated().sum()}"
    )

print("\nValidacao inicial concluida.")