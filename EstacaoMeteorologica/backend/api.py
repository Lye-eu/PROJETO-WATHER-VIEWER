from datetime import datetime, timedelta
import sqlite3

from flask import Flask, jsonify, render_template, request

from banco_dados import CAMINHO_BANCO, contar_medicoes, consultar_medicoes

app = Flask(__name__)


@app.route("/")
def inicio():
    """Abre a página principal do dashboard."""
    return render_template("index.html")


@app.route("/api/ultima")
def obter_ultima_medicao():
    """Retorna a medição mais recente registrada no SQLite."""
    medicoes = consultar_medicoes(1)

    if not medicoes:
        return jsonify({"mensagem": "Ainda não existem medições."}), 404

    return jsonify(dict(medicoes[0]))


@app.route("/api/medicoes")
def obter_medicoes():
    """Retorna as últimas medições. O limite pode ser informado pela URL."""
    try:
        limite = int(request.args.get("limite", 100))
        limite = max(1, min(limite, 5000))
    except ValueError:
        return jsonify({"erro": "O limite precisa ser um número inteiro."}), 400

    medicoes = consultar_medicoes(limite)
    return jsonify([dict(medicao) for medicao in medicoes])


@app.route("/api/historico")
def obter_historico():
    """Retorna médias agrupadas por minuto para o gráfico do período escolhido."""
    try:
        dias = int(request.args.get("dias", 7))
        dias = max(1, min(dias, 30))
    except ValueError:
        return jsonify({"erro": "O período precisa ser um número inteiro."}), 400

    data_inicial = (datetime.now() - timedelta(days=dias)).isoformat(timespec="seconds")

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    # Agrupa as leituras por minuto para evitar enviar milhares de pontos repetidos.
    cursor.execute("""
        SELECT
            substr(data_hora, 1, 16) AS minuto,
            AVG(temperatura_dht) AS temperatura_dht,
            AVG(temperatura_bmp) AS temperatura_bmp,
            AVG(umidade) AS umidade,
            AVG(pressao) AS pressao,
            AVG(mq135) AS mq135,
            MAX(luminosidade) AS luminosidade
        FROM medicoes
        WHERE data_hora >= ?
        GROUP BY minuto
        ORDER BY minuto ASC
    """, (data_inicial,))

    historico = [dict(registro) for registro in cursor.fetchall()]
    conexao.close()

    return jsonify({
        "periodo_dias": dias,
        "quantidade_pontos": len(historico),
        "dados": historico
    })


@app.route("/api/total")
def obter_total():
    """Retorna quantas medições estão armazenadas no banco."""
    return jsonify({"total_medicoes": contar_medicoes()})


if __name__ == "__main__":
    # A porta 5000 é a mesma que já usamos nos testes da API.
    # host 0.0.0.0 permite acesso de outros dispositivos na mesma rede.
    # Ao compartilhar o dashboard, mantenha debug=False (sem depurador exposto).
    app.run(host="0.0.0.0", port=5000, debug=False)

