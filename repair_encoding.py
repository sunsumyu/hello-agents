import pathlib

def repair_file(file_path):
    print(f"Repairing {file_path}...")
    p = pathlib.Path(file_path)
    if not p.exists():
        print("File not found.")
        return

    # 以二进制读取
    raw = p.read_bytes()
    
    # 尝试修复乱码。
    # 这种乱码通常是 UTF-8 字节被误认为某种单字节编码后再写回导致的
    # 我们尝试用几种常见的编码组合来恢复
    try:
        # 很多时候是 UTF-8 字节被当成了 Latin-1 或者 GBK 处理
        # 既然现在已经乱了，我们直接用能读通的编码读出来，然后根据上下文修复已知的损坏点
        content = raw.decode('utf-8', errors='replace')
        
        # 修复已知的标题和注释损坏点
        content = content.replace('三天工作流演?', '三天工作流演示')
        content = content.replace('第一?', '第一天:')
        content = content.replace('第二?', '第二天:')
        content = content.replace('第三?', '第三天:')
        content = content.replace('自主探索?', '自主探索）')
        content = content.replace('自主分析?', '自主分析）')
        content = content.replace('自主规划?', '自主规划）')
        content = content.replace('检查进?', '检查进度')
        content = content.replace('三选一?', '三选一）')
        content = content.replace('无需额外依赖?', '无需额外依赖）')
        content = content.replace('不兼容的参?', '不兼容的参数')
        content = content.replace('需?', '需要:')
        content = content.replace('?', ' ') # 清理掉剩下的单个乱码符
        
        # 确保路径是正确的本地路径
        content = content.replace('/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase', './codebase')
        
        # 以 UTF-8 重新写入
        p.write_text(content, encoding='utf-8')
        print(f"Successfully repaired {file_path}")
    except Exception as e:
        print(f"Error repairing {file_path}: {e}")

# 执行修复
repair_file(r'e:\chain\hello-agents\code\chapter9\06_three_day_workflow.py')
repair_file(r'e:\chain\hello-agents\code\chapter9\codebase_maintainer.py')
