#!/usr/bin/env python3
"""环境切换工具。用法: python switch_env.py [dev|test|prod]"""

import shutil
import sys
from pathlib import Path

VALID_ENVS = {"dev", "test", "prod"}
BASE_DIR = Path(__file__).parent


def switch_env(env_name: str) -> None:
    if env_name not in VALID_ENVS:
        print(f"[ERROR] 未知环境: {env_name}")
        print(f"可选: {', '.join(sorted(VALID_ENVS))}")
        sys.exit(1)

    src = BASE_DIR / f".env.{env_name}"
    dst = BASE_DIR / ".env"

    if not src.exists():
        print(f"[ERROR] 配置文件不存在: {src}")
        sys.exit(1)

    shutil.copy2(src, dst)
    print(f"[OK] 已切换到 {env_name} 环境 -> {src.name}")
    print("[NOTE] 请重启应用使配置生效")


if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else ""
    switch_env(env)
