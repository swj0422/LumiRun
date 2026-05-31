#!/usr/bin/env python3
"""
术语替换脚本
将前端代码中的'班级'、'学员'、'导师'替换为'组织'、'成员'、'管理者'
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, Tuple

FRONTEND_DIR = Path(__file__).parent / "frontend"

TERM_MAPPING = {
    '班级': '组织',
    '学员': '成员',
    '导师': '管理者',
}

EXCLUDE_DIRS = {'node_modules', '.git', 'dist', '.venv', '__pycache__'}

FILE_EXTENSIONS = {
    '.vue', '.ts', '.tsx', '.js', '.jsx', '.json',
    '.html', '.css', '.scss', '.md', '.yaml', '.yml'
}


def get_files_with_terms(directory: Path) -> list:
    """获取包含目标术语的文件列表"""
    files = []
    for ext in FILE_EXTENSIONS:
        for file_path in directory.rglob(f'*{ext}'):
            if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
                for term in TERM_MAPPING.keys():
                    if term in content:
                        files.append(file_path)
                        break
            except (UnicodeDecodeError, PermissionError):
                continue
    return sorted(files)


def replace_terms(content: str) -> Tuple[str, Dict[str, int]]:
    """替换内容中的术语，返回替换后的内容和统计"""
    counts = {term: content.count(term) for term in TERM_MAPPING.keys()}
    new_content = content
    for old_term, new_term in TERM_MAPPING.items():
        new_content = new_content.replace(old_term, new_term)
    return new_content, counts


def process_files(apply: bool = False):
    """处理所有文件"""
    print(f"扫描目录: {FRONTEND_DIR}")
    print(f"术语映射: {TERM_MAPPING}")
    print()

    files = get_files_with_terms(FRONTEND_DIR)

    if not files:
        print("未找到包含目标术语的文件。")
        return

    print(f"找到 {len(files)} 个包含目标术语的文件:\n")

    total_counts = {term: 0 for term in TERM_MAPPING.keys()}
    changes_preview = []

    for file_path in files:
        content = file_path.read_text(encoding='utf-8')
        new_content, counts = replace_terms(content)

        file_changes = {term: counts[term] for term in TERM_MAPPING.keys() if counts[term] > 0}
        if file_changes:
            changes_preview.append((file_path, file_changes))
            for term, count in file_changes.items():
                total_counts[term] += count

    print("\n" + "="*80)
    print("替换预览汇总")
    print("="*80)

    print(f"\n{'文件':<60} {'班级→组织':<12} {'学员→成员':<12} {'导师→管理者':<12}")
    print("-"*96)

    for file_path, counts in changes_preview:
        rel_path = str(file_path.relative_to(FRONTEND_DIR.parent))[:58]
        print(f"{rel_path:<60} {counts.get('班级', 0):<12} {counts.get('学员', 0):<12} {counts.get('导师', 0):<12}")

    print("-"*96)
    print(f"{'总计':<60} {total_counts['班级']:<12} {total_counts['学员']:<12} {total_counts['导师']:<12}")
    print(f"\n预计替换次数: {sum(total_counts.values())} 处")

    if apply:
        print("\n" + "="*80)
        print("执行替换...")
        print("="*80)

        for file_path, _ in changes_preview:
            content = file_path.read_text(encoding='utf-8')
            new_content, _ = replace_terms(content)
            file_path.write_text(new_content, encoding='utf-8')
            print(f"已替换: {file_path.relative_to(FRONTEND_DIR.parent)}")

        print(f"\n✅ 替换完成! 共处理 {len(changes_preview)} 个文件, {sum(total_counts.values())} 处术语。")
    else:
        print("\n" + "="*80)
        print("预览模式: 使用 --apply 参数执行实际替换")
        print("="*80)


def main():
    parser = argparse.ArgumentParser(description='术语替换工具')
    parser.add_argument('--apply', action='store_true', help='执行实际替换')
    args = parser.parse_args()
    process_files(apply=args.apply)


if __name__ == '__main__':
    main()
