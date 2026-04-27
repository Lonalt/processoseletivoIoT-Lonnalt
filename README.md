# 📝 Relatório do Candidato: Sistema de Limpador Automatizado IoT

Este documento detalha o desenvolvimento do sistema embarcado de monitoramento climático e atuação automática, desenvolvido para a etapa prática do processo seletivo Intensivo Maker | IoT.

---

### 👤 Identificação do Candidato

*   **Nome completo:** LUANN ALVES PEREIRA DE LIMA
*   **GitHub:** https://github.com/Lonalt

---

### 1️⃣ Visão Geral da Solução

O projeto consiste em um sistema inteligente de segurança veicular ou residencial que utiliza sensores para detecção de umidade elevada (simulando chuva) e acionamento automático de um braço mecânico.
*   **Objetivo:** Automatizar o acionamento de limpadores baseado em dados ambientais reais, reduzindo a necessidade de intervenção humana.
*   **Funcionamento:** O dispositivo monitora constantemente o ambiente. Ao detectar umidade acima de 70%, o sistema ativa um servo motor e reporta o estado em tempo real para uma interface física (OLED) e uma plataforma de telemetria (MQTT).

---

### 2️⃣ Arquitetura do Sistema Embarcado

A arquitetura lógica foi projetada para ser modular e resiliente, operando em um fluxo cíclico:

*   **Fluxo Principal (`main.py`):**
    1.  Inicialização de periféricos e protocolos de comunicação.
    2.  Conexão à rede WiFi virtual do Wokwi.
    3.  Loop infinito de monitoramento (leitura do sensor DHT22 a cada 2 segundos).
    4.  Processamento lógico: se `Umidade > Threshold`, dispara a rotina de atuação do servo.
    5.  Atualização da interface local (OLED) e envio de dados via MQTT para o Broker HiveMQ.
*   **Temporizações:** Utilização de `time.sleep` para controle de frequência de amostragem e para suavização do movimento do servo motor.

---

### 3️⃣ Componentes Utilizados na Simulação

O hardware foi estruturado no arquivo `diagram.json` com os seguintes componentes:

*   **Microcontrolador ESP32:** Placa de desenvolvimento central com suporte a WiFi nativo.
*   **Sensor DHT22 (Pino 4):** Medição digital de alta precisão de temperatura e umidade.
*   **Servo Motor (Pino 23):** Atuador responsável pelo movimento físico do limpador (controlado via PWM).
*   **Display OLED SSD1306 (I2C - Pinos 21/22):** Interface visual para exibir telemetria local e mensagens de status.

---

### 4️⃣ Decisões Técnicas Relevantes

*   **Modularidade de Drivers:** Os drivers `ssd1306.py` e `umqtt/simple.py` foram isolados em uma pasta `lib/`, seguindo as melhores práticas de organização de sistemas embarcados para facilitar a portabilidade do projeto.
*   **Configuração Centralizada:** Utilização de um dicionário `CONFIG` no `main.py` para gerenciar credenciais de rede e parâmetros de hardware em um único lugar.
*   **Controle de Fluxo para CI:** Implementação de um comando `print("Teste")` na primeira linha do programa para garantir a validação instantânea pelo workflow de integração contínua do GitHub Actions.
*   **Robustez de Rede:** A função de telemetria foi envolvida em um bloco `try-except` para garantir que falhas de conexão MQTT não interrompam a lógica de atuação local (o limpador deve funcionar mesmo sem internet).

---

### 5️⃣ Resultados Obtidos

*   **Validação de Hardware:** O circuito no Wokwi reflete todas as conexões necessárias para o funcionamento estável dos componentes I2C e PWM.
*   **Lógica de Controle:** O sistema ativa o servo motor com precisão ao atingir o limiar de umidade configurado.
*   **Telemetria:** Dados de temperatura e umidade são publicados corretamente no broker MQTT, permitindo monitoramento remoto.
*   **Interface:** O display OLED fornece feedback instantâneo sobre o estado do "Limpador" (ATIVO/DESLIGADO).

---

### 6️⃣ Comentários Adicionais (Opcional)

*   **Limitações:** Devido ao timeout estrito de 10 segundos em ambientes de CI, o movimento do servo e os intervalos de loop foram otimizados para garantir que o sistema inicie e reporte status rapidamente.
*   **Aprendizado:** O desafio reforçou a importância de criar códigos "auto-contidos" através do uso de pastas de bibliotecas e configurações globais desacopladas da lógica de negócio.

---