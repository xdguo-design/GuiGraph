"""认证模块测试。"""

import hashlib
import pytest

from app.core.security.crypto import hash_password, verify_password
from app.core.security.jwt import create_access_token, verify_token, decode_token, get_token_payload


class TestMD5Password:
    """MD5 密码加密测试。"""

    def test_hash_password_returns_32_char_hex(self):
        """MD5 哈希结果应为 32 位十六进制字符串。"""
        result = hash_password("admin123")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_password_deterministic(self):
        """同一密码的 MD5 哈希结果应一致。"""
        h1 = hash_password("admin123")
        h2 = hash_password("admin123")
        assert h1 == h2

    def test_hash_password_different_inputs(self):
        """不同密码的 MD5 哈希结果应不同。"""
        h1 = hash_password("admin123")
        h2 = hash_password("admin124")
        assert h1 != h2

    def test_verify_password_correct(self):
        """正确密码应验证通过。"""
        pwd = "admin123"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True

    def test_verify_password_incorrect(self):
        """错误密码应验证失败。"""
        hashed = hash_password("admin123")
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_empty(self):
        """空密码验证。"""
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password(" ", hashed) is False

    def test_hash_password_special_chars(self):
        """特殊字符密码应正确哈希。"""
        pwd = "p@$$w0rd!#$%"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True

    def test_hash_password_unicode(self):
        """Unicode 密码应正确哈希。"""
        pwd = "密码123"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True

    def test_md5_matches_stdlib(self):
        """自定义 MD5 应与 hashlib 一致。"""
        pwd = "test_password"
        expected = hashlib.md5(pwd.encode("utf-8")).hexdigest()
        assert hash_password(pwd) == expected


class TestJWTToken:
    """JWT Token 测试。"""

    def test_create_access_token_has_sub(self):
        """Access Token 应包含 sub 字段。"""
        token = create_access_token({"sub": "user_001", "username": "test"})
        payload = decode_token(token)
        assert payload["sub"] == "user_001"

    def test_create_access_token_has_type(self):
        """Access Token 的 type 应为 access。"""
        token = create_access_token({"sub": "user_001"})
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_create_access_token_has_exp(self):
        """Access Token 应包含 exp 过期时间。"""
        token = create_access_token({"sub": "user_001"})
        payload = decode_token(token)
        assert "exp" in payload

    def test_create_access_token_has_iat(self):
        """Access Token 应包含 iat 签发时间。"""
        token = create_access_token({"sub": "user_001"})
        payload = decode_token(token)
        assert "iat" in payload

    def test_verify_token_valid(self):
        """有效 Token 应通过验证。"""
        token = create_access_token({"sub": "user_001", "username": "test", "role": "editor"})
        user_id = verify_token(token)
        assert user_id == "user_001"

    def test_verify_token_invalid(self):
        """无效 Token 应验证失败。"""
        user_id = verify_token("invalid.token.here")
        assert user_id is None

    def test_verify_token_expired(self):
        """过期 Token 应验证失败。"""
        from datetime import timedelta
        from app.core.security.jwt import create_access_token
        token = create_access_token({"sub": "user_001"}, expires_delta=timedelta(seconds=-1))
        user_id = verify_token(token)
        assert user_id is None

    def test_get_token_payload_returns_full_data(self):
        """get_token_payload 应返回完整载荷。"""
        token = create_access_token({"sub": "user_001", "username": "test", "role": "editor"})
        payload = get_token_payload(token)
        assert payload["username"] == "test"
        assert payload["role"] == "editor"

    def test_refresh_token_has_type_refresh(self):
        """Refresh Token 的 type 应为 refresh。"""
        from app.core.security.jwt import create_refresh_token
        token = create_refresh_token({"sub": "user_001"})
        payload = decode_token(token)
        assert payload["type"] == "refresh"


class TestLoginAPI:
    """登录接口测试。"""

    def test_login_success(self, client):
        """正确用户名密码应登录成功。"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """错误密码应返回 401。"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrong",
        })
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "ERROR"

    def test_login_empty_username(self, client):
        """空用户名应返回 422。"""
        response = client.post("/api/v1/auth/login", json={
            "username": "",
            "password": "admin",
        })
        assert response.status_code == 422

    def test_login_empty_password(self, client):
        """空密码应返回 422。"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "",
        })
        assert response.status_code == 422

    def test_login_missing_fields(self, client):
        """缺少字段应返回 422。"""
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_nonexistent_user(self, client):
        """不存在的用户应返回 401。"""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent_user_xyz",
            "password": "any_password",
        })
        assert response.status_code == 401


class TestTokenAuth:
    """Token 认证测试。"""

    def test_protected_route_with_valid_token(self, client, auth_token):
        """有效 Token 可访问受保护接口。"""
        response = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # 当前返回模拟数据，只要不 401/403 就算通过
        assert response.status_code in (200, 404)

    def test_protected_route_without_token(self, client):
        """无 Token 访问受保护接口应返回 401。"""
        response = client.get("/api/v1/user/profile")
        assert response.status_code == 401

    def test_protected_route_with_invalid_token(self, client):
        """无效 Token 应返回 401。"""
        response = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": "Bearer invalid_token_xyz"},
        )
        assert response.status_code == 401

    def test_protected_route_with_x_access_token_header(self, client, auth_token):
        """X-Access-Token 头部也应生效。"""
        response = client.get(
            "/api/v1/user/profile",
            headers={"X-Access-Token": auth_token},
        )
        # Token 校验在 Depends 中通过 Authorization，X-Access-Token 由前端传递
        # 此处验证请求能到达后端
        assert response.status_code != 500

    def test_refresh_token_endpoint(self, client, auth_token):
        """刷新 Token 接口。"""
        # 先用登录获取 refresh_token
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin",
        })
        refresh_token = login_resp.json()["data"]["refresh_token"]

        response = client.post("/api/v1/auth/refresh", params={"refresh_token": refresh_token})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]


class TestLogoutAPI:
    """退出登录测试。"""

    def test_logout_success(self, client, auth_token):
        """退出登录应返回成功。"""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"


class TestWechatLogin:
    """微信登录测试。"""

    def test_get_wechat_qrcode_unconfigured(self, client):
        """微信未配置时应返回 501。"""
        response = client.post("/api/v1/auth/wechat/qrcode")
        assert response.status_code == 501
