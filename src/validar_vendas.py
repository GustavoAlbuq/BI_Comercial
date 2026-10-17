from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados" / "originais"


def ler_csv(nome):
    return pd.read_csv(
        DADOS / nome,
        sep=";",
        encoding="utf-8-sig",
    )


vendas = ler_csv("vendas_itens.csv")
clientes = ler_csv("clientes.csv")
produtos = ler_csv("produtos.csv")
vendedores = ler_csv("vendedores.csv")

# Converter tipos para validacao.
vendas["data_venda"] = pd.to_datetime(
    vendas["data_venda"],
    errors="raise",
)

vendas["quantidade"] = pd.to_numeric(
    vendas["quantidade"],
    errors="raise",
)

for coluna in [
    "preco_unitario",
    "desconto_valor",
    "custo_unitario",
]:
    vendas[coluna] = pd.to_numeric(
        vendas[coluna],
        errors="raise",
    )

erros = []

# 1. Volume e granularidade.
if vendas["id_venda"].nunique() != 6000:
    erros.append("Quantidade de pedidos diferente de 6.000.")

if vendas.duplicated().any():
    erros.append("Existem linhas integralmente duplicadas.")

if vendas.duplicated(["id_venda", "codigo_produto_origem"]).any():
    erros.append("Existe produto repetido no mesmo pedido.")

# 2. Periodo historico.
if not vendas["data_venda"].between(
    "2024-01-01", "2025-12-31"
).all():
    erros.append("Existem datas fora do periodo.")

# 3. Integridade referencial pelos codigos de origem.
referencias = [
    (
        "codigo_cliente_origem",
        clientes,
        "Clientes",
    ),
    (
        "codigo_produto_origem",
        produtos,
        "Produtos",
    ),
    (
        "codigo_vendedor_origem",
        vendedores,
        "Vendedores",
    ),
]

for coluna, cadastro, nome in referencias:
    codigos_validos = set(cadastro[coluna])
    codigos_usados = set(vendas[coluna])

    desconhecidos = codigos_usados - codigos_validos

    if desconhecidos:
        erros.append(
            f"{nome}: vendas com codigos inexistentes."
        )

# 4. Nenhuma compra antes do cadastro do cliente.
vendas_com_cadastro = vendas.merge(
    clientes[[
        "codigo_cliente_origem",
        "data_cadastro",
    ]],
    on="codigo_cliente_origem",
    how="left",
    validate="many_to_one",
)

vendas_com_cadastro["data_cadastro"] = pd.to_datetime(
    vendas_com_cadastro["data_cadastro"],
    errors="raise",
)

if (
    vendas_com_cadastro["data_venda"]
    < vendas_com_cadastro["data_cadastro"]
).any():
    erros.append("Existem compras anteriores ao cadastro.")

# 5. Valores financeiros e quantidades.
if (vendas["quantidade"] <= 0).any():
    erros.append("Existem quantidades invalidas.")

if (vendas["preco_unitario"] < 0).any():
    erros.append("Existem precos negativos.")

if (vendas["custo_unitario"] < 0).any():
    erros.append("Existem custos negativos.")

subtotal = vendas["quantidade"] * vendas["preco_unitario"]

if (vendas["desconto_valor"] < 0).any():
    erros.append("Existem descontos negativos.")

if (vendas["desconto_valor"] > subtotal).any():
    erros.append("Existem descontos superiores ao subtotal.")

# 6. Consistencia de cada pedido.
consistencia = vendas.groupby("id_venda").agg(
    clientes=("codigo_cliente_origem", "nunique"),
    vendedores=("codigo_vendedor_origem", "nunique"),
    datas=("data_venda", "nunique"),
)

if (
    (consistencia["clientes"] != 1)
    | (consistencia["vendedores"] != 1)
    | (consistencia["datas"] != 1)
).any():
    erros.append(
        "Algum pedido possui cliente, vendedor ou data inconsistente."
    )

# Relatorio.
print("\n=== VALIDACAO DO HISTORICO DE VENDAS ===")
print(f"Linhas de itens: {len(vendas)}")
print(f"Pedidos distintos: {vendas['id_venda'].nunique()}")
print(
    "Clientes compradores: "
    f"{vendas['codigo_cliente_origem'].nunique()}"
)
print(f"Data inicial: {vendas['data_venda'].min().date()}")
print(f"Data final: {vendas['data_venda'].max().date()}")

print("\nVerificacoes:")
print(f"Linhas duplicadas: {vendas.duplicated().sum()}")
print(
    "Produtos repetidos no pedido: "
    f"{vendas.duplicated(['id_venda', 'codigo_produto_origem']).sum()}"
)

if erros:
    print("\nVALIDACAO REPROVADA:")
    for erro in erros:
        print(f"- {erro}")
    raise SystemExit(1)

print("\nVALIDACAO APROVADA: todas as regras passaram.")