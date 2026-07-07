"""
GAIA 数据集直接下载脚本

绕过 huggingface_hub 库的版本问题，直接用 requests 下载。
运行前请确保已配置代理（如果需要）。
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("❌ 未找到 HF_TOKEN，请检查 .env 文件")
    exit(1)

print(f"✅ Token: {HF_TOKEN[:5]}***{HF_TOKEN[-4:]}")

# 代理设置（使用 Clash 端口 7897）
PROXIES = {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897",
}

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "User-Agent": "python-requests/2.31.0"
}

BASE_URL = "https://huggingface.co/datasets/gaia-benchmark/GAIA/resolve/main"

# 要下载的文件列表（只需要元数据，不需要附件）
FILES_TO_DOWNLOAD = [
    "2023/validation/metadata.jsonl",
    "2023/test/metadata.jsonl",
]

LOCAL_DIR = Path("./data/gaia")


def download_file(remote_path: str, local_path: Path) -> bool:
    """直接用 requests 下载单个文件"""
    import requests

    url = f"{BASE_URL}/{remote_path}"
    local_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n📥 下载: {remote_path}")
    print(f"   URL: {url}")

    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            proxies=PROXIES,
            timeout=60,
            stream=True
        )

        if resp.status_code == 200:
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            size = local_path.stat().st_size
            print(f"   ✅ 成功 ({size:,} 字节)")
            return True
        elif resp.status_code == 401:
            print(f"   ❌ 401 未授权：Token 无效或已过期")
        elif resp.status_code == 403:
            print(f"   ❌ 403 禁止访问：请在 HuggingFace 页面点击同意协议")
        elif resp.status_code == 404:
            print(f"   ⚠️ 404 文件不存在（可能路径已变更）")
        else:
            print(f"   ❌ HTTP {resp.status_code}: {resp.text[:200]}")

    except requests.exceptions.ProxyError as e:
        print(f"   ❌ 代理连接失败: {e}")
        print(f"   请检查 Clash 是否已开启，端口是否为 7897")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 连接失败: {e}")
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")

    return False


def main():
    print("\n" + "=" * 50)
    print("GAIA 数据集下载器（直接模式）")
    print("=" * 50)

    success_count = 0
    for file_path in FILES_TO_DOWNLOAD:
        local_path = LOCAL_DIR / file_path
        if local_path.exists():
            print(f"\n⏭️  已存在，跳过: {file_path}")
            success_count += 1
            continue
        if download_file(file_path, local_path):
            success_count += 1

    print(f"\n{'='*50}")
    if success_count == len(FILES_TO_DOWNLOAD):
        print(f"✅ 全部下载完成！数据位于: {LOCAL_DIR.absolute()}")
        print(f"\n现在可以运行：")
        print(f"   .\\venv-agent\\Scripts\\python.exe code/chapter12/05_gaia_quick_start.py")
    else:
        print(f"⚠️ 部分文件下载失败 ({success_count}/{len(FILES_TO_DOWNLOAD)})")


if __name__ == "__main__":
    main()
