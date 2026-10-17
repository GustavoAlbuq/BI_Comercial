from pathlib import Path

import numpy as np
import pandas as pd


# Caminho do projeto
RAIZ = Path(__file__).resolve().parent.parent
PASTA_SAIDA = RAIZ / "dados" / "originais"
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

# Semente fixa para reproduzir os mesmos dados em novas execuções
rng = np.random.default_rng(42)


# --------------------------------------------------
# 1. CLIENTES FICTICIOS
# --------------------------------------------------

nomes = [
    "Ana", "Bruno", "Carla", "Daniel", "Eduarda",
    "Felipe", "Gabriela", "Henrique", "Isabela", "Joao",
    "Julia", "Lucas", "Mariana", "Mateus", "Natalia",
    "Pedro", "Rafaela", "Ricardo", "Sofia", "Thiago",
    "Amanda", "Caio", "Leticia", "Marcelo", "Paula",
    "Renato", "Vanessa", "Diego", "Camila", "Andre",
]

sobrenomes = [
    "Almeida", "Barbosa", "Carvalho", "Dias", "Ferreira",
    "Gomes", "Lima", "Mendes", "Oliveira", "Pereira",
    "Ramos", "Santos", "Silva", "Souza", "Costa",
    "Martins", "Araujo", "Rocha", "Nunes", "Freitas",
]

cidades = [
    "Joao Pessoa",
    "Campina Grande",
    "Sape",
    "Guarabira",
    "Mamanguape",
    "Bayeux",
    "Santa Rita",
    "Patos",
    "Cabedelo",
    "Sousa",
]

quantidade_clientes = 300

clientes = pd.DataFrame({
    "codigo_cliente_origem": [
        f"CLI{i:04d}"
        for i in range(1, quantidade_clientes + 1)
    ],
    "nome_cliente": [
        f"{rng.choice(nomes)} {rng.choice(sobrenomes)}"
        for _ in range(quantidade_clientes)
    ],
    "cidade": rng.choice(cidades, size=quantidade_clientes),
    "data_cadastro": pd.to_datetime(
        rng.integers(
            pd.Timestamp("2023-01-01").value // 86_400_000_000_000,
            pd.Timestamp("2025-12-31").value // 86_400_000_000_000 + 1,
            size=quantidade_clientes,
        ),
        unit="D",
    ).strftime("%Y-%m-%d"),
    "status_cliente": rng.choice(
        ["ATIVO", "INATIVO"],
        size=quantidade_clientes,
        p=[0.75, 0.25],
    ),
})


# --------------------------------------------------
# 2. PRODUTOS FICTICIOS
# --------------------------------------------------

catalogo = {
    "Camiseta": ["PP", "P", "M", "G", "GG"],
    "Calca": ["2", "4", "6", "8", "10", "12", "14", "16"],
    "Vestido": ["2", "4", "6", "8", "10", "12", "14", "16"],
    "Conjunto": ["2", "4", "6", "8", "10", "12", "14", "16"],
    "Shorts": ["2", "4", "6", "8", "10", "12", "14", "16"],
    "Pijama": ["2", "4", "6", "8", "10", "12", "14", "16"],
}

marcas = ["Marca Aurora", "Marca Encanto", "Marca Brisa"]

produtos_lista = []

for categoria, tamanhos in catalogo.items():
    for numero in range(1, 11):
        tamanho = tamanhos[(numero - 1) % len(tamanhos)]

        produtos_lista.append({
            "codigo_produto_origem": f"PROD{len(produtos_lista) + 1:03d}",
            "nome_produto": f"{categoria} Infantil Modelo {numero:02d}",
            "categoria": categoria,
            "marca": rng.choice(marcas),
            "tamanho": tamanho,
        })

produtos = pd.DataFrame(produtos_lista)


# --------------------------------------------------
# 3. VENDEDORES FICTICIOS
# --------------------------------------------------

vendedores = pd.DataFrame({
    "codigo_vendedor_origem": [
        "VEND001",
        "VEND002",
        "VEND003",
        "VEND004",
        "VEND005",
    ],
    "nome_vendedor": [
        "Vendedora Ana",
        "Vendedora Beatriz",
        "Vendedora Clara",
        "Vendedora Diana",
        "Vendedora Elisa",
    ],
    "data_admissao": [
        "2022-03-01",
        "2022-08-15",
        "2023-02-01",
        "2023-09-10",
        "2024-01-02",
    ],
    "status_vendedor": ["ATIVO"] * 5,
})


# --------------------------------------------------
# 4. EXPORTACAO DOS ARQUIVOS
# --------------------------------------------------

arquivos = {
    "clientes.csv": clientes,
    "produtos.csv": produtos,
    "vendedores.csv": vendedores,
}

for nome_arquivo, dataframe in arquivos.items():
    caminho = PASTA_SAIDA / nome_arquivo
    dataframe.to_csv(
        caminho,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )
    print(f"Arquivo criado: {caminho}")
    print(f"Registros: {len(dataframe)}")

print("\nGeracao concluida.")
print(f"Clientes: {len(clientes)}")
print(f"Produtos: {len(produtos)}")
print(f"Vendedores: {len(vendedores)}")