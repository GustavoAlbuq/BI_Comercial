BI Comercial — Análise de Vendas



1\. Apresentação do Projeto



O BI Comercial é um projeto acadêmico de Business Intelligence desenvolvido no contexto de uma disciplina de pós-graduação em Engenharia e Análise de Dados. O objetivo é construir uma solução de análise comercial capaz de organizar dados de vendas, estruturar um modelo dimensional e gerar indicadores para apoiar a tomada de decisão.



O projeto utiliza dados sintéticos de uma operação comercial de varejo, contemplando clientes, produtos, vendedores, datas e itens vendidos no período de 2024 a 2025.



2\. Objetivos



\* Desenvolver um fluxo de preparação, validação e carga de dados.

\* Estruturar um banco de dados relacional com modelagem dimensional.

\* Integrar Python, PostgreSQL, Pentaho Data Integration e Power BI.

\* Analisar indicadores de desempenho comercial.

\* Construir visualizações para facilitar a interpretação dos resultados.



3\. Tecnologias Utilizadas



Tecnologia	Aplicação

Python	Geração, preparação e validação dos dados

Pandas e NumPy	Manipulação e tratamento dos dados

PostgreSQL	Armazenamento dos dados e estruturação do Data Warehouse

Pentaho Data Integration 9.4	Orquestração de um processo de leitura e validação dos dados

JupyterLab	Análise exploratória e desenvolvimento analítico

Power BI	Modelagem analítica, medidas DAX e visualização dos indicadores

Git e GitHub	Versionamento e disponibilização do código-fonte



4\. Arquitetura da Solução



O fluxo desenvolvido contempla as seguintes etapas:



1\. Geração dos dados: criação de uma base sintética de vendas e cadastros.

2\. Preparação e validação: utilização de scripts Python para preparar os dados e verificar a integridade das chaves dimensionais.

3\. Armazenamento: carga das tabelas no PostgreSQL.

4\. Análise exploratória: utilização do JupyterLab e Pandas para investigar o comportamento das vendas.

5\. Processamento com Pentaho: criação de uma transformação para leitura dos registros da tabela fato e validação de uma regra de negócio, além de um job para executar a transformação.

6\. Visualização: construção de um relatório no Power BI com indicadores e gráficos comerciais.



Observação: a transformação do Pentaho implementada nesta versão realiza leitura e validação dos registros, direcionando-os para saídas de registros válidos e inválidos. Ela não realiza uma nova carga em uma tabela de destino.



5\. Modelagem Dimensional



O banco de dados bi\_comercial utiliza uma estrutura dimensional composta por uma tabela fato e quatro dimensões.



Tabela fato



\* fato\_vendas: registra os itens vendidos, seus identificadores dimensionais, a receita líquida e o custo total.



Tabelas dimensão



\* dim\_cliente: informações dos clientes.

\* dim\_produto: informações dos produtos.

\* dim\_vendedor: informações dos vendedores.

\* dim\_data: calendário utilizado nas análises temporais.



A granularidade da tabela fato é uma linha por item vendido. Portanto, um mesmo pedido pode aparecer em várias linhas quando contém diferentes itens.



6\. Base de Dados



A base sintética contempla o período de 2024 a 2025.



Característica	Quantidade

Pedidos distintos	6.000

Itens vendidos	11.091

Clientes compradores	300

Produtos cadastrados	60

Vendedores cadastrados	5

Dias no calendário	731



Os dados são sintéticos e foram criados para fins acadêmicos. Os resultados representam o cenário simulado, não o desempenho de uma empresa real.



7\. Indicadores e Resultados



Os principais resultados consolidados da base são:



Indicador	Resultado

Receita líquida	R$ 1.385.694,27

Custo total	R$ 646.699,17

Margem bruta	R$ 738.995,10

Pedidos distintos	6.000

Clientes compradores	300



A margem bruta corresponde à diferença entre a receita líquida e o custo total registrados na base.



As análises desenvolvidas incluem:



\* Evolução mensal da receita.

\* Desempenho comercial por produto.

\* Desempenho por vendedor.

\* Recência de compra dos clientes.



Na análise de recência, 136 clientes compradores estavam há pelo menos 90 dias sem comprar, considerando como data de referência 31 de dezembro de 2025. Essa análise considera apenas clientes que realizaram ao menos uma compra no período.



8\. Estrutura do Repositório



BI-Comercial/

├── dados/

│   ├── originais/

│   ├── tratados/

│   └── warehouse/

├── notebooks/

│   └── 01\_analise\_exploratoria.ipynb

├── pentaho/

│   ├── jobs/

│   │   └── 00\_job\_carga\_vendas.kjb

│   └── transformacoes/

│       └── 01\_leitura\_fato\_vendas.ktr

├── powerbi/

│   └── BI\_Comercial.pbix

├── src/

│   ├── gerar\_cadastros.py

│   ├── gerar\_vendas.py

│   ├── preparar\_fato\_vendas.py

│   ├── carregar\_cadastros.py

│   ├── carregar\_fato\_vendas.py

│   ├── validar\_cadastros.py

│   ├── validar\_vendas.py

│   └── testar\_conexao.py

├── .gitignore

└── README.md



9\. Como Executar



Pré-requisitos



\* Python 3.11 ou compatível com as dependências do projeto.

\* PostgreSQL instalado e em execução.

\* Banco de dados bi\_comercial configurado.

\* Bibliotecas Python utilizadas nos scripts.

\* Pentaho Data Integration 9.4 para executar o job e a transformação.

\* Power BI Desktop para abrir o relatório.



Preparação do ambiente Python



No terminal, acesse a pasta do projeto e crie um ambiente virtual, se ainda não existir:



python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1



Instale as dependências utilizadas:



python -m pip install pandas numpy "psycopg\[binary]" jupyterlab matplotlib



Banco de dados



Crie o banco bi\_comercial no PostgreSQL e execute os scripts SQL de criação das dimensões e da tabela fato, respeitando as dependências entre as tabelas.



Configure as credenciais de conexão conforme o ambiente local. Não publique senhas ou outras credenciais no repositório.



Execução dos scripts



Os scripts disponíveis na pasta src/ abrangem geração, preparação, carregamento e validação dos dados. A execução deve respeitar a sequência de dependências do projeto e a configuração do PostgreSQL.



O notebook de análise exploratória pode ser aberto com:



jupyter lab



Pentaho e Power BI



Abra o arquivo pentaho/jobs/00\_job\_carga\_vendas.kjb no Spoon para executar o job e suas transformações associadas.



Para visualizar os indicadores, abra powerbi/BI\_Comercial.pbix no Power BI Desktop. Caso necessário, atualize as credenciais e a conexão com o PostgreSQL no ambiente local.



10\. Limitações e Próximas Evoluções



Como evolução do projeto, podem ser implementados:



\* Documentação automatizada da criação do banco de dados.

\* Parametrização das credenciais e configurações de ambiente.

\* Testes automatizados de qualidade dos dados.

\* Expansão do processo ETL no Pentaho, incluindo gravação em uma tabela de destino.

\* Novas páginas e indicadores no Power BI.

\* Rotinas automatizadas de atualização dos dados.



11\. Considerações Finais



O projeto demonstra a aplicação integrada de conceitos de Engenharia e Análise de Dados, abrangendo preparação de dados, modelagem dimensional, armazenamento relacional, análise exploratória, validação de registros e visualização de indicadores comerciais.



A solução estabelece uma base para futuras evoluções de um ambiente de Business Intelligence orientado à análise de desempenho comercial.



Autor



Projeto acadêmico desenvolvido para uma disciplina de pós-graduação em Engenharia e Análise de Dados.



Repositório: https://github.com/GustavoAlbuq/BI\_Comercial

