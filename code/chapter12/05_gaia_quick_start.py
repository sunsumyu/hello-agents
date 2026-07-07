"""
第十二章示例5：GAIA快速开始

对应文档：12.3.5 在HelloAgents中实现GAIA评估 - 方式1

这是最简单的GAIA评估方式，一行代码完成评估。

重要提示：
1. GAIA是受限数据集，需要先在HuggingFace上申请访问权限
2. 需要设置HF_TOKEN环境变量
3. 必须使用GAIA官方系统提示词
"""

import os
import sys
from dotenv import load_dotenv

# 1. 优先加载环境变量
load_dotenv()

# 2. 强制使用镜像站并增加重试逻辑
os.environ["HF_ENDPOINT"] = "https://huggingface.co"  # 直连官方（需开启代理）
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# 尝试提高网络库的稳定性
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
except ImportError:
    pass

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import GAIAEvaluationTool

# --- 强力预加载逻辑：将 Parquet 格式转换为 JSONL 格式 ---
def preload_gaia():
    print("\n🔄 检查并转换 GAIA 数据格式...")
    from pathlib import Path
    import json

    local_dir = Path("./data/gaia")
    
    for split in ["validation", "test"]:
        jsonl_path = local_dir / "2023" / split / "metadata.jsonl"
        
        if jsonl_path.exists():
            print(f"   ⏭️  {split}/metadata.jsonl 已存在，跳过")
            continue
        
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 方法1：从 datasets 库的 HF 缓存中读取并转换
        try:
            from datasets import load_dataset
            print(f"   📥 正在加载 {split} 分割...")
            ds = load_dataset(
                "gaia-benchmark/GAIA",
                "2023_all",
                split=split,
                token=os.getenv("HF_TOKEN")
            )
            print(f"   ✓ 读取到 {len(ds)} 条记录，正在转换为 JSONL...")
            with open(jsonl_path, "w", encoding="utf-8") as f:
                for item in ds:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"   ✅ 已保存: {jsonl_path}")
            continue
        except Exception as e:
            print(f"   ⚠️ datasets 方式失败: {e}")

        # 方法2：从已下载的 parquet 文件转换
        parquet_path = local_dir / "2023" / split / "metadata.parquet"
        if parquet_path.exists():
            try:
                import pyarrow.parquet as pq
                table = pq.read_table(str(parquet_path))
                records = table.to_pydict()
                keys = list(records.keys())
                n = len(records[keys[0]])
                with open(jsonl_path, "w", encoding="utf-8") as f:
                    for i in range(n):
                        row = {k: records[k][i] for k in keys}
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                print(f"   ✅ Parquet 转换完成: {jsonl_path} ({n} 条记录)")
            except Exception as e:
                print(f"   ⚠️ Parquet 转换失败: {e}")
        else:
            print(f"   ⚠️ 未找到数据文件: {parquet_path}")

preload_gaia()
# ---------------------

# GAIA官方系统提示词（必须使用）
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""

# 1. 设置HuggingFace Token（如果还没设置）
# os.environ["HF_TOKEN"] = "your_huggingface_token_here"

# 1. 验证 Token 加载
token = os.getenv("HF_TOKEN")
if not token:
    print("❌ 错误: 未在环境变量中找到 HF_TOKEN，请检查 .env 文件。")
else:
    print(f"✅ 已检测到 HF_TOKEN: {token[:5]}***{token[-4:]}")

# 2. 创建智能体（必须使用GAIA官方系统提示词）
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="TestAgent",
    llm=llm,
    system_prompt=GAIA_SYSTEM_PROMPT  # 必须使用官方提示词
)

# 3. 创建GAIA评估工具
gaia_tool = GAIAEvaluationTool()

# 4. 运行评估
results = gaia_tool.run(
    agent=agent,
    level=1,              # 评估级别（1=简单，2=中等，3=困难）
    max_samples=2,        # 评估样本数（0表示全部）
    export_results=True,  # 导出结果到GAIA官方格式
    generate_report=True  # 生成详细报告
)

# 5. 查看结果
if "error" in results or not results:
    print("\n❌ 评估未能成功运行，请检查上述错误信息（如网络或权限）。")
else:
    print(f"\n评估结果:")
    print(f"精确匹配率: {results['exact_match_rate']:.2%}")
    print(f"部分匹配率: {results['partial_match_rate']:.2%}")
    print(f"正确数: {results['correct_samples']}/{results['total_samples']}")

# 运行输出示例：
# ============================================================
# GAIA一键评估
# ============================================================
# 
# 配置:
#    智能体: TestAgent
#    级别: Level 1
#    样本数: 2
# 
# ✅ GAIA数据集加载完成
#    数据源: gaia-benchmark/GAIA
#    分割: validation
#    级别: 1
#    样本数: 2
# 
# 评估进度: 100%|██████████| 2/2 [00:10<00:00,  5.23s/样本]
# 
# ✅ 评估完成
#    总样本数: 2
#    正确样本数: 2
#    精确匹配率: 100.00%
#    部分匹配率: 100.00%
# 
# ✅ 结果已导出到 ./evaluation_results/gaia_submission.json
# ✅ 报告已生成到 ./evaluation_results/gaia_report.md
# 
# 评估结果:
# 精确匹配率: 100.00%
# 部分匹配率: 100.00%
# 正确数: 2/2

