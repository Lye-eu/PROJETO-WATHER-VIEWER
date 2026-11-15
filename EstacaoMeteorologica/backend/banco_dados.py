
# ============================================================
# ESTACAO METEOROLOGICA
# Arquivo: banco_dados.py
# Responsabilidade: criar e gerenciar o banco SQLite.
# ============================================================

import sqlite3
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------
# 1. CONFIGURACAO DO BANCO DE DADOS
# ------------------------------------------------------------

# Descobre a pasta onde este arquivo Python está localizado.
# Isso evita problemas caso o programa seja executado
# a partir de outra pasta do computador.
PASTA_ATUAL = Path(__file__).parent

# Define o caminho e o nome do arquivo do banco de dados.
CAMINHO_BANCO = PASTA_ATUAL / "estacao_meteorologica.db"

# ------------------------------------------------------------
# 2. CRIACAO DA TABELA
# ------------------------------------------------------------

def inicializar_banco():

    # Abre uma conexão com o banco de dados.
    # Se o arquivo ainda não existir, o SQLite o cria.
    conexao = sqlite3.connect(CAMINHO_BANCO)

    # Cria um cursor, que permite executar comandos SQL.
    cursor = conexao.cursor()

    # Cria a tabela de medições, caso ela ainda não exista.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicoes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            temperatura_dht REAL NOT NULL,

            umidade REAL NOT NULL,

            temperatura_bmp REAL NOT NULL,

            pressao REAL NOT NULL,

            luminosidade TEXT NOT NULL,

            mq135 INTEGER NOT NULL,

            data_hora TEXT NOT NULL

        )
    """)

    # Confirma as alterações realizadas no banco.
    conexao.commit()

    # Fecha a conexão para liberar os recursos.
    conexao.close()

    print("Banco de dados inicializado com sucesso!")


# ------------------------------------------------------------
# 3. SALVAMENTO DAS MEDICOES
# ------------------------------------------------------------

def salvar_medicao(informacoes):

    # Abre uma conexão com o banco de dados.
    conexao = sqlite3.connect(CAMINHO_BANCO)

    # Cria o cursor para executar o comando SQL.
    cursor = conexao.cursor()

    # Obtém a data e a hora atuais do computador.
    # O formato ISO facilita a organização e a consulta.
    data_hora = datetime.now().isoformat(
        timespec="seconds"
    )

    # Comando SQL responsável por inserir uma nova medição.
    # Cada ? representa um valor que será preenchido abaixo.
    comando = """
        INSERT INTO medicoes (
            temperatura_dht,
            umidade,
            temperatura_bmp,
            pressao,
            luminosidade,
            mq135,
            data_hora
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    # Organiza os valores recebidos em uma tupla,
    # respeitando a mesma ordem das colunas do INSERT.
    valores = (
        informacoes["temperatura_dht"],
        informacoes["umidade"],
        informacoes["temperatura_bmp"],
        informacoes["pressao"],
        informacoes["luminosidade"],
        informacoes["mq135"],
        data_hora
    )

    # Executa o comando SQL utilizando os valores organizados.
    cursor.execute(comando, valores)

    # Confirma e grava a medição no banco.
    conexao.commit()

    # Fecha a conexão.
    conexao.close()

    print("Medicao salva no banco de dados!")


# ------------------------------------------------------------
# 4. TESTE INICIAL
# ------------------------------------------------------------

if __name__ == "__main__":

    # Executa a criação da tabela quando este arquivo
    # é iniciado diretamente.
    inicializar_banco()




# ============================================================
# 5. CONSULTAR AS ULTIMAS MEDICOES
# ============================================================

def consultar_medicoes(limite=10):

    # Abre uma conexão com o banco.
    conexao = sqlite3.connect(CAMINHO_BANCO)

    # Permite acessar os resultados pelo nome das colunas.
    conexao.row_factory = sqlite3.Row

    cursor = conexao.cursor()

    # Busca as medições mais recentes.
    # O ORDER BY organiza da mais nova para a mais antiga.
    # O LIMIT define quantos registros serão retornados.
    cursor.execute("""
        SELECT *
        FROM medicoes
        ORDER BY id DESC
        LIMIT ?
    """, (limite,))

    # Recupera todos os resultados da consulta.
    medicoes = cursor.fetchall()

    conexao.close()

    return medicoes


# ============================================================
# 6. CONTAR O TOTAL DE MEDICOES
# ============================================================

def contar_medicoes():

    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    # COUNT(*) conta quantos registros existem na tabela.
    cursor.execute("SELECT COUNT(*) FROM medicoes")

    # fetchone() recupera o resultado da consulta.
    total = cursor.fetchone()[0]

    conexao.close()

    return total
