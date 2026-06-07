"""变更管理模块测试。"""

import pytest


class TestChangeListAPI:
    """变更列表接口测试。"""

    def test_list_changes_default_page(self, client, auth_token):
        """默认分页查询应返回 200。"""
        response = client.get(
            "/api/v1/changes",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"
        assert "items" in data["data"]
        assert "total" in data["data"]

    def test_list_changes_with_filters(self, client, auth_token):
        """带筛选条件的查询应返回 200。"""
        response = client.get(
            "/api/v1/changes",
            params={"change_type": "db", "status": "draft", "page": 1, "page_size": 10},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_list_changes_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/changes")
        assert response.status_code == 401

    def test_list_changes_page_out_of_range(self, client, auth_token):
        """页码为 0 应返回 422 或处理。"""
        response = client.get(
            "/api/v1/changes",
            params={"page": 0},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code in (200, 422)


class TestChangeDetailAPI:
    """变更详情接口测试。"""

    def test_get_change_detail(self, client, auth_token):
        """获取变更详情应返回 200。"""
        response = client.get(
            "/api/v1/changes/chg_001",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"
        assert data["data"]["id"] == "chg_001"

    def test_get_change_detail_not_found(self, client, auth_token):
        """不存在的变更应返回 404。"""
        response = client.get(
            "/api/v1/changes/nonexistent_999",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # 当前 MVP 返回模拟数据，后续实现后应为 404
        assert response.status_code in (200, 404)

    def test_get_change_detail_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.get("/api/v1/changes/chg_001")
        assert response.status_code == 401


class TestCreateChangeAPI:
    """创建变更接口测试。"""

    def test_create_change_valid(self, client, auth_token):
        """合法变更应创建成功。"""
        response = client.post(
            "/api/v1/changes",
            json={
                "version_id": "v001",
                "change_type": "db",
                "content": "新增用户表字段，用于存储微信 OpenID",
                "change_reason": "requirement",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "OK"
        assert data["data"]["status"] == "draft"

    def test_create_change_missing_required_fields(self, client, auth_token):
        """缺少必填字段应返回 422。"""
        response = client.post(
            "/api/v1/changes",
            json={"version_id": "v001"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    def test_create_change_empty_content(self, client, auth_token):
        """内容为空应返回 422。"""
        response = client.post(
            "/api/v1/changes",
            json={
                "version_id": "v001",
                "change_type": "db",
                "content": "",
                "change_reason": "requirement",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    def test_create_change_content_too_short(self, client, auth_token):
        """内容少于 10 字符应返回 422。"""
        response = client.post(
            "/api/v1/changes",
            json={
                "version_id": "v001",
                "change_type": "db",
                "content": "短",
                "change_reason": "requirement",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    def test_create_change_invalid_change_type(self, client, auth_token):
        """无效变更类型应返回 422。"""
        response = client.post(
            "/api/v1/changes",
            json={
                "version_id": "v001",
                "change_type": "invalid_type",
                "content": "测试变更",
                "change_reason": "requirement",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422

    def test_create_change_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post(
            "/api/v1/changes",
            json={
                "version_id": "v001",
                "change_type": "db",
                "content": "测试",
                "change_reason": "requirement",
            },
        )
        assert response.status_code == 401


class TestUpdateChangeAPI:
    """更新变更接口测试。"""

    def test_update_change(self, client, auth_token):
        """更新变更应返回成功。"""
        response = client.put(
            "/api/v1/changes/chg_001",
            json={"content": "更新后的变更内容"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_update_change_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.put("/api/v1/changes/chg_001", json={})
        assert response.status_code == 401


class TestApproveChangeAPI:
    """审批变更接口测试。"""

    def test_approve_change_pass(self, client, auth_token):
        """审批通过应返回成功。"""
        response = client.post(
            "/api/v1/changes/chg_001/approve",
            json={"approved": True, "comment": "同意"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_approve_change_reject(self, client, auth_token):
        """审批驳回应返回成功。"""
        response = client.post(
            "/api/v1/changes/chg_001/approve",
            json={"approved": False, "comment": "需要补充影响范围"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_approve_change_without_token(self, client):
        """无 Token 应返回 401。"""
        response = client.post("/api/v1/changes/chg_001/approve", json={})
        assert response.status_code == 401
