"""组织架构模块测试。"""


class TestOrgStructureAPI:
    """组织架构接口测试。"""

    def test_get_structure(self, client, auth_token):
        """获取组织架构应返回 200。"""
        response = client.get(
            "/api/v1/org/structure",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"

    def test_get_structure_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/org/structure")
        assert response.status_code == 401


class TestCreateDepartmentAPI:
    """创建部门接口测试。"""

    def test_create_department_valid(self, client, auth_token):
        """合法部门应创建成功。"""
        response = client.post(
            "/api/v1/org/departments",
            json={
                "name": "研发部",
                "code": "dev_dept",
                "company_id": "company_001",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"
        assert data["data"]["name"] == "研发部"

    def test_create_department_missing_name(self, client, auth_token):
        """缺少名称应返回 422。"""
        response = client.post(
            "/api/v1/org/departments",
            json={"code": "dev_dept", "company_id": "company_001"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    def test_create_department_empty_name(self, client, auth_token):
        """空名称应返回 422。"""
        response = client.post(
            "/api/v1/org/departments",
            json={"name": "", "code": "dev_dept", "company_id": "company_001"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    def test_create_department_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/org/departments", json={})
        assert response.status_code == 401


class TestCreateTeamAPI:
    """创建团队接口测试。"""

    def test_create_team_valid(self, client, auth_token):
        """合法团队应创建成功。"""
        response = client.post(
            "/api/v1/org/teams",
            json={
                "name": "前端组",
                "code": "frontend_team",
                "department_id": "dept_001",
                "description": "负责前端开发",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_create_team_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/org/teams", json={})
        assert response.status_code == 401


class TestAddTeamMemberAPI:
    """添加团队成员接口测试。"""

    def test_add_member_valid(self, client, auth_token):
        """添加成员应返回成功。"""
        response = client.post(
            "/api/v1/org/teams/team_001/members",
            json={"user_id": "user_002", "role": "member"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_add_member_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/org/teams/team_001/members", json={})
        assert response.status_code == 401


class TestRemoveTeamMemberAPI:
    """移除团队成员接口测试。"""

    def test_remove_member(self, client, auth_token):
        """移除成员应返回成功。"""
        response = client.delete(
            "/api/v1/org/teams/team_001/members/user_002",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_remove_member_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.delete("/api/v1/org/teams/team_001/members/user_002")
        assert response.status_code == 401
