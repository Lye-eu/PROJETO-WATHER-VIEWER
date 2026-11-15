
# ============================================================
# TESTE DO BANCO DE DADOS
# ============================================================

# Importa as funções de consulta do banco.
from banco_dados import consultar_medicoes, contar_medicoes

# Mostra a quantidade total de registros armazenados.
print("Total de medicoes:", contar_medicoes())

# Consulta as dez medições mais recentes.
medicoes = consultar_medicoes(10)

print("\nULTIMAS MEDICOES REGISTRADAS")
print("----------------------------------------")

# Percorre cada registro retornado pelo banco.
for medicao in medicoes:

    print("ID:", medicao["id"])
    print("Temperatura DHT11:", medicao["temperatura_dht"], "C")
    print("Umidade:", medicao["umidade"], "%")
    print("Temperatura BMP:", medicao["temperatura_bmp"], "C")
    print("Pressao:", medicao["pressao"], "hPa")
    print("Luminosidade:", medicao["luminosidade"])
    print("MQ-135:", medicao["mq135"])
    print("Data e hora:", medicao["data_hora"])

    print("----------------------------------------")
