"""Jenkins 集成模块测试。"""


class TestJenkinsInstancesAPI:
    """Jenkins 实例接口测试。"""

    def test_list_instances(self, client, auth_token):
        """列出实例应返回 200。"""
        response = client.get(
            "/api/v1/jenkins/instances",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_list_instances_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/jenkins/instances")
        assert response.status_code == 401


class TestTriggerBuildAPI:
    """触发构建接口测试。"""

    def test_trigger_build(self, client, auth_token):
        """触发构建应返回成功。"""
        response = client.post(
            "/api/v1/jenkins/build",
            json={"job_name": "sample-job"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "build_id" in data["data"]

    def test_trigger_build_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/jenkins/build", json={})
        assert response.status_code == 401


class TestBuildStatusAPI:
    """构建状态接口测试。"""

    def test_get_build_status(self, client, auth_token):
        """获取构建状态应返回 200。"""
        response = client.get(
            "/api/v1/jenkins/build/build_001/status",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_get_build_status_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/jenkins/build/build_001/status")
        assert response.status_code == 401


class TestBuildLogAPI:
    """构建日志接口测试。"""

    def test_get_build_log(self, client, auth_token):
        """获取构建日志应返回 200。"""
        response = client.get(
            "/api/v1/jenkins/build/build_001/log",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "log" in data["data"]

    def test_get_build_log_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/jenkins/build/build_001/log")
        assert response.status_code == 401


class TestStopBuildAPI:
    """停止构建接口测试。"""

    def test_stop_build(self, client, auth_token):
        """停止构建应返回成功。"""
        response = client.post(
            "/api/v1/jenkins/build/build_001/stop",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_stop_build_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/jenkins/build/build_001/stop")
        assert response.status_code == 401
