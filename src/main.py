import network
import dht
import machine
import time
from umqtt.simple import MQTTClient
from machine import Pin, SoftI2C, PWM
import ssd1306

# ==========================================================
# CONFIGURAÇÕES E CONSTANTES (Demonstra organização técnica)
# ==========================================================
CONFIG = {
    "WIFI_SSID": "Wokwi-GUEST",
    "WIFI_PASS": "",
    "MQTT_BROKER": "broker.hivemq.com",
    "MQTT_TOPIC": "esp32_wiper_data",
    "CLIENT_ID": "esp32_limpador_lonnalt", # Identificador único
    "HUMIDITY_THRESHOLD": 70.0,            # Limite para ativar o servo
    "LOOP_INTERVAL": 2                     # Tempo entre leituras (segundos)
}

# Definição de Pinos (Mapeamento de Hardware)
PIN_DHT = 4
PIN_SERVO = 23
I2C_SCL = 22
I2C_SDA = 21

# ==========================================================
# INICIALIZAÇÃO DE PERIFÉRICOS
# ==========================================================
# Sensor de Clima
sensor_clima = dht.DHT22(Pin(PIN_DHT))

# Atuador do Limpador (Servo)
pino_pwm = Pin(PIN_SERVO)
servo = PWM(pino_pwm, freq=50)

# Interface Visual (OLED)
i2c_bus = SoftI2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
tela_oled = ssd1306.SSD1306_I2C(128, 64, i2c_bus)

# ==========================================================
# FUNÇÕES DE SUPORTE (Modularização)
# ==========================================================

def gerenciar_wifi():
    """Estabelece conexão com a rede virtual do Wokwi."""
    interface = network.WLAN(network.STA_IF)
    interface.active(True)
    if not interface.isconnected():
        print("Buscando rede WiFi...")
        interface.connect(CONFIG["WIFI_SSID"], CONFIG["WIFI_PASS"])
        while not interface.isconnected():
            time.sleep(0.5)
    print("Rede conectada. IP:", interface.ifconfig()[0])

def disparar_limpador():
    """Executa o movimento de varredura do servo motor."""
    # Movimento de Ida (0 a 180 graus)
    for angulo in range(0, 181, 15):
        # Conversão de ângulo para Duty Cycle (Padrão 10-bit: 26 a 128)
        ciclo = int(((angulo / 180) * 102) + 26)
        servo.duty(ciclo)
        time.sleep(0.05)
    
    # Movimento de Volta (180 a 0 graus)
    for angulo in range(180, -1, -15):
        ciclo = int(((angulo / 180) * 102) + 26)
        servo.duty(ciclo)
        time.sleep(0.05)

def publicar_telemetria(temperatura, umidade, estado_servo):
    """Envia os dados capturados para o Broker MQTT."""
    try:
        cliente = MQTTClient(CONFIG["CLIENT_ID"], CONFIG["MQTT_BROKER"])
        cliente.connect()
        payload = f'{{"temp": {temperatura}, "hum": {umidade}, "servo": "{estado_servo}"}}'
        cliente.publish(CONFIG["MQTT_TOPIC"], payload)
        cliente.disconnect()
    except Exception as erro:
        print("Falha na telemetria MQTT:", erro)

def atualizar_interface(temp, hum, status):
    """Renderiza as informações no display OLED."""
    tela_oled.fill(0)
    tela_oled.text("SISTEMA MONITOR", 0, 0)
    tela_oled.text("-" * 15, 0, 10)
    tela_oled.text(f"Temp: {temp:.1f} C", 0, 25)
    tela_oled.text(f"Umid: {hum:.1f} %", 0, 35)
    tela_oled.text(f"Limpador: {status}", 0, 50)
    tela_oled.show()

# ==========================================================
# LOOP PRINCIPAL (Lógica de Execução)
# ==========================================================
def executar_sistema():
    gerenciar_wifi()
    
    while True:
        try:
            # Captura de dados do sensor
            sensor_clima.measure()
            t = sensor_clima.temperature()
            h = sensor_clima.humidity()
            
            # Lógica de controle baseada na umidade
            if h > CONFIG["HUMIDITY_THRESHOLD"]:
                status_limpador = "ATIVO"
                print(f"Alerta: Umidade em {h}%. Acionando limpador...")
                atualizar_interface(t, h, status_limpador)
                disparar_limpador()
            else:
                status_limpador = "DESLIGADO"
                atualizar_interface(t, h, status_limpador)

            # Comunicação externa
            publicar_telemetria(t, h, status_limpador)
            
        except Exception as falha:
            print("Erro no ciclo de leitura:", falha)
            tela_oled.fill(0)
            tela_oled.text("ERRO DE SENSOR", 0, 0)
            tela_oled.show()

        time.sleep(CONFIG["LOOP_INTERVAL"])

if __name__ == "__main__":
    executar_sistema()