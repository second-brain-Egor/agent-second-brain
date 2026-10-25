"""Живые лимиты подписки: выбор недели, честные ошибки и отсутствие запуска модели."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from d_brain.services import codex_limits


RESET = 1793383152
EXPECTED = (
    "📊 Недельный лимит Codex: осталось <b>22%</b>.\n\n"
    "Сброс — <b>30.10.2026 в 20:59 по Москве</b>."
)


def bucket(used=78, reset=RESET, *, weekly_slot="primary"):
    result = {
        "limitId": "codex",
        "primary": {"usedPercent": 7, "windowDurationMins": 300, "resetsAt": RESET},
        "secondary": None,
    }
    result[weekly_slot] = {
        "usedPercent": used,
        "windowDurationMins": 10080,
        "resetsAt": reset,
    }
    return result


@pytest.mark.parametrize("slot", ["primary", "secondary"])
def test_weekly_window_is_identified_by_duration_and_reset_is_moscow(slot):
    payload = {"rateLimits": bucket(weekly_slot=slot)}
    assert codex_limits.parse_weekly_limits(payload) == EXPECTED


def test_codex_bucket_takes_precedence_over_other_limit():
    unrelated = bucket(used=3)
    unrelated["limitId"] = "other"
    payload = {
        "rateLimits": unrelated,
        "rateLimitsByLimitId": {"other": unrelated, "codex": bucket()},
    }
    assert codex_limits.parse_weekly_limits(payload) == EXPECTED


@pytest.mark.parametrize("used,left", [(0, 100), (100, 0)])
def test_zero_and_fully_used_limits_are_valid(used, left):
    text = codex_limits.parse_weekly_limits({"rateLimits": bucket(used=used)})
    assert f"осталось <b>{left}%</b>" in text


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"rateLimits": None},
        {"rateLimits": {"primary": None, "secondary": None}},
        {"rateLimits": {"primary": {
            "usedPercent": 7, "windowDurationMins": 300, "resetsAt": RESET,
        }}},
        {"rateLimits": {"primary": {"usedPercent": 7, "resetsAt": RESET}}},
    ],
)
def test_missing_weekly_window_is_an_error(payload):
    with pytest.raises(codex_limits.CodexLimitsError):
        codex_limits.parse_weekly_limits(payload)


@pytest.mark.parametrize("value", [None, True, -1, 101, "invalid", float("nan")])
def test_invalid_used_percent_is_an_error(value):
    with pytest.raises(codex_limits.CodexLimitsError):
        codex_limits.parse_weekly_limits({"rateLimits": bucket(used=value)})


@pytest.mark.parametrize("value", [None, True, 0, -1, "invalid", 10**30])
def test_invalid_reset_is_an_error(value):
    with pytest.raises(codex_limits.CodexLimitsError):
        codex_limits.parse_weekly_limits({"rateLimits": bucket(reset=value)})


def fake_process(*, payload=None, error=None, eof=False, read_error=None):
    """Ответ зависит от настоящего id запроса; дополнительные уведомления допустимы."""
    stdout = asyncio.StreamReader()
    requests = []
    stdin = SimpleNamespace(drain=AsyncMock(), close=Mock(), wait_closed=AsyncMock())
    proc = SimpleNamespace(
        stdin=stdin, stdout=stdout, stderr=None, returncode=None,
        wait=AsyncMock(return_value=0), terminate=Mock(), kill=Mock(), requests=requests,
    )

    def write(raw):
        for line in raw.splitlines():
            request = json.loads(line)
            requests.append(request)
            if request["method"] == "initialize":
                response = {"id": request["id"], "result": {"userAgent": "test"}}
            elif request["method"] == "account/rateLimits/read":
                if eof:
                    stdout.feed_eof()
                    continue
                if read_error:
                    stdout.set_exception(read_error)
                    continue
                response = {"id": request["id"]}
                if error:
                    response["error"] = error
                else:
                    response["result"] = payload or {"rateLimits": bucket()}
            else:
                continue
            stdout.feed_data((json.dumps(response) + "\n").encode())

    stdin.write = Mock(side_effect=write)
    return proc


async def test_each_read_uses_fresh_subprocess_and_only_read_only_methods(tmp_path, monkeypatch):
    processes = [fake_process(), fake_process(payload={"rateLimits": bucket(used=80)})]
    launch = AsyncMock(side_effect=processes)
    monkeypatch.setattr(codex_limits.asyncio, "create_subprocess_exec", launch)

    first = await codex_limits.read_weekly_limits("/usr/bin/codex", tmp_path)
    second = await codex_limits.read_weekly_limits("/usr/bin/codex", tmp_path)

    assert first == EXPECTED
    assert "осталось <b>20%</b>" in second
    assert launch.await_count == 2
    for call, proc in zip(launch.await_args_list, processes, strict=True):
        assert call.args[0] == "/usr/bin/codex"
        assert "app-server" in call.args
        assert str(call.kwargs["cwd"]) == str(tmp_path)
        assert [request["method"] for request in proc.requests] == [
            "initialize", "initialized", "account/rateLimits/read",
        ]
        assert proc.wait.await_count >= 1


async def test_rpc_error_does_not_expose_raw_server_message(tmp_path, monkeypatch, caplog):
    secret = "SENSITIVE_SERVER_DETAIL"
    proc = fake_process(error={"code": -32000, "message": secret})
    monkeypatch.setattr(codex_limits.asyncio, "create_subprocess_exec", AsyncMock(return_value=proc))

    with pytest.raises(codex_limits.CodexLimitsError) as caught:
        await codex_limits.read_weekly_limits("codex", tmp_path)

    assert secret not in str(caught.value)
    assert secret not in caplog.text
    assert proc.wait.await_count >= 1


@pytest.mark.parametrize("failure", ["eof", "timeout"])
async def test_broken_response_becomes_error_and_process_is_reaped(failure, tmp_path, monkeypatch):
    proc = fake_process(eof=failure == "eof", read_error=TimeoutError() if failure == "timeout" else None)
    monkeypatch.setattr(codex_limits.asyncio, "create_subprocess_exec", AsyncMock(return_value=proc))

    with pytest.raises(codex_limits.CodexLimitsError):
        await codex_limits.read_weekly_limits("codex", tmp_path)

    assert proc.wait.await_count >= 1

