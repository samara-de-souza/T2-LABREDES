import socket
import struct
import datetime
import csv
import os
import curses
import signal
import sys
from typing import Tuple

# Caminhos para os arquivos de log
LOG_DIR = os.environ.get("LOG_DIR", "logs")
CAMADA2_CSV = os.path.join(LOG_DIR, "camada2.csv")
CAMADA3_CSV = os.path.join(LOG_DIR, "camada3.csv")
CAMADA4_CSV = os.path.join(LOG_DIR, "camada4.csv")

# Cabeçalhos dos CSVs
CSV_HEADERS = {
    CAMADA2_CSV: [
        "timestamp",
        "src_mac",
        "dst_mac",
        "ethertype",
        "frame_size_bytes",
    ],
    CAMADA3_CSV: [
        "timestamp",
        "protocol_name",
        "src_ip",
        "dst_ip",
        "inner_proto_id",
        "packet_size_bytes",
    ],
    CAMADA4_CSV: [
        "timestamp",
        "protocol_name",
        "src_ip",
        "src_port",
        "dst_ip",
        "dst_port",
        "segment_size_bytes",
    ],
}

# Contadores globais a serem exibidos na interface
counters_l2 = {}
counters_l3 = {}
counters_l4 = {}


def ensure_logs():
    """Cria diretório e arquivos CSV com cabeçalhos se ainda não existirem."""
    os.makedirs(LOG_DIR, exist_ok=True)
    for path, headers in CSV_HEADERS.items():
        if not os.path.isfile(path):
            with open(path, "w", newline="") as f:
                csv.writer(f).writerow(headers)


def mac_addr(raw: bytes) -> str:
    """Converte 6 bytes em endereço MAC legível."""
    return ":".join(f"{b:02x}" for b in raw)


def ipv4_addr(raw: bytes) -> str:
    return ".".join(str(b) for b in raw)


def parse_ethernet_header(packet: bytes) -> Tuple[str, str, int]:
    dst_mac, src_mac, proto = struct.unpack("!6s6sH", packet[:14])
    return mac_addr(src_mac), mac_addr(dst_mac), proto


def parse_ipv4_header(packet: bytes) -> Tuple[str, str, int, int]:
    version_header_len = packet[0]
    header_len = (version_header_len & 0x0F) * 4
    total_length = struct.unpack("!H", packet[2:4])[0]
    proto = packet[9]
    src = ipv4_addr(packet[12:16])
    dst = ipv4_addr(packet[16:20])
    return src, dst, proto, total_length


def parse_tcp_udp_header(packet: bytes) -> Tuple[int, int]:
    src_port, dst_port = struct.unpack("!HH", packet[:4])
    return src_port, dst_port


# Mapas de protocolos
ETHERTYPE_MAP = {0x0800: "IPv4", 0x0806: "ARP", 0x86DD: "IPv6"}
IP_PROTO_MAP = {1: "ICMP", 6: "TCP", 17: "UDP"}


class TrafficMonitor:
    def __init__(self, interface: str = "tun0") -> None:
        self.interface = interface
        self.running = True
        ensure_logs()
        self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        self.sock.bind((interface, 0))
        self.sock.setblocking(False)
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, *args):
        self.running = False

    def run(self):
        curses.wrapper(self._run_curses)

    def _run_curses(self, stdscr):
        stdscr.nodelay(True)
        stdscr.clear()
        while self.running:
            try:
                packet, _ = self.sock.recvfrom(65535)
                self.process_packet(packet)
            except BlockingIOError:
                pass  # Sem pacote
            except Exception as e:
                stdscr.addstr(0, 0, f"Erro: {e}\n")
            self.draw_ui(stdscr)

    def process_packet(self, packet: bytes):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        frame_size = len(packet)

        # Primeiro tentamos interpretar como quadro Ethernet
        is_ethernet = len(packet) >= 14
        eth_proto = None
        src_mac = dst_mac = "N/A"
        ip_payload = b""

        if is_ethernet:
            src_mac, dst_mac, eth_proto = parse_ethernet_header(packet)
            ip_payload = packet[14:]
        
        # Se não for Ethernet reconhecido, ou se o EtherType não indicar IPv4/IPv6,
        # pode ser um dispositivo TUN (camada 3 pura). Nesse caso, tratamos o pacote
        # como IPv4 se o primeiro nibble for 4 ou 6.
        if not is_ethernet or eth_proto not in (0x0800, 0x86DD, 0x0806):
            version = packet[0] >> 4
            if version in (4, 6):
                # Pacote IP bruto vindo de tun
                eth_proto = 0x0800 if version == 4 else 0x86DD
                ip_payload = packet  # todo o pacote é cabeçalho IP + payload

        # Atualiza contador L2 (mesmo para TUN identificamos pelo eth_proto mapeado)
        eth_name = ETHERTYPE_MAP.get(eth_proto, hex(eth_proto) if eth_proto is not None else "RAW")
        counters_l2[eth_name] = counters_l2.get(eth_name, 0) + 1

        # Log camada 2 somente se havia cabeçalho Ethernet; em TUN, macs ficam N/A
        with open(CAMADA2_CSV, "a", newline="") as f:
            csv.writer(f).writerow([
                timestamp,
                src_mac,
                dst_mac,
                f"0x{eth_proto:04x}" if eth_proto is not None else "RAW",
                frame_size,
            ])

        # Processa IPv4 se aplicável
        if eth_proto == 0x0800 and len(ip_payload) >= 20:
            ip_header = ip_payload
            src_ip, dst_ip, proto, total_len = parse_ipv4_header(ip_header)
            proto_name = IP_PROTO_MAP.get(proto, str(proto))
            counters_l3[proto_name] = counters_l3.get(proto_name, 0) + 1

            # Log camada 3
            with open(CAMADA3_CSV, "a", newline="") as f:
                csv.writer(f).writerow([
                    timestamp,
                    "IPv4",
                    src_ip,
                    dst_ip,
                    proto,
                    total_len,
                ])

            # Camada 4 (TCP/UDP)
            if proto in (6, 17) and len(ip_header) >= 20:
                ip_header_len = (ip_header[0] & 0x0F) * 4
                transport_pkt = ip_header[ip_header_len:]
                if len(transport_pkt) >= 4:
                    src_port, dst_port = parse_tcp_udp_header(transport_pkt)
                    proto_upper = "TCP" if proto == 6 else "UDP"
                    counters_l4[proto_upper] = counters_l4.get(proto_upper, 0) + 1
                    with open(CAMADA4_CSV, "a", newline="") as f:
                        csv.writer(f).writerow([
                            timestamp,
                            proto_upper,
                            src_ip,
                            src_port,
                            dst_ip,
                            dst_port,
                            total_len - ip_header_len,
                        ])

    def draw_ui(self, stdscr):
        stdscr.erase()
        stdscr.addstr(0, 0, "Monitor de Tráfego em Tempo Real - Interface tun0")

        # Exibe L2
        stdscr.addstr(2, 0, "Camada 2 (EtherType):")
        row = 3
        for proto, cnt in counters_l2.items():
            stdscr.addstr(row, 2, f"{proto}: {cnt}")
            row += 1

        # Exibe L3
        row += 1
        stdscr.addstr(row, 0, "Camada 3 (Protocolos IP):")
        row += 1
        for proto, cnt in counters_l3.items():
            stdscr.addstr(row, 2, f"{proto}: {cnt}")
            row += 1

        # Exibe L4
        row += 1
        stdscr.addstr(row, 0, "Camada 4 (TCP/UDP):")
        row += 1
        for proto, cnt in counters_l4.items():
            stdscr.addstr(row, 2, f"{proto}: {cnt}")
            row += 1

        stdscr.refresh()


if __name__ == "__main__":
    interface = sys.argv[1] if len(sys.argv) > 1 else "tun0"
    monitor = TrafficMonitor(interface)
    monitor.run() 