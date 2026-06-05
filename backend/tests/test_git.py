"""Git 集成模块测试。"""


class TestGitReposAPI:
    """Git 仓库接口测试。"""

    def test_list_repos(self, client, auth_token):
        """列出仓库应返回 200。"""
        response = client.get(
            "/api/v1/git/repos",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_list_repos_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/git/repos")
        assert response.status_code == 401

    def test_get_branches(self, client, auth_token):
        """获取分支列表应返回 200。"""
        response = client.get(
            "/api/v1/git/repos/repo_001/branches",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "branches" in data["data"]

    def test_get_branches_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/git/repos/repo_001/branches")
        assert response.status_code == 401


class TestMergeBranchesAPI:
    """Git 合并接口测试。"""

    def test_merge_branches_valid(self, client, auth_token):
        """执行合并应返回成功。"""
        response = client.post(
            "/api/v1/git/merge",
            json={
                "repo_id": "repo_001",
                "source_branch": "feature/new",
                "target_branch": "develop",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success"] is True

    def test_merge_branches_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/git/merge", json={})
        assert response.status_code == 401


class TestAuthRepoAPI:
    """Git 授权接口测试。"""

    def test_auth_repo(self, client, auth_token):
        """授权仓库应返回成功。"""
        response = client.post(
            "/api/v1/git/repos/repo_001/auth",
            json={"user_id": "user_002"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_revoke_auth(self, client, auth_token):
        """撤销授权应返回成功。"""
        response = client.delete(
            "/api/v1/git/repos/repo_001/auth/user_002",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
