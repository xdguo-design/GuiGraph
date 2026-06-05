"""用户模块测试。"""


class TestUserProfileAPI:
    """用户资料接口测试。"""

    def test_get_profile(self, client, auth_token):
        """获取用户资料应返回 200。"""
        response = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"
        assert "username" in data["data"]

    def test_get_profile_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/user/profile")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        """无效 Token 应返回 401。"""
        response = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401


class TestUpdateProfileAPI:
    """更新用户资料接口测试。"""

    def test_update_profile(self, client, auth_token):
        """更新用户资料应返回成功。"""
        response = client.put(
            "/api/v1/user/profile",
            json={"nickname": "新昵称", "email": "new@example.com"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_update_profile_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.put("/api/v1/user/profile", json={})
        assert response.status_code == 401


class TestUploadAvatarAPI:
    """头像上传接口测试。"""

    def test_upload_avatar_valid_image(self, client, auth_token):
        """上传有效图片应返回成功。"""
        files = {"file": ("test.png", b"fake_png_data", "image/png")}
        response = client.post(
            "/api/v1/user/avatar",
            files=files,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_upload_avatar_non_image(self, client, auth_token):
        """上传非图片文件应返回 400。"""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post(
            "/api/v1/user/avatar",
            files=files,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

    def test_upload_avatar_without_token(self, client):
        """无 Token 应返回 401。"""
        files = {"file": ("test.png", b"fake_data", "image/png")}
        response = client.post("/api/v1/user/avatar", files=files)
        assert response.status_code == 401


class TestBindWechatAPI:
    """微信绑定接口测试。"""

    def test_bind_wechat(self, client, auth_token):
        """绑定微信应返回成功。"""
        response = client.post(
            "/api/v1/user/bind-wechat",
            json={"code": "wechat_auth_code"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # 当前返回模拟数据
        assert response.status_code == 200

    def test_bind_wechat_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/user/bind-wechat", json={"code": "code"})
        assert response.status_code == 401
