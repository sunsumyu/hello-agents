"""
精确补丁：只修改 terminal_tool.py 中 subprocess.run 的 encoding 参数
不改动任何中文字符串，避免编码损坏
"""
import pathlib

p = pathlib.Path(r'E:\chain\hello-agents\venv-agent\Lib\site-packages\hello_agents\tools\builtin\terminal_tool.py')
raw = p.read_bytes()

# 检测文件编码
for enc in ['utf-8', 'utf-8-sig', 'gbk', 'latin-1']:
    try:
        raw.decode(enc)
        print(f"File encoding: {enc}")
        file_enc = enc
        break
    except:
        pass

content = raw.decode(file_enc)

# 只做一件事：在 text=True 后面加 encoding 和 errors 参数
# 找所有 subprocess.run 中 text=True 的位置
old_pattern = "text=True,\n                    timeout=self.timeout,"
new_pattern = "text=True,\n                    encoding='utf-8',\n                    errors='ignore',\n                    timeout=self.timeout,"

# 也处理 \r\n 的情况
old_pattern_crlf = "text=True,\r\n                    timeout=self.timeout,"
new_pattern_crlf = "text=True,\r\n                    encoding='utf-8',\r\n                    errors='ignore',\r\n                    timeout=self.timeout,"

count = 0
if old_pattern_crlf in content:
    content = content.replace(old_pattern_crlf, new_pattern_crlf)
    count = content.count("encoding='utf-8'")
elif old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    count = content.count("encoding='utf-8'")

if count > 0:
    p.write_bytes(content.encode(file_enc))
    print(f"Patched {count} subprocess.run call(s) with encoding='utf-8'")
else:
    if "encoding='utf-8'" in content:
        print("Already patched!")
    else:
        print("ERROR: Could not find pattern to patch")
        # Debug: show what's around text=True
        idx = content.find("text=True")
        if idx >= 0:
            print(f"Context around text=True: {repr(content[idx:idx+100])}")

# 验证文件仍然是有效 Python
import py_compile
try:
    py_compile.compile(str(p), doraise=True)
    print("Syntax check: PASSED")
except py_compile.PyCompileError as e:
    print(f"Syntax check: FAILED - {e}")
