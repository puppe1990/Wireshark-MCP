from app.utils.pagination import DEFAULT_MAX_CHARS, paginate_text


def test_texto_menor_que_o_limite_volta_inteiro():
    chunk, meta = paginate_text("abc")

    assert chunk == "abc"
    assert meta["truncated"] is False
    assert meta["next_offset"] is None
    assert meta["total_length"] == 3
    assert meta["message"] == "Full result returned."


def test_corte_exato_no_limite_nao_marca_truncado():
    chunk, meta = paginate_text("abcd", offset=0, max_chars=4)

    assert chunk == "abcd"
    assert meta["truncated"] is False


def test_texto_maior_que_o_limite_devolve_a_proxima_janela():
    chunk, meta = paginate_text("0123456789", offset=0, max_chars=4)

    assert chunk == "0123"
    assert meta["truncated"] is True
    assert meta["next_offset"] == 4
    assert "offset=4" in meta["message"]


def test_offset_no_meio_continua_de_onde_parou():
    chunk, meta = paginate_text("0123456789", offset=4, max_chars=4)

    assert chunk == "4567"
    assert meta["next_offset"] == 8


def test_offset_alem_do_fim_devolve_vazio_sem_truncar():
    chunk, meta = paginate_text("abc", offset=10, max_chars=4)

    assert chunk == ""
    assert meta["truncated"] is False
    assert meta["next_offset"] is None


def test_limite_padrao_e_de_duzentos_mil_caracteres():
    assert DEFAULT_MAX_CHARS == 200_000
