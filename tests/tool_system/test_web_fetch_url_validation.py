"""B6 Wave F1 — WebFetch URL 校验（SSRF 防护）edge cases。

05 号文档 Tools 项“补缺失 tool edge cases”。``_validate_url`` 是 WebFetch 的
安全边界：协议白名单、凭据拒绝、单段主机名拒绝、localhost/私网/保留地址拒绝。
此前没有任何直接测试。
"""
from __future__ import annotations

import pytest

from src.tool_system.errors import ToolInputError, ToolPermissionError
from src.tool_system.tools.web_fetch import _validate_url


class TestWebFetchUrlValidation:
    def test_http_upgraded_to_https(self) -> None:
        assert _validate_url("http://example.com/page") == "https://example.com/page"

    def test_https_passes(self) -> None:
        assert _validate_url("https://example.com") == "https://example.com"

    @pytest.mark.parametrize("scheme", ["ftp", "file", "javascript", "data", "ws"])
    def test_non_http_schemes_rejected(self, scheme: str) -> None:
        with pytest.raises(ToolPermissionError, match="only http/https"):
            _validate_url(f"{scheme}://example.com")

    def test_missing_network_location_rejected(self) -> None:
        with pytest.raises(ToolInputError, match="network location"):
            _validate_url("https://")

    def test_embedded_credentials_rejected(self) -> None:
        with pytest.raises(ToolPermissionError, match="credentials"):
            _validate_url("https://user:pass@example.com/")

    def test_single_part_hostname_rejected(self) -> None:
        with pytest.raises(ToolInputError, match="at least 2 parts"):
            _validate_url("https://intranet/")

    @pytest.mark.parametrize("host", ["localhost", "localhost:8080", "x.localhost"])
    def test_localhost_rejected(self, host: str) -> None:
        with pytest.raises(ToolPermissionError, match="localhost/private"):
            _validate_url(f"https://{host}/")

    @pytest.mark.parametrize(
        "host",
        ["127.0.0.1", "127.0.0.2", "10.0.0.1", "192.168.1.1", "172.16.0.1",
         "169.254.1.1", "0.0.0.0"],
    )
    def test_private_and_loopback_ip_rejected(self, host: str) -> None:
        with pytest.raises(ToolPermissionError, match="localhost/private"):
            _validate_url(f"https://{host}/")

    def test_public_hostname_passes(self) -> None:
        # example.com 解析可能依赖外部 DNS；_is_private_host 解析失败时按非私网
        # 处理（fail-open to validation, 不阻断公开站点）。
        assert _validate_url("https://example.com/") == "https://example.com/"

    def test_long_url_rejected(self) -> None:
        long = "https://example.com/" + "a" * 20_000
        with pytest.raises(ToolInputError, match="URL too long"):
            _validate_url(long)
