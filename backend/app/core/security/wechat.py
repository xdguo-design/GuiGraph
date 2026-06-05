"""微信 OAuth2.0 客户端。"""

import httpx
from loguru import logger

from app.config.settings import settings


class WechatClient:
    """微信 OAuth2.0 客户端。"""

    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
        self.base_url = "https://api.weixin.qq.com"

    async def get_qrconnect_url(self, redirect_uri: str, state: str = "") -> str:
        """生成微信扫码登录 URL。"""
        if not self.app_id or not self.app_secret:
            logger.warning("微信 OAuth 未配置")
            return ""
        params = {
            "appid": self.app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_login",
            "state": state,
        }
        return f"https://open.weixin.qq.com/connect/qrconnect?{self._urlencode(params)}#wechat_redirect"

    async def get_user_info(self, code: str) -> dict:
        """通过 code 获取用户信息。"""
        if not self.app_id or not self.app_secret:
            return {}
        url = f"{self.base_url}/sns/oauth2/access_token"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if "access_token" not in data:
                logger.error(f"微信获取 access_token 失败: {data}")
                return {}
            # 获取用户信息
            user_url = f"{self.base_url}/sns/userinfo"
            user_params = {
                "access_token": data["access_token"],
                "openid": data["openid"],
                "lang": "zh_CN",
            }
            user_resp = await client.get(user_url, params=user_params)
            return user_resp.json()

    @staticmethod
    def _urlencode(params: dict) -> str:
        return "&".join(f"{k}={v}" for k, v in params.items())


wechat_client = WechatClient()
