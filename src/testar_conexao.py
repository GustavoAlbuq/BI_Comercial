import psycopg

try:
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="bi_comercial",
        user="postgres",
        password=input("Digite a senha do PostgreSQL: "),
        connect_timeout=5,
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user;"
            )
            banco, usuario = cursor.fetchone()

            print("Conexao realizada com sucesso!")
            print(f"Banco conectado: {banco}")
            print(f"Usuario conectado: {usuario}")

except psycopg.OperationalError as erro:
    print("Nao foi possivel conectar ao PostgreSQL.")
    print(f"Detalhe: {erro}")