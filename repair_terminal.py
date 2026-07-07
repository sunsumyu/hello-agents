import pathlib

# 目标文件路径
file_path = pathlib.Path(r'E:\chain\hello-agents\venv-agent\Lib\site-packages\hello_agents\tools\builtin\terminal_tool.py')

# 正确的完整文件内容预览 (基于之前的 view_file 结果并修复损坏部分)
# 我们直接用字符串替换的方式，修复损坏的第97行
# 并且确保之前的 encoding='utf-8' 修复也被保留

try:
    # 1. 尝试以多种编码读取
    raw = file_path.read_bytes()
    
    # 2. 修复损坏的 description 字符串 (第97行左右)
    # 报错显示它卡在了 "Mac?" 附近
    # 我们找一个足够长的唯一片段来匹配
    corrupted_fragment = b'description="\xbf\xe7\xc6\xbd\xcc\xa8\xc3\xfc\xc1\xee\xd0\xd0\xb9\xa4\xbe\xdf - \xd6\xb4\xd0\xd0\xb0\xb2\xc8\xab\xb5\xc4\xce\xc4\xbc\xfe\xcf\xb5\xcd\xb3\xa1\xa2\xce\xc4\xb1\xbe\xb4\xa6\xc1\xee\xba\xcd\xb4\xfa\xc2\xeb\xd6\xb4\xd0\xd0\xc3\xfc\xc1\xee\xa3\xa8\xd6\xa7\xb3\xd6Windows/Linux/Mac'
    
    # 或者干脆寻找 description=" 开头到下一个末尾的部分
    # 由于文件现在可能包含 GBK 字节，我们直接用 bytes 搜索
    
    # 正确的内容（UTF-8）
    correct_line = '            description="跨平台命令行工具 - 执行安全的文件系统、文本处理和代码执行命令（支持Windows/Linux/Mac）"'.encode('utf-8')
    
    # 我们根据之前的 view_file 结果，把整个 __init__ 部分重写一遍，确保万无一失
    # 找到 __init__ 的开始
    init_start_marker = b'def __init__('
    init_idx = raw.find(init_start_marker)
    
    # 找到 run 方法的开始
    run_start_marker = b'def run(self, parameters: Dict[str, Any]) -> str:'
    run_idx = raw.find(run_start_marker)
    
    if init_idx != -1 and run_idx != -1:
        # 重构 __init__ 部分的内容，确保它是干净的 UTF-8
        new_init_content = """    def __init__(
        self,
        workspace: str = ".",
        timeout: int = 30,
        max_output_size: int = 10 * 1024 * 1024,  # 10MB
        allow_cd: bool = True,
        os_type: str = "auto"  # "auto", "windows", "linux", "mac"
    ):
        super().__init__(
            name="terminal",
            description="跨平台命令行工具 - 执行安全的文件系统、文本处理和代码执行命令（支持Windows/Linux/Mac）"
        )

        self.workspace = Path(workspace).resolve()
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.allow_cd = allow_cd

        # 检测或设置操作系统类型
        if os_type == "auto":
            self.os_type = self._detect_os()
        else:
            self.os_type = os_type.lower()

        # 当前工作目录（相对于workspace）
        self.current_dir = self.workspace

        # 确保工作目录存在
        self.workspace.mkdir(parents=True, exist_ok=True)

    """.encode('utf-8')
        
        # 拼接文件：头部 + 新的__init__ + 尾部
        new_raw = raw[:init_idx] + new_init_content + raw[run_idx:]
        
        # 再次检查 _execute_command 中的编码修复
        exec_marker = b'# \xcd\xb3\xd2\xbb\xca\xb9\xd3\xc3 utf-8' # 这可能也被弄乱了
        # 寻找 subprocess.run 附近的 text=True
        subp_marker = b'text=True,'
        
        # 为了稳妥起见，我们直接把 _execute_command 也整个重写一遍
        exec_start_marker = b'def _execute_command(self, command: str) -> str:'
        exec_idx = raw.find(exec_start_marker)
        
        if exec_idx != -1:
            # 找到下一个方法的开始或文件末尾
            next_method_marker = b'def get_current_dir(self) -> str:'
            next_idx = raw.find(next_method_marker)
            
            if next_idx != -1:
                new_exec_content = """    def _execute_command(self, command: str) -> str:
        \"\"\"执行命令\"\"\"
        try:
            # 统一使用 utf-8 + errors='ignore' 避免 Windows GBK 编码崩溃
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.current_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=self.timeout,
                env=os.environ.copy()
            )

            # 合并标准输出和标准错误
            output = result.stdout
            if result.stderr:
                output += f"\\n[stderr]\\n{result.stderr}"

            # 检查输出大小
            if len(output) > self.max_output_size:
                output = output[:self.max_output_size]
                output += f"\\n\\n⚠️ 输出被截断（超过 {self.max_output_size} 字节）"

            # 添加返回码信息
            if result.returncode != 0:
                output = f"⚠️ 命令返回码: {result.returncode}\\n\\n{output}"

            return output if output else "✅ 命令执行成功（无输出）"

        except subprocess.TimeoutExpired:
            return f"❌ 命令执行超时（超过 {self.timeout} 秒）"
        except Exception as e:
            return f"❌ 命令执行失败: {e}"

    """.encode('utf-8')
                
                # 重新拼接最终结果
                # 如果我们已经改了前面的部分，需要重新计算 run_idx 等，所以最稳妥是按顺序拼
                
                # 方案：分块拼接
                # 1. 头部到 __init__
                # 2. 干净的 __init__
                # 3. __init__ 之后到 _execute_command
                # 4. 干净的 _execute_command
                # 5. 剩余部分
                
                header = raw[:init_idx]
                middle = raw[run_idx:exec_idx]
                footer = raw[next_idx:]
                
                final_raw = header + new_init_content + middle + new_exec_content + footer
                
                file_path.write_bytes(final_raw)
                print("Repair successful: Reconstructed __init__ and _execute_command with UTF-8.")
            else:
                print("Failed to find next method marker.")
        else:
            print("Failed to find _execute_command marker.")
    else:
        print(f"Markers not found: init_idx={init_idx}, run_idx={run_idx}")

except Exception as e:
    print(f"Error during repair: {e}")
