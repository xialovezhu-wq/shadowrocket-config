#!/usr/bin/env python3
"""Validate the published files and routing intent; this is not an iOS core emulator."""
from __future__ import annotations

import fnmatch
import hashlib
import ipaddress
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICIES = {"DIRECT", "REJECT", "PROXY", "通用代理", "ChatGPT", "Claude", "Gemini"}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AssertionError(reason)


def sections(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    current = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            require(current not in result, f"Repeated section: {current}")
            result[current] = []
        else:
            require(bool(current), "Content outside a section")
            result[current].append(line)
    return result


def valid_domain(value: str) -> bool:
    domain = value.removeprefix(".")
    if not domain or any(c in domain for c in "/,:?#@\\ "):
        return False
    try:
        ipaddress.ip_address(domain)
        return False
    except ValueError:
        pass
    return all(re.fullmatch(r"[A-Za-z0-9_-]{1,63}", x) for x in domain.split("."))


def main() -> None:
    config = sections((ROOT / "mobile.conf").read_text())
    module = sections((ROOT / "adblock.sgmodule").read_text())
    release = json.loads((ROOT / "release.json").read_text())
    source = json.loads((ROOT / "sources.lock.json").read_text())
    expected_general = json.loads((ROOT / "tests/expected-general.json").read_text())
    actual_general = {k.strip(): v.strip() for k, v in (line.split("=", 1) for line in config["General"])}
    require(actual_general.pop("update-url") == release["stable_config_url"], "Wrong update URL")
    require(actual_general == expected_general, "Baseline network settings changed")
    require("block-quic" not in actual_general, "Unexpected QUIC override")
    require(set(config) == {"General", "Proxy Group", "Rule", "Host", "URL Rewrite"}, "Unexpected config capability")
    require(config["Host"] == ["localhost = 127.0.0.1"], "Unexpected local host override")
    require(config["URL Rewrite"] == [
        "'^https?://(www.)?g.cn($|/.*)' 'https://www.google.com$2' 302",
        "'^https?://(www.)?google.cn($|/.*)' 'https://www.google.com$2' 302",
    ], "Inherited rewrites changed")
    require(set(module) == {"Rule"}, "Ad module has capabilities beyond domain filtering")

    groups = {}
    for line in config["Proxy Group"]:
        name, options = line.split("=", 1)
        name = name.strip()
        require(name not in groups, "Duplicate group")
        require(options.strip().startswith("select,WgetCloud,use=true,policy-regex-filter="), "Group is not a manual local-subscription selector")
        expression = options.split("policy-regex-filter=", 1)[1]
        groups[name] = re.compile(expression)
    require(set(groups) == {"通用代理", "ChatGPT", "Claude", "Gemini"}, "Missing independent groups")
    for regex in groups.values():
        require(bool(regex.search("🇺🇲 美国 02")), "Real node was excluded")
        require(bool(regex.search("🇭🇰 香港 01")), "Real node was excluded")
        require(not regex.search("🇭🇰 套餐到期日期：2027-03-16"), "Metadata node included")
        require(not regex.search("🇭🇰 订阅获取时间：2026-11-09"), "Metadata node included")

    rules = [line.split(",") for line in config["Rule"]]
    identifiers = set()
    for rule in rules:
        kind = rule[0]
        policy = rule[-2] if rule[-1] == "no-resolve" else rule[-1]
        require(policy in POLICIES, f"Undefined policy: {policy}")
        require(kind in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "USER-AGENT", "IP-CIDR", "IP-ASN", "GEOIP", "FINAL"}, f"Unexpected rule type: {kind}")
        key = tuple(rule[:2])
        require(key not in identifiers, f"Duplicate rule: {key}")
        identifiers.add(key)
        if kind in {"DOMAIN", "DOMAIN-SUFFIX"}:
            require(valid_domain(rule[1]), f"Invalid domain: {rule[1]}")
        elif kind == "IP-CIDR":
            ipaddress.ip_network(rule[1], strict=False)
        elif kind == "IP-ASN":
            require(rule[1].isdigit(), "Invalid ASN")
    require(rules[-2:] == [["GEOIP", "CN", "DIRECT"], ["FINAL", "通用代理"]], "Wrong fallback order")
    for rule in rules:
        if rule[-1] in {"ChatGPT", "Claude", "Gemini"}:
            require(rule[1] not in {"google.com", "googleapis.com", "gstatic.com", "googleusercontent.com", "auth0.com", "stripe.com", "cloudflare.com", "sentry.io"}, "Shared service captured by AI group")

    ad_file = ROOT / source["distributed_file"]
    ad_lines = [x.strip() for x in ad_file.read_text().splitlines() if x.strip() and not x.startswith("#")]
    require(len(ad_lines) == len(set(ad_lines)) == source["domain_count"] == 37692, "Ad domain count or uniqueness changed")
    require(all(valid_domain(x) for x in ad_lines), "Invalid domain-set entry")
    require(hashlib.sha256(ad_file.read_bytes()).hexdigest() == source["distributed_sha256"], "Vendored list hash changed")
    exact = {x for x in ad_lines if not x.startswith(".")}
    suffix = {x[1:] for x in ad_lines if x.startswith(".")}

    def blocked(host: str) -> bool:
        host = host.lower()
        labels = host.split(".")
        return host in exact or any(".".join(labels[i:]) in suffix for i in range(len(labels)))

    def route(host: str, *, ads: bool = False, geoip: str | None = None) -> str:
        if ads and blocked(host):
            return "REJECT"
        try:
            addr = ipaddress.ip_address(host)
        except ValueError:
            addr = None
        for rule in rules:
            kind = rule[0]
            policy = rule[-2] if rule[-1] == "no-resolve" else rule[-1]
            value = rule[1]
            matched = (
                kind == "FINAL"
                or (kind == "DOMAIN" and host.lower() == value.lower())
                or (kind == "DOMAIN-SUFFIX" and (host.lower() == value.lower() or host.lower().endswith("." + value.lower())))
                or (kind == "DOMAIN-KEYWORD" and value.lower() in host.lower())
                or (kind == "GEOIP" and geoip == value)
            )
            if kind == "IP-CIDR" and addr is not None:
                matched = addr in ipaddress.ip_network(value, strict=False)
            if matched:
                return policy
        raise AssertionError("No fallback")

    cases = {
        "localhost": "DIRECT", "printer.local": "DIRECT", "router.home.arpa": "DIRECT",
        "192.168.1.20": "DIRECT", "10.2.0.1": "DIRECT", "127.0.0.1": "DIRECT",
        "::1": "DIRECT", "fd12::1": "DIRECT", "fe80::123": "DIRECT",
        "www.baidu.com": "DIRECT", "www.taobao.com": "DIRECT", "www.bilibili.com": "DIRECT",
        "weixin.qq.com": "DIRECT", "pay.weixin.qq.com": "DIRECT", "www.alipay.com": "DIRECT",
        "appleid.apple.com": "DIRECT", "push.apple.com": "DIRECT", "www.icloud.com": "DIRECT",
        "apple-relay.apple.com": "通用代理",
        "chatgpt.com": "ChatGPT", "api.openai.com": "ChatGPT", "cdn.oaistatic.com": "ChatGPT",
        "files.oaiusercontent.com": "ChatGPT", "claude.ai": "Claude", "api.anthropic.com": "Claude",
        "gemini.google.com": "Gemini", "aistudio.google.com": "Gemini", "generativelanguage.googleapis.com": "Gemini",
        "www.google.com": "通用代理", "accounts.google.com": "通用代理", "mail.google.com": "通用代理",
        "www.googleapis.com": "通用代理", "fonts.gstatic.com": "通用代理", "example.googleusercontent.com": "通用代理",
        "github.com": "通用代理", "www.youtube.com": "通用代理", "example.invalid": "通用代理",
        "api.stripe.com": "通用代理", "example.auth0.com": "通用代理", "example.sentry.io": "通用代理",
    }
    for host, expected in cases.items():
        require(route(host) == expected, f"Routing mismatch: {host}")
    critical = ["chatgpt.com", "api.openai.com", "claude.ai", "accounts.google.com", "appleid.apple.com", "idmsa.apple.com", "push.apple.com", "pay.weixin.qq.com", "www.alipay.com", "tenpay.com", "captive.apple.com"]
    for host in critical:
        require(not blocked(host), f"Critical flow appears in ad list: {host}")
    require(route("googleads.g.doubleclick.net", ads=True) == "REJECT", "Ad module has no expected blocking effect")
    require(route("googleads.g.doubleclick.net", ads=False) != "REJECT", "Ad module cannot be bypassed when disabled")
    require(route("unknown.example", geoip="CN") == "DIRECT", "CN fallback failed")

    asset_sha = release["asset_commit"]
    require(re.fullmatch(r"[0-9a-f]{40}", asset_sha) is not None, "Unpinned asset version")
    expected_ad_rule = f"DOMAIN-SET,https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/{asset_sha}/rules/vendor/advertising-lite.domain-set,REJECT"
    require(module["Rule"] == [expected_ad_rule], "Unexpected ad module rules or mutable dependency")
    version_dir = ROOT / "versions" / release["version"]
    frozen = sections((version_dir / "mobile.conf").read_text())
    require(not any(l.startswith("update-url") for l in frozen["General"]), "Frozen version would update back to main")
    current_without_url = {**config, "General": [l for l in config["General"] if not l.startswith("update-url")]}
    require(frozen == current_without_url, "Frozen config is incomplete")
    require((version_dir / "adblock.sgmodule").read_bytes() == (ROOT / "adblock.sgmodule").read_bytes(), "Frozen module mismatch")
    require(release["config_import_url"] == "shadowrocket://config/add/" + release["stable_config_url"], "Wrong config import scheme")
    require(release["module_import_url"] == "shadowrocket://install?module=" + release["stable_module_url"], "Wrong module import scheme")
    forbidden = re.compile(r"(?im)/U[s]ers/|wgetcloud\.online/link/|\b(?:ss|vmess|vless|trojan)://|^\s*\[Proxy\]\s*$")
    credential = re.compile(r"(?im)^\s*[\"']?(?:password|private[-_]?key|secret|token|uuid)[\"']?\s*[:=]\s*[\"']?[^\s\"']")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix == ".png":
            continue
        body = path.read_text(encoding="utf-8")
        require(not forbidden.search(body), f"Private endpoint, local path, or node block in {path.relative_to(ROOT)}")
        require(not credential.search(body), f"Credential assignment in {path.relative_to(ROOT)}")
    print(json.dumps({"passed": True, "routing_cases": len(cases), "critical_ad_exceptions_checked": len(critical), "rules": len(rules), "groups": len(groups), "ad_domains": len(ad_lines), "scope": "static validation only; native iPhone compilation and network tests pending"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
