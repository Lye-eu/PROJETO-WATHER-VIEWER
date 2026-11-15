
# ============================================================
# ESTACAO METEOROLOGICA - RECEPTOR MQTT
# Responsabilidade: receber os dados enviados pelo ESP32.
# ============================================================

import json
import paho.mqtt.client as mqtt

# Importa as funções responsáveis pelo banco de dados.
from banco_dados import inicializar_banco, salvar_medicao


# -------------------- CONFIGURACOES --------------------------

# Endereço do computador onde o Mosquitto está instalado.
# Como o programa será executado no próprio computador,
# podemos utilizar localhost.
BROKER = "localhost"

# Porta padrão do Mosquitto.
PORTA = 1883

# Tópico utilizado pelo ESP32 para publicar as medições.
TOPICO = "estacao/esp32/dados"


# -------------------- RECEBIMENTO DOS DADOS ------------------

# Esta função será executada automaticamente quando
# o programa conseguir se conectar ao Mosquitto.
def ao_conectar(cliente, dados, flags, motivo, propriedades):
    if motivo == 0:
        print("Conectado ao Mosquitto!")
        cliente.subscribe(TOPICO)
        print("Aguardando dados do ESP32...")
    else:
        print("Falha na conexao. Codigo:", motivo)

# Esta função será executada sempre que uma nova mensagem
# chegar pelo tópico ao qual estamos inscritos.

def ao_receber(cliente, dados, mensagem):

    try:
        # Converte os bytes recebidos pelo MQTT em texto.
        conteudo = mensagem.payload.decode("utf-8")

        # Transforma o texto JSON em um dicionário Python.
        informacoes = json.loads(conteudo)

        # Exibe os dados recebidos no terminal.
        print("\n========== NOVA MEDICAO ==========")
        print("Temperatura DHT11:", informacoes["temperatura_dht"], "C")
        print("Umidade:", informacoes["umidade"], "%")
        print("Temperatura BMP280:", informacoes["temperatura_bmp"], "C")
        print("Pressao:", informacoes["pressao"], "hPa")
        print("Luminosidade:", informacoes["luminosidade"])
        print("MQ-135:", informacoes["mq135"])
        print("=================================")

        # Salva automaticamente a medição no banco SQLite.
        salvar_medicao(informacoes)

    except Exception as erro:
        # Informa qualquer erro ocorrido durante o recebimento,
        # a interpretação ou o armazenamento da mensagem.
        print("Erro ao processar mensagem:", erro)

# -------------------- CLIENTE MQTT ---------------------------

# Cria o cliente MQTT.
cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="Backend_Estacao"
)

# Define quais funções serão executadas nos eventos MQTT.
cliente.on_connect = ao_conectar
cliente.on_message = ao_receber


# -------------------- INICIALIZACAO --------------------------

# Garante que o banco e a tabela existam antes de receber dados.
inicializar_banco()

try:
    print("Iniciando receptor MQTT...")

    # Conecta o programa ao servidor Mosquitto.
    cliente.connect(BROKER, PORTA, 60)

    # Mantém o programa funcionando e aguardando mensagens.
    cliente.loop_forever()

except KeyboardInterrupt:
    # Permite encerrar o programa usando Ctrl + C.
    print("\nEncerrando receptor MQTT...")

finally:
    cliente.disconnect()
    print("Conexao encerrada.")
