# Estação Meteorológica Inteligente para Monitoramento Ambiental Urbano

Projeto acadêmico de uma estação meteorológica baseada em **ESP32 e MicroPython**, com coleta de medições ambientais, transmissão por **MQTT**, armazenamento em **SQLite** e visualização em um **dashboard web** desenvolvido com Flask.

> **Status:** protótipo funcional em ambiente local. O ESP32, a comunicação MQTT, o armazenamento SQLite e as rotas da API foram testados. O dashboard exibe medições e permite consultar o histórico armazenado.

## 1. Objetivo

Desenvolver uma solução de monitoramento ambiental urbano capaz de coletar dados de sensores, transmiti-los pela rede Wi-Fi, armazenar as medições e apresentá-las por meio de uma interface web.

O sistema foi desenvolvido como parte de uma **Atividade Prática Supervisionada (APS)** do curso de Ciência da Computação.

## 2. Funcionalidades

- Leitura periódica dos sensores conectados ao ESP32.
- Exibição local de informações em display OLED.
- Conexão Wi-Fi com tentativa de redes configuradas no firmware.
- Publicação de dados no broker MQTT Mosquitto.
- Recepção de mensagens MQTT em Python.
- Armazenamento de medições com data e hora em banco SQLite.
- API REST para consultar a última medição, registros recentes, total de registros e histórico.
- Dashboard web com indicadores atuais e gráficos históricos.
- Filtros de histórico de **24 horas, 3 dias e 7 dias**.
- Inicializador `.bat` para iniciar o receptor, a API e abrir o dashboard no Windows.

## 3. Arquitetura

```text
Sensores ──> ESP32 (MicroPython)
                  │
                  │ Wi-Fi / MQTT
                  ▼
           Mosquitto (PC)
                  │
                  ▼
          receptor_mqtt.py
                  │
                  ▼
         SQLite (medições)
                  │
                  ▼
             api.py
          (Flask / HTTP)
                  │
                  ▼
          Dashboard web
```

O ESP32 envia as medições ao tópico MQTT `estacao/esp32/dados`. O receptor Python assina esse tópico e grava as mensagens recebidas no banco. O Flask consulta o banco para atender às requisições do dashboard.

## 4. Hardware e medições

| Componente | Função | Observação |
| --- | --- | --- |
| ESP32 | Controlador principal com Wi-Fi | Executa MicroPython |
| DHT11 | Temperatura e umidade | Medições ambientais |
| BMP280 | Temperatura e pressão atmosférica | Comunicação I²C |
| LDR (módulo digital) | Detecção de luminosidade | Estados **CLARO** ou **ESCURO**; não mede lux |
| MQ-135 | Leitura analógica associada ao sensor de gases | **Valor bruto do ADC**, sem calibração em ppm |
| OLED SSD1306 128×64 | Exibição local | Comunicação I²C |
| Protoboard, jumpers e resistores | Interligação do circuito | Divisor resistivo utilizado na leitura analógica do MQ-135 |

### Pinos utilizados

| Componente / sinal | Pino ESP32 |
| --- | --- |
| DHT11 (dados) | GPIO 15 |
| LDR (saída digital) | GPIO 27 |
| MQ-135 (leitura analógica via divisor resistivo) | GPIO 34 |
| I²C SDA — BMP280 e OLED | GPIO 21 |
| I²C SCL — BMP280 e OLED | GPIO 22 |

O BMP280 foi identificado no endereço I²C `0x76` e o OLED no endereço `0x3C` durante os testes.

**Atenção:** o MQ-135 não fornece, neste projeto, uma concentração calibrada de gases ou um índice validado de qualidade do ar. A leitura da LDR é binária, e não uma medição de intensidade luminosa em lux.

## 5. Tecnologias

- **MicroPython:** firmware do ESP32.
- **Wi-Fi:** comunicação do dispositivo com a rede local.
- **MQTT / Mosquitto:** transporte das mensagens dos sensores.
- **Python:** receptor MQTT e backend.
- **Paho MQTT:** cliente MQTT Python.
- **SQLite:** persistência das medições.
- **Flask:** servidor web e API HTTP.
- **HTML, CSS e JavaScript:** interface do dashboard.
- **Chart.js:** gráficos do histórico, carregados por CDN.
- **Windows / PowerShell:** ambiente de execução utilizado nos testes.

## 6. Estrutura do projeto

```text
EstacaoMeteorologica/
├── README.md
├── iniciar_estacao.bat
├── .gitignore
├── firmware/
│   ├── Base_EstacaoMeteo.py  # versão com configurações de exemplo
│   └── main.py               # cópia para salvar no ESP32
└── backend/
    ├── receptor_mqtt.py
    ├── banco_dados.py
    ├── teste_banco.py
    ├── api.py
    ├── estacao_meteorologica.db    # criado ao executar; não incluído no GitHub
    └── templates/
        └── index.html
```

No ESP32, uma cópia do firmware principal foi salva como **`main.py`**, para execução automática após ligar ou reiniciar a placa. As bibliotecas `bmp280.py` e `ssd1306.py` também devem estar presentes no dispositivo. O arquivo `boot.py` do MicroPython foi mantido.

> A estrutura acima representa os arquivos utilizados na integração. O arquivo `app.py` originalmente criado para um servidor Flask separado não é necessário na arquitetura final, pois suas funções foram integradas ao `api.py`.

## 7. Pré-requisitos

- ESP32 com MicroPython instalado e firmware configurado.
- Sensores e display conectados conforme o circuito testado.
- Computador Windows com Python instalado e disponível no `PATH`.
- Mosquitto instalado e executando como serviço do Windows.
- ESP32 e computador conectados à mesma rede local, com conectividade entre eles.
- Bibliotecas Python `flask` e `paho-mqtt`.

Instale as dependências Python no PowerShell:

```powershell
python -m pip install flask paho-mqtt
```

A versão testada do ambiente incluiu Python 3.14.7, Flask 3.1.3 e Paho MQTT 2.1.0.

## 8. Configuração

### 8.1. Firmware do ESP32

1. Abra `firmware/Base_EstacaoMeteo.py` ou `firmware/main.py` no Thonny.
2. **Substitua os valores de exemplo** `SSID_DA_REDE_*`, `SENHA_DA_REDE_*` e `IP_DO_COMPUTADOR_NA_REDE_*` no dicionário `REDES` pelos dados da sua rede. O IP é o do computador que executa o Mosquitto, na rede correspondente.
3. Salve o firmware configurado no **Dispositivo MicroPython** com o nome `main.py`.
4. Mantenha as bibliotecas de sensores necessárias na memória da placa.
5. Reinicie o ESP32 e verifique as mensagens de conexão e publicação.

**Não publique senhas de Wi-Fi, credenciais ou outros dados privados no repositório.** Os arquivos de firmware desta versão pública contêm apenas valores de exemplo e **não conectam ao Wi-Fi enquanto não forem configurados**. Mantenha sua cópia funcional com credenciais reais apenas no computador/ESP32 e fora do GitHub.

### 8.2. Mosquitto

O broker deve aceitar conexões na porta MQTT configurada (nos testes, `1883`). No computador de desenvolvimento, o Mosquitto foi executado como serviço do Windows.

O receptor Python usa `localhost:1883`, enquanto o ESP32 utiliza o endereço IP do computador na rede local. **Esse IP pode mudar** quando a rede ou o roteador muda; revise a configuração do firmware quando necessário.

A configuração de teste permitiu conexões anônimas na rede local. **Não exponha o broker à internet dessa forma.** Em uma implantação fora do laboratório, configure autenticação e controles de acesso apropriados.

### 8.3. Caminho do inicializador

O arquivo `iniciar_estacao.bat` usa um caminho relativo à própria pasta do inicializador:

```bat
set "BACKEND=%~dp0backend"
```

Mantenha o `.bat` na pasta principal e o diretório `backend` ao lado dele. Se reorganizar as pastas, ajuste esse caminho.

## 9. Como executar

### Opção A — Inicializador do Windows

1. Ligue o ESP32 e aguarde a conexão Wi-Fi/MQTT.
2. Confirme que o serviço **Mosquitto** está em execução.
3. Certifique-se de que não existem instâncias anteriores do receptor ou da API.
4. Dê dois cliques em `iniciar_estacao.bat`.
5. O arquivo verifica a porta MQTT local, abre o receptor e a API em janelas separadas e acessa o dashboard em `http://127.0.0.1:5000`.
6. **Mantenha as janelas do receptor e da API abertas** enquanto o sistema estiver em uso.

Para encerrar, pressione `Ctrl+C` em cada janela. O inicializador não impede múltiplas execuções; evite abri-lo duas vezes.

### Opção B — Execução manual

No primeiro terminal PowerShell:

```powershell
cd CAMINHO_DA_PASTA\EstacaoMeteorologica\backend
python receptor_mqtt.py
```

Em outro terminal PowerShell:

```powershell
cd CAMINHO_DA_PASTA\EstacaoMeteorologica\backend
python api.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

**Não use o Go Live / Live Server para acessar este dashboard:** o site deve ser servido pelo Flask, pois consulta rotas HTTP do próprio backend.

## 10. Formato das mensagens MQTT

Tópico: `estacao/esp32/dados`

Exemplo ilustrativo de mensagem (valores apenas demonstrativos):

```json
{
  "temperatura_dht": 30,
  "umidade": 58,
  "temperatura_bmp": 30.33,
  "pressao": 928.66,
  "luminosidade": "ESCURO",
  "mq135": 203
}
```

As medições são publicadas aproximadamente a cada **5 segundos** durante a operação normal.

## 11. Banco de dados

O SQLite armazena as medições na tabela `medicoes`, contendo:

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | INTEGER | Identificador da medição |
| `temperatura_dht` | REAL | Temperatura do DHT11 |
| `umidade` | REAL | Umidade relativa |
| `temperatura_bmp` | REAL | Temperatura do BMP280 |
| `pressao` | REAL | Pressão atmosférica |
| `luminosidade` | TEXT | Estado CLARO/ESCURO |
| `mq135` | INTEGER | Leitura bruta do MQ-135 |
| `data_hora` | TEXT | Data e hora do registro, atribuídas pelo backend |

A tabela é criada automaticamente pelo receptor quando necessário. O histórico depende de o receptor ter estado ativo e gravado os dados; não há recuperação automática de medições perdidas enquanto o computador estava desligado.

## 12. Endpoints da API

| Método | Rota | Resultado |
| --- | --- | --- |
| GET | `/` | Página principal do dashboard |
| GET | `/api/ultima` | Última medição armazenada |
| GET | `/api/medicoes` | Medições recentes (padrão: 100) |
| GET | `/api/medicoes?limite=20` | Até 20 medições recentes |
| GET | `/api/total` | Quantidade total de medições |
| GET | `/api/historico?dias=7` | Histórico agregado por minuto dos últimos 7 dias |

O endpoint de histórico aceita períodos entre 1 e 30 dias e calcula médias por minuto para os campos numéricos. A interface oferece botões para 1, 3 e 7 dias. Os registros são consultados no banco SQLite.

## 13. Dashboard

O dashboard apresenta as leituras atuais de:

- Temperatura do DHT11;
- Temperatura do BMP280;
- Umidade;
- Pressão atmosférica;
- Estado de luminosidade;
- Leitura bruta do MQ-135.

Também mostra a data e hora da última medição e o total de registros. A página de histórico contém gráficos de temperatura do DHT11, umidade, pressão e leitura bruta do MQ-135, com filtros de período.

As informações atuais são consultadas periodicamente pela página. **Uma resposta HTTP `200` indica que a requisição foi atendida, mas não garante, por si só, que o ESP32 esteja enviando dados novos.** Para confirmar dados recentes, confira o horário da última medição e o receptor MQTT.

## 14. Testes realizados

Foram verificados durante o desenvolvimento:

- Leitura individual e integrada dos sensores conectados ao ESP32.
- Funcionamento do display OLED.
- Conexão Wi-Fi, incluindo tentativa de outra rede após falha na primeira.
- Publicação de mensagens MQTT e conexão ao Mosquitto.
- Recepção dos dados pelo `receptor_mqtt.py`.
- Inserção e consulta de registros no SQLite.
- Funcionamento das rotas HTTP do Flask.
- Exibição das medições e consulta do histórico no dashboard.
- Inicialização automática do firmware por meio de `main.py` após religar o ESP32.

O teste do firmware mostrou conexão à rede Wi-Fi, conexão ao broker e envio de dados após a inicialização automática.

## 15. Limitações e cuidados

- **MQ-135:** sem calibração, sem conversão validada para ppm e sem classificação confiável de qualidade do ar.
- **LDR:** informa somente CLARO ou ESCURO; não mede lux.
- **Temperatura:** DHT11 e BMP280 possuem características e fontes de erro diferentes; uma média simples entre os dois não deve ser apresentada como medição calibrada.
- **Dependência de rede:** o ESP32 precisa alcançar o broker MQTT no computador.
- **Dependência do computador:** o receptor, o banco e o servidor Flask funcionam no PC; o ESP32 não hospeda o dashboard.
- **Histórico:** apenas as medições efetivamente recebidas e salvas ficam disponíveis.
- **Gráficos:** o Chart.js é carregado por CDN; a biblioteca pode não carregar sem acesso à internet, mesmo que a rede local esteja funcionando.
- **Servidor Flask:** a versão pública mantém `debug=False`, mas ainda usa o servidor de desenvolvimento; para disponibilização na internet, utilize um servidor WSGI apropriado e revise a segurança do serviço.
- **Inicializador:** não gerencia automaticamente o encerramento dos serviços nem evita processos duplicados.

## 16. Possíveis melhorias

- Criar indicador de conexão e de atraso da última medição no dashboard.
- Melhorar a gestão dos processos do backend (iniciar, verificar e encerrar).
- Adicionar autenticação e reforçar a segurança da comunicação MQTT.
- Configurar o endereço do broker sem depender de IP fixado no firmware.
- Exportar histórico para CSV.
- Validar e calibrar sensores conforme as necessidades de medição.
- Preparar a aplicação para execução estável fora do ambiente de desenvolvimento.

## 17. Equipe e créditos

Projeto desenvolvido em grupo para a APS de Ciência da Computação - UNIP - Segundo Semestre

---

**Nota:** esta documentação descreve o protótipo integrado e testado em ambiente local. Os valores e resultados de medição não substituem instrumentos meteorológicos calibrados.

> **Publicação segura:** o banco SQLite real e arquivos de cache não fazem parte deste pacote. O `.gitignore` evita incluir esses arquivos em commits futuros, desde que ainda não tenham sido versionados. A versão original com senhas deve permanecer privada.
