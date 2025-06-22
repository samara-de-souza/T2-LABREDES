## Monitor de Tráfego em Tempo Real

Este projeto implementa um monitor de tráfego que captura pacotes na interface `tun0` utilizando sockets RAW, exibe contadores em tempo real na tela e grava logs das camadas 2, 3 e 4 em arquivos CSV.

### Estrutura de Diretórios
- `src/monitor.py` — implementação principal.
- `logs/` — diretório criado automaticamente para armazenar `camada2.csv`, `camada3.csv` e `camada4.csv`.
- `Dockerfile` — imagem Docker para executar o monitor.
- `docker-compose.yml` — orquestração recomendada.

### Execução sem Docker
Requer Python ≥ 3.9 executando em Linux (necessário suporte a `AF_PACKET`).
```bash
sudo python src/monitor.py tun0
```

### Construindo a imagem Docker
```bash
# Na raiz do projeto
docker build -t traffic-monitor .
```

### Executando via Docker (linha de comando)
```bash
docker run --rm -it \
  --net=host \
  --cap-add=NET_ADMIN --cap-add=NET_RAW \
  -v $(pwd)/logs:/logs \
  traffic-monitor
```

### Executando via Docker-Compose
```bash
docker compose up --build
```

O contêiner será iniciado com acesso à rede do host (`network_mode: host`) e capacidades necessárias para sockets RAW. Os CSVs gerados ficam montados em `./logs`.

### Visualizando os logs em tempo real
Em outro terminal:
```bash
tail -f logs/camada2.csv
```

### Encerrando
Pressione `Ctrl+C` na interface de texto para finalizar a captura. 