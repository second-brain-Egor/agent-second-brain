"""Страж шведского выхода (deploy/vpn-guard/vpn-guard): разбор подписки, выбор и замена узла."""
import base64
import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "deploy" / "vpn-guard" / "vpn-guard"
UUID = "11111111-2222-3333-4444-555555555555"
OTHER = "99999999-8888-7777-6666-555555555555"


def reality_link(name="Stockholm Sweden Extra", host="203.0.113.10", user=UUID, port=443):
    return (f"vless://{user}@{host}:{port}?encryption=none&flow=xtls-rprx-vision&security=reality"
            f"&sni=example.org&fp=firefox&pbk=PUBLICKEY&sid=ab12&spx=%2F&type=tcp#{name.replace(' ', '%20')}")


@pytest.fixture
def guard(monkeypatch, tmp_path):
    loader = importlib.machinery.SourceFileLoader("vpn_guard_under_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    for name, relative in dict(STATE_FILE="state.json", SUB_FILE="subscription", HWID_FILE="hwid",
                               TELEGRAM_OFF="off", LOG_FILE="guard.log", XRAY_CONF="config.json").items():
        monkeypatch.setattr(module, name, tmp_path / relative)
    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)
    yield module
    sys.modules.pop(loader.name, None)


@pytest.fixture
def config():
    return {
        "inbounds": [{"tag": "socks", "port": 10808, "protocol": "socks"},
                     {"tag": "transparent", "port": 12345, "protocol": "dokodemo-door"}],
        "outbounds": [
            {"tag": "proxy", "protocol": "vless", "mux": {"enabled": False},
             "settings": {"vnext": [{"address": "203.0.113.10", "port": 443, "users": [
                 {"id": UUID, "flow": "xtls-rprx-vision", "encryption": "none"}]}]},
             "streamSettings": {"network": "tcp", "security": "reality", "realitySettings": {
                 "serverName": "example.org", "publicKey": "PUBLICKEY", "shortId": "ab12"}}},
            {"tag": "direct", "protocol": "freedom"},
            {"tag": "block", "protocol": "blackhole"},
        ],
        "remarks": "Stockholm Sweden Extra",
        "routing": {"rules": [{"inboundTag": ["transparent"], "domain": ["domain:forumhouse.ru"], "outboundTag": "direct"}]},
    }


# ── ссылки vless:// ──

def test_vless_reality_becomes_xray_outbound(guard):
    node = guard.parse_vless(reality_link())
    out = node.outbound
    user = out["settings"]["vnext"][0]["users"][0]
    assert node.name == "Stockholm Sweden Extra"
    assert out["tag"] == "proxy" and out["protocol"] == "vless"
    assert (user["id"], user["flow"]) == (UUID, "xtls-rprx-vision")
    reality = out["streamSettings"]["realitySettings"]
    assert (reality["serverName"], reality["publicKey"], reality["shortId"], reality["spiderX"],
            reality["fingerprint"]) == ("example.org", "PUBLICKEY", "ab12", "/", "firefox")
    assert out["streamSettings"]["network"] == "tcp"


def test_vless_websocket_tls(guard):
    link = (f"vless://{UUID}@node.example.com:8443?security=tls&sni=node.example.com&alpn=h2,http/1.1"
            "&type=ws&host=cdn.example.com&path=%2Fws#WS")
    stream = guard.parse_vless(link).outbound["streamSettings"]
    assert stream["network"] == "ws" and stream["security"] == "tls"
    assert stream["wsSettings"] == {"path": "/ws", "headers": {"Host": "cdn.example.com"}}
    assert stream["tlsSettings"]["alpn"] == ["h2", "http/1.1"]


@pytest.mark.parametrize("link", [
    "vless://@host:443", "https://example.com", f"vless://{UUID}@host:443?security=reality&type=tcp",
    f"vless://{UUID}@host:443?type=quic", f"vless://{UUID}@host:443?security=weird"])
def test_vless_rejects_unusable_links(guard, link):
    with pytest.raises(ValueError):
        guard.parse_vless(link)


def test_identity_ignores_case_and_name(guard):
    a = guard.parse_vless(reality_link(host="Node.Example.com"))
    b = guard.parse_vless(reality_link(name="Другое имя", host="node.example.com"))
    assert guard.identity(a.outbound) == guard.identity(b.outbound)
    assert guard.identity(a.outbound) != guard.identity(guard.parse_vless(reality_link(user=OTHER)).outbound)


# ── подписка ──

def test_subscription_plain_lines_skip_comments_and_foreign_protocols(guard):
    body = "\n".join(["#profile-title: test", reality_link("Sweden 1"), "trojan://x@host:443#T",
                      "", reality_link("Germany", host="203.0.113.20")]).encode()
    nodes, skipped = guard.parse_subscription(body)
    assert [n.name for n in nodes] == ["Sweden 1", "Germany"]
    assert any("trojan" in note for note in skipped)


@pytest.mark.parametrize("encode", [
    lambda raw: base64.b64encode(raw),
    lambda raw: base64.urlsafe_b64encode(raw).rstrip(b"="),
    lambda raw: base64.b64encode(raw).replace(b"=", b"\n"),
])
def test_subscription_base64_variants(guard, encode):
    raw = "\n".join([reality_link("Sweden 1"), reality_link("Sweden 2", host="203.0.113.11")]).encode()
    nodes, _ = guard.parse_subscription(encode(raw))
    assert [n.name for n in nodes] == ["Sweden 1", "Sweden 2"]


def test_subscription_json_configs(guard):
    body = json.dumps([
        {"remarks": "Sweden JSON", "outbounds": [{"protocol": "vless", "tag": "x", "settings": {"vnext": []}}]},
        {"remarks": "Без узла", "outbounds": [{"protocol": "freedom"}]}]).encode()
    nodes, skipped = guard.parse_subscription(body)
    assert [n.name for n in nodes] == ["Sweden JSON"] and len(skipped) == 1


@pytest.mark.parametrize("body, fragment", [
    (b"", "пустая"),
    (b"<!DOCTYPE html><html><body>https://x</body></html>", "веб-страница"),
    (b"happ://crypt3/abcdef", "зашифрована"),
    (b"{not json", "JSON"),
])
def test_subscription_failures_are_explained(guard, body, fragment):
    with pytest.raises(guard.GuardError, match=fragment):
        guard.parse_subscription(body)


# ── выбор узла ──

def test_rank_prefers_current_name_filters_and_dedupes(guard):
    nodes = [guard.parse_vless(reality_link(name, host=host)) for name, host in [
        ("🇩🇪 Germany", "203.0.113.30"), ("Sweden fast", "203.0.113.11"),
        ("Stockholm Sweden Extra", "203.0.113.10"), ("Sweden fast copy", "203.0.113.11")]]
    ranked = guard.rank(nodes, "Stockholm Sweden Extra")
    assert [n.name for n in ranked] == ["Stockholm Sweden Extra", "Sweden fast"]


# ── замена только блока proxy ──

def test_build_config_replaces_only_proxy_and_remarks(guard, config, monkeypatch):
    monkeypatch.setattr(guard, "read_config", lambda: json.loads(json.dumps(config)))
    node = guard.parse_vless(reality_link("Sweden NEW", host="203.0.113.99", user=OTHER))
    new = guard.build_config(node)
    assert new["remarks"] == "Sweden NEW"
    assert new["inbounds"] == config["inbounds"] and new["routing"] == config["routing"]
    assert new["outbounds"][1:] == config["outbounds"][1:]
    proxy = new["outbounds"][0]
    assert proxy["tag"] == "proxy" and proxy["mux"] == {"enabled": False}
    assert proxy["settings"]["vnext"][0]["address"] == "203.0.113.99"


# ── служебное ──

def test_curl_config_quoting_and_newline_guard(guard):
    assert guard.cfg_quote('a"b\\c\nd') == '"a\\"b\\\\c\\nd"'
    with pytest.raises(guard.GuardError):
        guard.curl("https://example.com/\nurl = file:///etc/passwd")


def test_mask_host(guard):
    assert guard.mask_host("203.0.113.10") == "203.0.*.*"
    assert guard.mask_host("node.example.com") == "node.example.com"


def test_fetch_falls_back_to_device_id_and_remembers(guard, monkeypatch):
    calls = []

    def fake_curl(url, **kwargs):
        headers = kwargs.get("headers") or {}
        calls.append("x-hwid" in headers)
        return (200, b"ok", "") if "x-hwid" in headers else (404, b"", "")

    monkeypatch.setattr(guard, "curl", fake_curl)
    state = {}
    assert guard.fetch_subscription("https://sub.example/x", state) == b"ok"
    assert calls == [False, True] and state["needs_hwid"] is True
    calls.clear()
    assert guard.fetch_subscription("https://sub.example/x", state) == b"ok"
    assert calls == [True]


def test_fetch_reports_panel_error_without_url(guard, monkeypatch):
    monkeypatch.setattr(guard, "curl", lambda url, **kw: (404, b"", ""))
    with pytest.raises(guard.GuardError) as caught:
        guard.fetch_subscription("https://secret.example/token123", {})
    assert "лимит устройств" in str(caught.value) and "token123" not in str(caught.value)


def test_set_url_rejects_encrypted_and_junk_without_network(guard, monkeypatch):
    monkeypatch.setattr(guard, "curl", lambda *a, **k: pytest.fail("сеть не должна вызываться"))
    assert "зашифрована" in guard.do_set_url("happ://crypt3/AAAA")["message"]
    assert not guard.do_set_url("просто текст")["ok"]
    assert not guard.do_set_url("https://a.example/x\nhttps://b.example/y")["ok"]
    assert not guard.SUB_FILE.exists()


# ── сценарий замены ──

class Rig:
    """Подставки вместо сети и Xray для сценариев do_refresh / do_check."""

    def __init__(self, guard, monkeypatch, config, *, alive, nodes, verdicts=None, apply_ok=True):
        self.guard, self.applied, self.notices = guard, [], []
        self.alive = alive
        verdicts = verdicts or {}
        guard.SUB_FILE.write_text("https://sub.example/token\n")
        monkeypatch.setattr(guard, "read_config", lambda: json.loads(json.dumps(config)))
        monkeypatch.setattr(guard, "fetch_subscription", lambda url, state: b"")
        monkeypatch.setattr(guard, "parse_subscription", lambda body: (nodes, []))
        monkeypatch.setattr(guard, "probe_egress", lambda *a, **k: dict(ok=self.alive, ms=700, country="SE"))
        monkeypatch.setattr(guard, "test_candidate",
                            lambda node: dict(ok=verdicts.get(node.name, True), ms=650, country="SE", error=None))
        monkeypatch.setattr(guard, "xray_test", lambda cfg: None)
        monkeypatch.setattr(guard, "apply_node", lambda node: (
            self.applied.append(node.name) or (dict(ok=True, egress=dict(ok=True, ms=640, country="SE")) if apply_ok
                                              else dict(ok=False, reason="Xray не поднялся после замены"))))
        monkeypatch.setattr(guard, "notify", lambda state, text: self.notices.append(text) or True)
        monkeypatch.setattr(guard, "snapshot_is_current", lambda: True)
        monkeypatch.setattr(guard, "safety_armed", lambda: False)
        monkeypatch.setattr(guard, "probe_telegram_direct", lambda: True)
        monkeypatch.setattr(guard, "probe_telegram_tunnel", lambda: True)
        monkeypatch.setattr(guard, "sh", lambda *a, **k: type("R", (), dict(stdout="active\n", returncode=0))())


def node(guard, name, host, user=UUID):
    return guard.parse_vless(reality_link(name, host=host, user=user))


def test_refresh_unchanged_when_alive_and_same_node(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=True, nodes=[node(guard, "Stockholm Sweden Extra", "203.0.113.10")])
    result = guard.do_refresh(force=True)
    assert result["ok"] and not result["changed"] and "Менять нечего" in result["message"] and not rig.applied


def test_refresh_replaces_dead_node_with_first_working_candidate(guard, monkeypatch, config):
    nodes = [node(guard, "Sweden A", "203.0.113.21", OTHER), node(guard, "Sweden B", "203.0.113.22", OTHER)]
    rig = Rig(guard, monkeypatch, config, alive=False, nodes=nodes, verdicts={"Sweden A": False})
    result = guard.do_refresh(force=False)
    assert result["changed"] and rig.applied == ["Sweden B"]
    assert json.loads(guard.STATE_FILE.read_text())["last_change"]["to"] == "Sweden B"


def test_refresh_skips_the_node_that_is_currently_dead(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=False, nodes=[node(guard, "Stockholm Sweden Extra", "203.0.113.10")])
    result = guard.do_refresh(force=False)
    assert not result["ok"] and not rig.applied and "тот же узел" in result["message"]


def test_refresh_without_swedish_node_lists_names(guard, monkeypatch, config):
    Rig(guard, monkeypatch, config, alive=False, nodes=[node(guard, "Germany", "203.0.113.30")])
    result = guard.do_refresh(force=False)
    assert not result["ok"] and "Germany" in result["message"] and "шведского" in result["message"]


def test_refresh_forced_new_node_failing_keeps_working_one(guard, monkeypatch, config):
    nodes = [node(guard, "Stockholm Sweden Extra", "203.0.113.50", OTHER), node(guard, "Stockholm Sweden Extra", "203.0.113.10")]
    rig = Rig(guard, monkeypatch, config, alive=True, nodes=nodes, verdicts={"Stockholm Sweden Extra": False})
    result = guard.do_refresh(force=True)
    assert result["ok"] and not result["changed"] and not rig.applied and "Оставил прежний" in result["message"]


def test_refresh_without_subscription_url(guard, monkeypatch, config):
    Rig(guard, monkeypatch, config, alive=False, nodes=[])
    guard.SUB_FILE.unlink()
    assert "не задана" in guard.do_refresh(force=False)["message"]


def test_dry_run_never_applies(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=False, nodes=[node(guard, "Sweden A", "203.0.113.21", OTHER)])
    result = guard.do_refresh(force=False, dry_run=True)
    assert result["ok"] and result.get("dry_run") and not rig.applied


# ── проверка по таймеру ──

def test_check_healthy_is_silent(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=True, nodes=[])
    guard.do_check()
    assert rig.notices == []
    assert json.loads(guard.STATE_FILE.read_text())["last_check"]["egress_ok"] is True


def test_check_replaces_and_notifies_once(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=False, nodes=[node(guard, "Sweden B", "203.0.113.22", OTHER)])
    result = guard.do_check()
    assert result["changed"] and rig.applied == ["Sweden B"]
    assert len(rig.notices) == 1 and "Узел заменён" in rig.notices[0]
    assert json.loads(guard.STATE_FILE.read_text())["incident"] is None


def test_check_failure_notifies_once_per_incident_then_announces_recovery(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=False, nodes=[node(guard, "Germany", "203.0.113.30")])
    guard.do_check()
    guard.do_check()
    assert len(rig.notices) == 1 and "не отвечает" in rig.notices[0] and "нет шведского узла" in rig.notices[0]
    rig.alive = True
    guard.do_check()
    assert len(rig.notices) == 2 and "снова отвечает" in rig.notices[1]
    guard.do_check()
    assert len(rig.notices) == 2


def test_check_recovery_before_notification_stays_silent(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=False, nodes=[])
    state = guard.load_state()
    state["incident"] = {"since": "x", "notified": False}
    guard.save_state(state)
    rig.alive = True
    guard.do_check()
    assert rig.notices == [] and json.loads(guard.STATE_FILE.read_text())["incident"] is None


def test_check_removes_telegram_exemption_when_direct_path_closes(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=True, nodes=[])
    monkeypatch.setattr(guard, "probe_telegram_direct", lambda: False)
    toggled = []
    monkeypatch.setattr(guard, "set_telegram_direct", lambda enabled: toggled.append(enabled))
    guard.do_check()
    assert toggled == [False] and "Вернул Telegram в туннель" in rig.notices[0]


def test_check_restores_exemption_only_after_three_good_checks(guard, monkeypatch, config):
    rig = Rig(guard, monkeypatch, config, alive=True, nodes=[])
    guard.TELEGRAM_OFF.write_text("x")
    toggled = []
    monkeypatch.setattr(guard, "set_telegram_direct", lambda enabled: toggled.append(enabled))
    guard.do_check()
    guard.do_check()
    assert toggled == []
    guard.do_check()
    assert toggled == [True] and "включено обратно" in rig.notices[-1]


# ── уведомления ──

def test_notify_delivers_and_records_history(guard, monkeypatch, tmp_path):
    (tmp_path / ".env").write_text('TELEGRAM_BOT_TOKEN=123:ABC\nADMIN_USER_IDS=[4242]\n')
    monkeypatch.setattr(guard, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(guard, "SESSIONS", tmp_path / "sessions")
    (tmp_path / "sessions").mkdir()
    sent = {}

    def fake_curl(url, **kwargs):
        sent.update(url=url, post=kwargs["post"])
        return 200, json.dumps({"ok": True, "result": {"message_id": 777}}).encode(), ""

    monkeypatch.setattr(guard, "curl", fake_curl)
    state = {}
    assert guard.notify(state, "🔁 <b>Узел заменён.</b>")
    assert sent["url"] == "https://api.telegram.org/bot123:ABC/sendMessage"
    assert sent["post"]["chat_id"] == "4242" and sent["post"]["parse_mode"] == "HTML"
    entry = json.loads((tmp_path / "sessions" / "4242.jsonl").read_text().splitlines()[-1])
    assert (entry["type"], entry["msg_id"], entry["chat_id"], entry["text"]) == ("assistant", 777, 4242, "🔁 <b>Узел заменён.</b>")
    assert entry["automatic"] is True and entry["ts"] and "pending_notifications" not in state


def test_notify_failure_is_kept_for_retry_and_not_recorded(guard, monkeypatch, tmp_path):
    (tmp_path / ".env").write_text('TELEGRAM_BOT_TOKEN=123:ABC\nADMIN_USER_IDS=[4242]\n')
    monkeypatch.setattr(guard, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(guard, "SESSIONS", tmp_path / "sessions")
    (tmp_path / "sessions").mkdir()
    monkeypatch.setattr(guard, "curl", lambda url, **kw: (0, b"", "timeout"))
    state = {}
    assert guard.notify(state, "текст") is False
    assert state["pending_notifications"] == ["текст"]
    assert not (tmp_path / "sessions" / "4242.jsonl").exists()
