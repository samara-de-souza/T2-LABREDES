FROM python:3.11-slim

# Instala dependências de sistema necessárias para raw sockets e curses
RUN apt-get update && \
    apt-get install -y --no-install-recommends iproute2 net-tools && \
    rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Diretório para logs
RUN mkdir -p /logs
ENV LOG_DIR=/logs

# Interface padrão
ENV INTERFACE=tun0

ENTRYPOINT ["python", "src/monitor.py", "tun0"] 