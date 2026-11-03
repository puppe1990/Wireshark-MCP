import pytest

import app.config as config
import app.tools.conversations as conversations
import app.tools.discovery as discovery
import app.tools.interfaces as interfaces
import app.tools.live_capture as live_capture
import app.tools.packets as packets
import app.tools.statistics as statistics
import app.tools.streams as streams


class FakeTshark:
    """Captura os comandos montados e devolve um stdout fixo."""

    def __init__(self, output: str = ""):
        self.output = output
        self.calls: list[list[str]] = []

    async def __call__(self, cmd: list[str], timeout: int | None = None) -> str:
        self.calls.append(cmd)
        return self.output


@pytest.fixture(autouse=True)
def tshark_path(monkeypatch):
    monkeypatch.setattr(config.settings, "TSHARK_PATH", "tshark")


async def test_query_packets_monta_campos_filtro_e_limita_linhas(monkeypatch):
    fake = FakeTshark("1|GET\n2|POST\n3|GET\n")
    monkeypatch.setattr(packets, "run_tshark", fake)

    result = await packets.query_packets(
        "/tmp/x.pcap",
        ["frame.number", "http.request.method"],
        display_filter="http",
        limit=2,
    )

    cmd = fake.calls[0]
    assert cmd[:4] == ["tshark", "-r", "/tmp/x.pcap", "-T"]
    assert cmd.count("-e") == 2
    assert cmd[cmd.index("-Y") + 1] == "http"
    assert cmd[-2:] == ["-E", "separator=|"]
    assert result["fields"] == ["frame.number", "http.request.method"]
    assert result["rows"] == [["1", "GET"], ["2", "POST"]]


async def test_query_packets_sem_filtro_nao_passa_y(monkeypatch):
    fake = FakeTshark("1|\n")
    monkeypatch.setattr(packets, "run_tshark", fake)

    await packets.query_packets("/tmp/x.pcap", ["frame.number"])

    assert "-Y" not in fake.calls[0]


async def test_discover_protocols_usa_io_phs_e_pagina(monkeypatch):
    fake = FakeTshark("eth.ip.tcp.data\n")
    monkeypatch.setattr(discovery, "run_tshark", fake)

    result = await discovery.discover_protocols("/tmp/x.pcap", offset=0, max_chars=4)

    assert fake.calls[0][-3:] == ["-q", "-z", "io,phs"]
    assert result["protocol_hierarchy"] == "eth."
    assert result["truncated"] is True
    assert result["next_offset"] == 4


async def test_protocol_statistics_usa_io_stat(monkeypatch):
    fake = FakeTshark("stats\n")
    monkeypatch.setattr(statistics, "run_tshark", fake)

    result = await statistics.protocol_statistics("/tmp/x.pcap")

    assert fake.calls[0][-2:] == ["-z", "io,stat,1"]
    assert result["statistics"] == "stats\n"


async def test_inspect_stream_segue_o_stream_pedido(monkeypatch):
    fake = FakeTshark("hello\n")
    monkeypatch.setattr(streams, "run_tshark", fake)

    result = await streams.inspect_stream("/tmp/x.pcap", "tcp", 3)

    assert fake.calls[0][-2:] == ["-z", "follow,tcp,ascii,3"]
    assert result["stream_data"] == "hello\n"


async def test_analyze_conversations_usa_ip_por_padrao(monkeypatch):
    fake = FakeTshark("conv\n")
    monkeypatch.setattr(conversations, "run_tshark", fake)

    result = await conversations.analyze_conversations("/tmp/x.pcap")

    assert fake.calls[0][-2:] == ["-z", "conv,ip"]
    assert result["conversation_type"] == "ip"


async def test_list_interfaces_so_mantem_linhas_com_indice(monkeypatch):
    fake = FakeTshark("1. en0 (Wi-Fi)\nlinha sem índice\n2. lo0 (Loopback)\n")
    monkeypatch.setattr(interfaces, "run_tshark", fake)

    result = await interfaces.list_interfaces()

    assert fake.calls[0] == ["tshark", "-D"]
    assert result["interfaces"] == ["1. en0 (Wi-Fi)", "2. lo0 (Loopback)"]


async def test_capture_live_sem_interface_pede_para_escolher(monkeypatch):
    fake = FakeTshark("1. en0 (Wi-Fi)\n2. lo0 (Loopback)\n")
    monkeypatch.setattr(live_capture, "run_tshark", fake)

    result = await live_capture.start_live_capture()

    assert result["status"] == "user_input_required"
    assert result["available_interfaces"] == ["1. en0 (Wi-Fi)", "2. lo0 (Loopback)"]


async def test_capture_live_recusa_interface_inexistente(monkeypatch):
    fake = FakeTshark("1. en0 (Wi-Fi)\n2. lo0 (Loopback)\n")
    monkeypatch.setattr(live_capture, "run_tshark", fake)

    result = await live_capture.start_live_capture(interface="wlan999")

    assert result["status"] == "invalid_interface"
    assert result["available_interfaces"] == ["1. en0 (Wi-Fi)", "2. lo0 (Loopback)"]
