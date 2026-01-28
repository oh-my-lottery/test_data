#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
移除JSON文件中指定的字段
"""

import json
import os
from pathlib import Path


# 需要移除的字段列表
FIELDS_TO_REMOVE = [
    'detailsLink',
    'videoLink',
    'msg',
    'prizegrades',
    'content',
    'z2add',
    'm2add'
]


def remove_fields_from_dict(obj, fields_to_remove):
    """
    递归地从字典或列表中移除指定字段
    保持列表元素顺序不变
    """
    if isinstance(obj, dict):
        # 使用列表推导式保持键的顺序
        return {
            key: remove_fields_from_dict(value, fields_to_remove)
            for key, value in obj.items()
            if key not in fields_to_remove
        }
    elif isinstance(obj, list):
        # 保持列表顺序不变
        return [remove_fields_from_dict(item, fields_to_remove) for item in obj]
    else:
        return obj


def process_json_file(file_path, fields_to_remove):
    """
    处理单个JSON文件，移除指定字段
    """
    print(f"处理文件: {file_path}")

    # 读取JSON文件（处理BOM）
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    # 移除指定字段
    cleaned_data = remove_fields_from_dict(data, fields_to_remove)

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=None, separators=(',', ':'))

    print(f"完成: {file_path}")


def main():
    # data目录路径
    data_dir = Path(__file__).parent / 'data'

    # 获取所有JSON文件
    json_files = list(data_dir.glob('*.json'))

    if not json_files:
        print("未找到JSON文件")
        return

    print(f"找到 {len(json_files)} 个JSON文件")
    print(f"将移除以下字段: {FIELDS_TO_REMOVE}")
    print("-" * 50)

    for json_file in json_files:
        process_json_file(json_file, FIELDS_TO_REMOVE)

    print("-" * 50)
    print("所有文件处理完成")


if __name__ == '__main__':
    main()
