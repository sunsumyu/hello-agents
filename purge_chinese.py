import pathlib

p = pathlib.Path(r'E:\chain\hello-agents\venv-agent\Lib\site-packages\hello_agents\tools\builtin\terminal_tool.py')
raw = p.read_bytes()

# 尝试用各种编码解码
content = None
for enc in ['utf-8', 'gbk', 'latin-1']:
    try:
        content = raw.decode(enc)
        print(f"Read with {enc}")
        break
    except:
        continue

if not content:
    print("Failed to decode file")
    exit(1)

# 替换所有可能引起编码问题的中文字符串
replacements = {
    '跨平台命令行工具': 'Cross-platform terminal tool',
    '执行安全的文件系统': 'Execute safe filesystem commands',
    '支持Windows/Linux/Mac': 'Supports Windows/Linux/Mac',
    '❌ 不允许的命令': 'Error: Command not allowed',
    '允许的命令': 'Allowed commands',
    '要执行的命令': 'Command to execute',
    '白名单': 'Whitelist',
    '示例': 'Example',
    '❌ cd 命令已禁用': 'Error: cd command is disabled',
    '当前目录': 'Current directory',
    '目标路径不存在': 'Target path does not exist',
    '❌ 路径逃逸尝试': 'Error: Path traversal attempt',
    '❌ 无法切换到目录': 'Error: Cannot change to directory',
    '✅ 切换到目录': 'Success: Changed directory to',
    '执行命令': 'Execute command',
    '合并标准输出和标准错误': 'Merge stdout and stderr',
    '检查输出大小': 'Check output size',
    '⚠️ 输出被截断': 'Warning: Output truncated',
    '添加返回码信息': 'Add return code info',
    '⚠️ 命令返回码': 'Warning: Command return code',
    '✅ 命令执行成功（无输出）': 'Success: Command executed (no output)',
    '❌ 命令执行超时': 'Error: Command timeout',
    '❌ 命令执行失败': 'Error: Command failed',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# 确保之前的 encoding 修复也在
if "encoding='utf-8'" not in content:
    # 再次尝试修补 subprocess.run
    content = content.replace("text=True,\n", "text=True, encoding='utf-8', errors='ignore',\n")
    content = content.replace("text=True,\r\n", "text=True, encoding='utf-8', errors='ignore',\r\n")

# 以纯 ASCII/UTF-8 写入
p.write_text(content, encoding='utf-8')
print("Successfully purged Chinese characters and applied encoding fix.")
