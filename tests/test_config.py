import app.config as config


def test_defaults_do_settings(monkeypatch):
    monkeypatch.delenv("TSHARK_PATH", raising=False)

    settings = config.Settings(_env_file=None)

    assert settings.TSHARK_PATH == "tshark"
    assert settings.MAX_PACKETS == 5000
    assert settings.CAPTURE_DIR.endswith("captures")
    assert settings.LOG_DIR.endswith("logs")


def test_variavel_de_ambiente_sobrepoe_o_padrao(monkeypatch):
    monkeypatch.setenv("TSHARK_PATH", "/opt/tshark/bin/tshark")

    settings = config.Settings(_env_file=None)

    assert settings.TSHARK_PATH == "/opt/tshark/bin/tshark"
