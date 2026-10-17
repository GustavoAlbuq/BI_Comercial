from pathlib import Path

import numpy as np
import pandas as pd


# ==================================================
# BI COMERCIAL - GERACAO DE VENDAS SINTETICAS
# Periodo: 2024-01-01 a 2025-12-31
# Meta: 6.000 pedidos
# Saida: dados/originais/vendas_itens.csv
# Este script NAO acessa o PostgreSQL.
# ==================================================

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados" / "originais"
ARQUIVO_SAIDA = PASTA_DADOS / "vendas_itens.csv"

SEMENTE = 42
QUANTIDADE_PEDIDOS = 6000

DATA_INICIAL = pd.Timestamp("2024-01-01")
DATA_FINAL = pd.Timestamp("2025-12-31")

rng = np.random.default_rng(SEMENTE)


def carregar_csv(nome):
    caminho = PASTA_DADOS / nome

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho}"
        )

    return pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
    )


def validar_cadastros(clientes, produtos, vendedores):
    if len(clientes) != 300:
        raise ValueError("Esperados 300 clientes.")

    if len(produtos) != 60:
        raise ValueError("Esperados 60 produtos.")

    if len(vendedores) != 5:
        raise ValueError("Esperados 5 vendedores.")

    for df, coluna in [
        (clientes, "codigo_cliente_origem"),
        (produtos, "codigo_produto_origem"),
        (vendedores, "codigo_vendedor_origem"),
    ]:
        if df[coluna].isna().any() or df[coluna].duplicated().any():
            raise ValueError(
                f"Codigos ausentes ou duplicados: {coluna}"
            )


def preparar_clientes(clientes):
    clientes = clientes.copy()

    clientes["data_cadastro"] = pd.to_datetime(
        clientes["data_cadastro"],
        errors="raise",
    )

    # Grupos com diferentes comportamentos simulados.
    ordem = rng.permutation(len(clientes))
    clientes["grupo_compra"] = "RECORRENTE"

    clientes.loc[ordem[:75], "grupo_compra"] = "INATIVO"
    clientes.loc[ordem[75:150], "grupo_compra"] = "OCASIONAL"
    clientes.loc[ordem[150:225], "grupo_compra"] = "RECORRENTE"

    # Os 75 restantes permanecem recorrentes.
    clientes["data_limite_compra"] = DATA_FINAL

    mask_inativo = clientes["grupo_compra"].eq("INATIVO")
    mask_ocasional = clientes["grupo_compra"].eq("OCASIONAL")

    clientes.loc[mask_inativo, "data_limite_compra"] = pd.to_datetime(
        rng.choice(
            pd.date_range("2024-07-01", "2025-06-30"),
            size=mask_inativo.sum(),
        )
    )

    clientes.loc[mask_ocasional, "data_limite_compra"] = pd.to_datetime(
        rng.choice(
            pd.date_range("2025-07-01", "2025-10-01"),
            size=mask_ocasional.sum(),
        )
    )

    # Clientes cadastrados depois do limite precisam ter
    # um limite igual ou posterior ao cadastro.
    clientes["data_limite_compra"] = clientes[
        ["data_limite_compra", "data_cadastro"]
    ].max(axis=1)

    return clientes


def sortear_data(data_cadastro, data_limite):
    inicio = max(DATA_INICIAL, data_cadastro)
    fim = min(DATA_FINAL, data_limite)

    if inicio > fim:
        raise ValueError(
            "Cliente sem periodo valido para compra."
        )

    datas = pd.date_range(inicio, fim, freq="D")

    # Leve variacao sazonal mensal, sem eliminar nenhum mes.
    pesos_mensais = {
        1: 0.90, 2: 0.85, 3: 0.95, 4: 0.95,
        5: 1.00, 6: 1.10, 7: 1.05, 8: 1.00,
        9: 1.00, 10: 1.10, 11: 1.35, 12: 1.45,
    }

    pesos = np.array(
        [pesos_mensais[d.month] for d in datas],
        dtype=float,
    )
    pesos /= pesos.sum()

    return pd.Timestamp(rng.choice(datas, p=pesos))


def gerar_vendas(clientes, produtos, vendedores):
    registros = []

    # Clientes recorrentes recebem maior probabilidade de compra.
    pesos_clientes = np.where(
        clientes["grupo_compra"].eq("RECORRENTE"),
        1.8,
        np.where(
            clientes["grupo_compra"].eq("OCASIONAL"),
            1.0,
            0.7,
        ),
    ).astype(float)

    pesos_clientes /= pesos_clientes.sum()

    # Valores sinteticos por categoria.
    precos_base = {
        "Camiseta": 49.90,
        "Calca": 89.90,
        "Vestido": 99.90,
        "Conjunto": 119.90,
        "Shorts": 59.90,
        "Pijama": 69.90,
    }

    custos_base = {
        "Camiseta": 22.00,
        "Calca": 40.00,
        "Vestido": 45.00,
        "Conjunto": 55.00,
        "Shorts": 27.00,
        "Pijama": 31.00,
    }

    for numero_pedido in range(1, QUANTIDADE_PEDIDOS + 1):
        indice_cliente = int(
            rng.choice(len(clientes), p=pesos_clientes)
        )
        cliente = clientes.iloc[indice_cliente]

        data_venda = sortear_data(
            cliente["data_cadastro"],
            cliente["data_limite_compra"],
        )

        codigo_venda = f"VEN{numero_pedido:06d}"

        vendedor = vendedores.iloc[
            int(rng.integers(0, len(vendedores)))
        ]

        quantidade_itens = int(
            rng.choice([1, 2, 3, 4], p=[0.45, 0.32, 0.16, 0.07])
        )

        # Evita repetir o mesmo produto dentro do pedido.
        indices_produtos = rng.choice(
            len(produtos),
            size=min(quantidade_itens, len(produtos)),
            replace=False,
        )

        for indice_produto in indices_produtos:
            produto = produtos.iloc[int(indice_produto)]
            categoria = produto["categoria"]

            preco = round(
                precos_base[categoria]
                * rng.uniform(0.90, 1.15),
                2,
            )

            custo = round(
                custos_base[categoria]
                * rng.uniform(0.90, 1.10),
                2,
            )

            quantidade = int(rng.choice([1, 1, 1, 2, 3]))

            subtotal = round(quantidade * preco, 2)

            percentual_desconto = float(
                rng.choice(
                    [0.00, 0.00, 0.05, 0.10, 0.15],
                )
            )

            desconto = round(
                subtotal * percentual_desconto,
                2,
            )

            registros.append({
                "id_venda": codigo_venda,
                "codigo_cliente_origem": (
                    cliente["codigo_cliente_origem"]
                ),
                "codigo_produto_origem": (
                    produto["codigo_produto_origem"]
                ),
                "codigo_vendedor_origem": (
                    vendedor["codigo_vendedor_origem"]
                ),
                "data_venda": data_venda.strftime("%Y-%m-%d"),
                "quantidade": quantidade,
                "preco_unitario": preco,
                "desconto_valor": desconto,
                "custo_unitario": custo,
            })

    return pd.DataFrame(registros)


def main():
    clientes = carregar_csv("clientes.csv")
    produtos = carregar_csv("produtos.csv")
    vendedores = carregar_csv("vendedores.csv")

    validar_cadastros(clientes, produtos, vendedores)
    clientes = preparar_clientes(clientes)

    vendas = gerar_vendas(
        clientes,
        produtos,
        vendedores,
    )

    if vendas["id_venda"].nunique() != QUANTIDADE_PEDIDOS:
        raise ValueError("A quantidade de pedidos gerada esta incorreta.")

    datas = pd.to_datetime(vendas["data_venda"])

    if datas.min() < DATA_INICIAL or datas.max() > DATA_FINAL:
        raise ValueError("Existem vendas fora do periodo definido.")

    if (vendas["desconto_valor"] < 0).any():
        raise ValueError("Foi gerado desconto negativo.")

    if (
        vendas["desconto_valor"]
        > vendas["quantidade"] * vendas["preco_unitario"]
    ).any():
        raise ValueError("Foi gerado desconto superior ao subtotal.")

    # Gravar apenas depois das validacoes.
    vendas.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    receita = (
        vendas["quantidade"] * vendas["preco_unitario"]
        - vendas["desconto_valor"]
    ).sum()

    custo = (
        vendas["quantidade"] * vendas["custo_unitario"]
    ).sum()

    print("\nGERACAO CONCLUIDA")
    print(f"Pedidos: {vendas['id_venda'].nunique()}")
    print(f"Itens vendidos: {len(vendas)}")
    print(f"Clientes compradores: {vendas['codigo_cliente_origem'].nunique()}")
    print(f"Data inicial: {datas.min().date()}")
    print(f"Data final: {datas.max().date()}")
    print(f"Receita liquida simulada: R$ {receita:,.2f}")
    print(f"Custo total simulado: R$ {custo:,.2f}")
    print(f"Margem bruta simulada: R$ {receita - custo:,.2f}")
    print(f"Arquivo: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()