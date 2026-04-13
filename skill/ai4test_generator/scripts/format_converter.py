#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例格式转换工具

支持以下格式互转:
- JSON -> Excel
- Excel -> JSON
- Markdown -> JSON
"""

import json
import sys
from typing import List, Dict


def json_to_markdown_table(test_cases: List[Dict]) -> str:
    """
    将测试用例 JSON 转换为 Markdown 表格

    Args:
        test_cases: 测试用例列表

    Returns:
        Markdown 表格字符串
    """
    if not test_cases:
        return "无测试用例"

    headers = ['序号', '用例名称', '等级', '前置条件', '测试步骤', '预期结果', '标签', '需 SQL']
    rows = [headers]

    for i, case in enumerate(test_cases, 1):
        row = [
            str(i),
            case.get('case_name', ''),
            case.get('level', ''),
            case.get('pre_condition', ''),
            case.get('eval_step_descri', ''),
            case.get('expected_result', ''),
            case.get('tags', ''),
            '是' if case.get('need_generate_sql', False) else '否'
        ]
        rows.append(row)

    # 计算每列最大宽度
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*rows)]

    # 生成表格
    lines = []
    for i, row in enumerate(rows):
        line = ' | '.join(str(cell).ljust(col_widths[j]) for j, cell in enumerate(row))
        lines.append(line)
        if i == 0:
            # 添加分隔线
            separator = ' | '.join('-' * width for width in col_widths)
            lines.append(separator)

    return '\n'.join(lines)


def markdown_table_to_json(table_content: str) -> List[Dict]:
    """
    将 Markdown 表格转换为测试用例 JSON

    Args:
        table_content: Markdown 表格内容

    Returns:
        测试用例列表
    """
    lines = table_content.strip().split('\n')
    if len(lines) < 3:
        return []

    # 跳过分隔线
    data_lines = [line for line in lines if not line.strip().startswith('|---')]

    # 解析表头
    headers = [h.strip() for h in data_lines[0].split('|')[1:-1]]

    # 解析数据行
    test_cases = []
    for line in data_lines[2:]:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells) >= len(headers):
            case = dict(zip(headers, cells))
            # 转换布尔值
            if '需 SQL' in case:
                case['need_generate_sql'] = case['需 SQL'] == '是'
            test_cases.append(case)

    return test_cases


def json_to_excel_format(test_cases: List[Dict]) -> Dict:
    """
    将测试用例 JSON 转换为 Excel 导入格式

    Args:
        test_cases: 测试用例列表

    Returns:
        Excel 导入格式的字典
    """
    excel_data = {
        'headers': ['Case Name', 'Level', 'Pre-condition', 'Test Step', 'Expected Result', 'Tags', 'Need SQL'],
        'rows': []
    }

    for case in test_cases:
        row = [
            case.get('case_name', ''),
            case.get('level', ''),
            case.get('pre_condition', ''),
            case.get('eval_step_descri', ''),
            case.get('expected_result', ''),
            case.get('tags', ''),
            str(case.get('need_generate_sql', False))
        ]
        excel_data['rows'].append(row)

    return excel_data


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法：python3 format_converter.py <input_file> <output_format>")
        print("支持的目标格式：markdown, excel, json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_format = sys.argv[2]

    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 判断输入格式并解析
    try:
        test_cases = json.loads(content)
    except json.JSONDecodeError:
        test_cases = markdown_table_to_json(content)

    # 转换为目标格式
    if output_format == 'markdown':
        output = json_to_markdown_table(test_cases)
    elif output_format == 'excel':
        output = json.dumps(json_to_excel_format(test_cases), ensure_ascii=False, indent=2)
    elif output_format == 'json':
        # 重新格式化 JSON
        output = json.dumps(test_cases, ensure_ascii=False, indent=2)
    else:
        print(f"不支持的目标格式：{output_format}")
        sys.exit(1)

    print(output)


if __name__ == '__main__':
    main()
