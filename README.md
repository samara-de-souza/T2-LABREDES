# Monitor de Tráfego de Rede em Tempo Real

## 📋 Resumo do Trabalho

Este projeto consiste no desenvolvimento de uma ferramenta para monitoramento de tráfego de rede em tempo real utilizando **raw sockets**. A aplicação deve ser capaz de capturar, interpretar e classificar pacotes de rede, fornecendo uma interface de usuário simples para visualizar contadores e estatísticas de tráfego, além de manter um histórico dos pacotes recebidos em arquivos de log.

### 🎯 Objetivos Específicos

- Desenvolvimento de uma aplicação usando sockets raw
- Estudo do funcionamento dos protocolos de rede e relacionamento entre camadas
- Compreensão da estruturação de pacotes de dados e interpretação para extração de informações
- Análise do tráfego de rede local e tipos de protocolos comuns
- Utilização de uma estrutura de rede pré-definida

### 🏗️ Arquitetura da Rede

O sistema funciona em uma rede onde:
- **Clientes** acessam a internet através de um **servidor proxy**
- Ambos residem na mesma LAN
- O acesso externo é feito através de um programa cliente do proxy
- O tráfego é encapsulado em pacotes IP com informações forjadas para segurança
- O monitor executa na máquina servidor proxy

### 📊 Arquivos de Log

A aplicação deve gerar três arquivos CSV em tempo real:

1. **camada2.csv** - Camada de Enlace (Ethernet)
   - Data/hora de captura
   - MAC origem e destino
   - EtherType (protocolo)
   - Tamanho do quadro

2. **camada3.csv** - Camada de Rede (IP)
   - Data/hora de captura
   - Nome do protocolo (IPv4/IPv6)
   - IP origem e destino
   - Número do protocolo
   - Tamanho do pacote

3. **camada4.csv** - Camada de Transporte (TCP/UDP)
   - Data/hora de captura
   - Nome do protocolo (TCP/UDP/etc.)
   - IP origem e destino
   - Portas origem e destino
   - Tamanho do pacote

---

## 📋 Divisão de Tarefas

### 🎯 **Tarefa 1: Configuração do Ambiente**
- [ ] Instalação das dependências (build-essentials, iptables)
- [ ] Compilação do programa túnel (`make`)
- [ ] Configuração da interface virtual tun0
- [ ] Verificação do roteamento no kernel

### 🎯 **Tarefa 2: Implementação dos Raw Sockets**
- [ ] Criação de socket raw para captura de pacotes
- [ ] Configuração da interface tun0 para monitoramento
- [ ] Implementação da captura de pacotes em tempo real
- [ ] Tratamento de erros e exceções

### 🎯 **Tarefa 3: Análise de Protocolos - Camada 2 (Ethernet)**
- [ ] Parsing de cabeçalhos Ethernet
- [ ] Extração de endereços MAC (origem/destino)
- [ ] Identificação do EtherType
- [ ] Cálculo do tamanho do quadro
- [ ] Geração do arquivo `camada2.csv`

### 🎯 **Tarefa 4: Análise de Protocolos - Camada 3 (IP)**
- [ ] Parsing de cabeçalhos IP (IPv4/IPv6)
- [ ] Extração de endereços IP (origem/destino)
- [ ] Identificação do protocolo de transporte
- [ ] Cálculo do tamanho do pacote
- [ ] Geração do arquivo `camada3.csv`

### 🎯 **Tarefa 5: Análise de Protocolos - Camada 4 (Transporte)**
- [ ] Parsing de cabeçalhos TCP/UDP
- [ ] Extração de portas (origem/destino)
- [ ] Identificação de outros protocolos (ICMP, etc.)
- [ ] Cálculo do tamanho do pacote
- [ ] Geração do arquivo `camada4.csv`

### 🎯 **Tarefa 6: Interface de Usuário**
- [ ] Desenvolvimento da interface modo texto
- [ ] Implementação de contadores por tipo de pacote
- [ ] Exibição de estatísticas em tempo real
- [ ] Atualização dinâmica dos dados

### 🎯 **Tarefa 7: Sistema de Logging**
- [ ] Implementação de escrita em arquivos CSV
- [ ] Atualização em tempo real dos logs
- [ ] Tratamento de concorrência na escrita
- [ ] Verificação de integridade dos dados

### 🎯 **Tarefa 8: Classificação e Estatísticas**
- [ ] Implementação de contadores por protocolo
- [ ] Cálculo de estatísticas de tráfego
- [ ] Identificação de padrões de tráfego
- [ ] Geração de relatórios

### 🎯 **Tarefa 9: Testes e Validação**
- [ ] Testes com diferentes tipos de tráfego
- [ ] Validação da captura de pacotes
- [ ] Verificação da precisão dos logs
- [ ] Testes de performance

### 🎯 **Tarefa 10: Documentação e Entrega**
- [ ] Criação do relatório técnico
- [ ] Captura de screenshots demonstrativos
- [ ] Documentação do código
- [ ] Preparação do arquivo de entrega (.tar.gz/.zip)

---

## 🚀 Como Executar

### Modo Servidor Proxy
```bash
sudo ./traffic_tunnel <interface_do_servidor> -s <ip_do_servidor>
```

### Modo Cliente
```bash
sudo ./traffic_tunnel <interface_do_cliente> -c <ip_do_cliente> -t
```

### Verificação da Interface
```bash
ifconfig tun0
# ou
ip addr show tun0
```

---

## 📅 Prazo de Entrega
- **Data**: 23/06
- **Formato**: Arquivo .tar.gz ou .zip
- **Conteúdo**: Código fonte + relatório + screenshots
- **Apresentação**: Todos os grupos devem estar aptos a apresentar desde o início da aula

---

## 👥 Trabalho em Equipe
- **Formato**: Duplas ou trios
- **Responsabilidade**: Todos os integrantes devem estar preparados para apresentar
- **Entrega**: Apenas um integrante envia pelo Moodle

---

## 🔧 Dependências
- Ambiente Linux
- build-essentials
- iptables
- Interface de rede configurada
- Permissões de administrador (sudo) 
