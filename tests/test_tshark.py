import sys

import pytest

from app.utils.tshark import run_tshark


async def test_devolve_o_stdout_do_processo():
    output = await run_tshark([sys.executable, "-c", "print('ok')"], timeout=10)

    assert output.strip() == "ok"


async def test_falha_do_processo_vira_runtime_error_com_o_stderr():
    with pytest.raises(RuntimeError, match="boom"):
        await run_tshark(
            [sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"],
            timeout=10,
        )


async def test_timeout_mata_o_processo_e_avisa():
    with pytest.raises(RuntimeError, match="did not finish within 1s"):
        await run_tshark([sys.executable, "-c", "import time; time.sleep(10)"], timeout=1)
