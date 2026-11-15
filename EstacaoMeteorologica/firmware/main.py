# ============================================================
# ESTACAO METEOROLOGICA INTELIGENTE - ESP32
# Sensores: DHT11, BMP280, LDR e MQ-135
# Comunicacao: Wi-Fi + MQTT (Mosquitto)
# Display: OLED 128x64
# Linguagem: MicroPython
# ============================================================

# -------------------- BIBLIOTECAS ----------------------------

import network
import time
import json
import dht
import ssd1306

from machine import Pin, SoftI2C, ADC
from umqtt.simple import MQTTClient


# -------------------- REDES WI-FI ----------------------------

# Cadastre aqui as duas redes que pretende utilizar.
# O ESP32 tentará a primeira e, se não conseguir,
# tentará a segunda.

# -------------------- REDES WI-FI ----------------------------

# PARA USAR ESTE CODIGO: altere "ssid" e "senha" para a sua rede Wi-Fi.
# Em "broker", informe o IP LOCAL do computador com o Mosquitto nessa rede.
# Se usar duas redes, preencha os tres campos de cada uma.
# Nao publique as suas senhas reais no GitHub.

REDES = [
    {
        "ssid": "SSID_DA_REDE_1",
        "senha": "SENHA_DA_REDE_1",
        "broker": "IP_DO_COMPUTADOR_NA_REDE_1"
    },
    {
        "ssid": "SSID_DA_REDE_2",
        "senha": "SENHA_DA_REDE_2",
        "broker": "IP_DO_COMPUTADOR_NA_REDE_2"
    }
]
# Configurações do servidor MQTT.
BROKER_PORT = 1883
CLIENT_ID = "ESP32_Estacao"

# Tópico no qual os dados serão publicados.
TOPIC = b"estacao/esp32/dados"


# -------------------- CONFIGURACAO DOS SENSORES --------------

# Configura o barramento I2C compartilhado pelo OLED e BMP280.
# D22 = SCL e D21 = SDA.
i2c = SoftI2C(
    scl=Pin(22),
    sda=Pin(21),
    freq=100000
)

# Inicializa o display OLED de 128 por 64 pixels.
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Inicializa o sensor DHT11 no pino D15.
sensor_dht = dht.DHT11(Pin(15))

# Inicializa o sensor LDR digital no pino D27.
sensor_ldr = Pin(27, Pin.IN)

# Inicializa o MQ-135 no pino D34.
# A leitura será um valor bruto do conversor analógico.
sensor_mq = ADC(Pin(34))
sensor_mq.atten(ADC.ATTN_11DB)


# -------------------- CONFIGURACAO DO BMP280 -----------------

# Endereço I2C do BMP280.
ENDERECO = 0x76

# Lê os 24 bytes de calibração gravados no próprio sensor.
cal = i2c.readfrom_mem(ENDERECO, 0x88, 24)


# Converte dois bytes em um número inteiro sem sinal.
def u16(i):
    return cal[i] | (cal[i + 1] << 8)


# Converte dois bytes em um número inteiro com sinal.
# Isso é necessário porque alguns valores de calibração
# do BMP280 podem ser negativos.
def s16(i):
    valor = u16(i)

    if valor > 32767:
        valor -= 65536

    return valor


# Recupera os coeficientes de calibração da temperatura.
T1 = u16(0)
T2 = s16(2)
T3 = s16(4)

# Recupera os coeficientes de calibração da pressão.
P1 = u16(6)
P2 = s16(8)
P3 = s16(10)
P4 = s16(12)
P5 = s16(14)
P6 = s16(16)
P7 = s16(18)
P8 = s16(20)
P9 = s16(22)

# Configura o BMP280 para realizar as medições.
i2c.writeto_mem(ENDERECO, 0xF4, b'\x27')


# Função responsável por ler e calcular os dados do BMP280.
def ler_bmp280():

    # Lê os registros que contêm pressão e temperatura.
    dados = i2c.readfrom_mem(ENDERECO, 0xF7, 6)

    # Reconstrói os valores brutos de 20 bits.
    adc_p = (dados[0] << 12) | (dados[1] << 4) | (dados[2] >> 4)
    adc_t = (dados[3] << 12) | (dados[4] << 4) | (dados[5] >> 4)

    # Calcula a temperatura usando os coeficientes de calibração.
    var1 = (adc_t / 16384 - T1 / 1024) * T2
    var2 = ((adc_t / 131072 - T1 / 8192) ** 2) * T3

    t_fine = var1 + var2
    temperatura = t_fine / 5120

    # Calcula a pressão atmosférica compensada.
    var1 = t_fine / 2 - 64000
    var2 = var1 * var1 * P6 / 32768
    var2 += var1 * P5 * 2
    var2 = var2 / 4 + P4 * 65536

    var1 = (P3 * var1 * var1 / 524288 + P2 * var1) / 524288
    var1 = (1 + var1 / 32768) * P1

    # Evita divisão por zero caso a calibração esteja inválida.
    if var1 == 0:
        raise ValueError("Erro na calibracao da pressao")

    pressao = 1048576 - adc_p
    pressao = (pressao - var2 / 4096) * 6250 / var1

    var1 = P9 * pressao * pressao / 2147483648
    var2 = pressao * P8 / 32768

    pressao += (var1 + var2 + P7) / 16

    # Retorna temperatura em Celsius e pressão em hPa.
    return temperatura, pressao / 100


# -------------------- CONEXAO WI-FI --------------------------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)


def conectar_wifi():

    while True:

        for rede in REDES:

            print("================================")
            print("Tentando conectar a:", rede["ssid"])

            try:
                # Desativa a interface Wi-Fi para limpar
                # o estado da conexão anterior.
                wifi.active(False)
                time.sleep(2)

                # Ativa novamente a interface Wi-Fi.
                wifi.active(True)
                time.sleep(2)

                # Inicia a conexão com a rede atual.
                wifi.connect(rede["ssid"], rede["senha"])

                # Aguarda até 20 segundos pela conexão.
                for tentativa in range(20):

                    if wifi.isconnected():

                        print("Wi-Fi conectado!")
                        print("Rede:", rede["ssid"])
                        print("IP do ESP32:", wifi.ifconfig()[0])

                        # Retorna o IP do computador
                        # correspondente à rede conectada.
                        return rede["broker"]

                    time.sleep(1)

                print("Tempo esgotado para:", rede["ssid"])

            except Exception as erro:

                print("Erro ao conectar:", erro)

        # Se nenhuma rede funcionar, aguarda e tenta novamente.
        print("Nenhuma rede disponivel.")
        print("Nova tentativa em 5 segundos...")
        time.sleep(5)
# -------------------- CONEXAO MQTT ---------------------------

# Variável que guardará a conexão MQTT ativa.
cliente = None


def conectar_mqtt(ip_broker):

    global cliente

    while True:

        try:
            print("Conectando ao Mosquitto:", ip_broker)

            # Cria o cliente MQTT usando o IP da rede atual.
            cliente = MQTTClient(
                CLIENT_ID,
                ip_broker,
                port=BROKER_PORT
            )

            cliente.connect()

            print("Conectado ao Mosquitto!")
            return

        except Exception as erro:

            print("Erro na conexao MQTT:", erro)
            cliente = None

            # Aguarda antes de tentar novamente.
            time.sleep(5)


# -------------------- INICIALIZACAO --------------------------

# Conecta ao Wi-Fi e identifica o IP do servidor MQTT.
ip_broker = conectar_wifi()

# Conecta ao Mosquitto.
conectar_mqtt(ip_broker)

print("Estacao meteorologica iniciada!")


# -------------------- LOOP PRINCIPAL -------------------------

while True:

    # Verifica se o Wi-Fi continua conectado.
    if not wifi.isconnected():

        print("Conexao Wi-Fi perdida!")

        # Reconecta e obtém o endereço do broker da rede escolhida.
        ip_broker = conectar_wifi()

        # A conexão MQTT antiga não deve ser reutilizada.
        cliente = None

    # Se o cliente MQTT não estiver conectado, tenta conectar.
    if cliente is None:
        conectar_mqtt(ip_broker)

    try:

        # ----------- LEITURA DO DHT11 -------------------------

        sensor_dht.measure()

        temperatura_dht = sensor_dht.temperature()
        umidade = sensor_dht.humidity()

        # ----------- LEITURA DO BMP280 ------------------------

        temperatura_bmp, pressao = ler_bmp280()

        # ----------- LEITURA DO LDR ----------------------------

        leitura_ldr = sensor_ldr.value()

        # No módulo utilizado:
        # 0 significa claro e 1 significa escuro.
        if leitura_ldr == 0:
            luminosidade = "CLARO"
        else:
            luminosidade = "ESCURO"

        # ----------- LEITURA DO MQ-135 -------------------------

        leitura_mq = sensor_mq.read()

        # ----------- ORGANIZACAO DOS DADOS --------------------

        # Agrupa todas as medições em um dicionário.
        # Cada chave identifica uma informação.
        dados = {
            "temperatura_dht": temperatura_dht,
            "umidade": umidade,
            "temperatura_bmp": round(temperatura_bmp, 2),
            "pressao": round(pressao, 2),
            "luminosidade": luminosidade,
            "mq135": leitura_mq
        }

        # Converte o dicionário para JSON e depois para bytes,
        # formato utilizado pelo cliente MQTT para publicação.
        mensagem = json.dumps(dados).encode()

        # ----------- ENVIO MQTT -------------------------------

        try:

            cliente.publish(TOPIC, mensagem)
            print("Dados enviados ao MQTT!")

        except Exception as erro:

            # Se a publicação falhar, descarta a conexão atual.
            # Na próxima volta do loop, tentará conectar novamente.
            print("Erro ao enviar dados:", erro)
            cliente = None

        # ----------- EXIBICAO NO TERMINAL ---------------------

        print("================================")
        print("Temperatura DHT11:", temperatura_dht, "C")
        print("Umidade:", umidade, "%")
        print("Temperatura BMP280:", temperatura_bmp, "C")
        print("Pressao:", pressao, "hPa")
        print("Luminosidade:", luminosidade)
        print("MQ-135:", leitura_mq)
        print("================================")

        # ----------- ATUALIZACAO DO OLED ----------------------

        oled.fill(0)

        # Mantém os textos nas posições que funcionaram
        # com a divisão amarela e azul do nosso display.
        oled.text("ESTACAO METEO", 0, 3)
        oled.text("Temp: {:.1f}C".format(temperatura_dht), 0, 18)
        oled.text("Umid: {}%".format(umidade), 0, 27)
        oled.text("Press: {:.1f}hPa".format(pressao), 0, 36)
        oled.text("Luz: {}".format(luminosidade), 0, 45)
        oled.text("MQ135: {}".format(leitura_mq), 0, 54)

        # Envia o conteúdo para aparecer no display.
        oled.show()

    except Exception as erro:

        # Se algum sensor apresentar erro, informa no terminal
        # e continua tentando na próxima leitura.
        print("Erro durante a leitura dos sensores:", erro)

    # Intervalo entre as atualizações: 5 segundos.
    time.sleep(5)