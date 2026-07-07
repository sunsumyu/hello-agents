import pathlib
import re

p_workflow = pathlib.Path(r'E:\chain\hello-agents\code\chapter9\06_three_day_workflow.py')
content_w = p_workflow.read_text(encoding='utf-8')

# 匹配所有的 codebase_path="..." 或 codebase_path='./...'
pattern = r'codebase_path\s*=\s*[\"\'].*?[\"\']\s*,'
replacement = 'codebase_path=__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "codebase"),'

new_content, count = re.subn(pattern, replacement, content_w)

if count > 0:
    p_workflow.write_text(new_content, encoding='utf-8')
    print(f'Successfully updated {count} codebase paths.')
else:
    print('No paths found to update.')
