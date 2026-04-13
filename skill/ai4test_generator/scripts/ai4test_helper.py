#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI4Test 测试用例生成辅助脚本

提供以下功能:
1. 文档格式转换 (docx/txt -> markdown)
2. Mapping 表格提取
3. 测试用例 JSON 校验
4. Excel 结果解析
"""

import json
import re
import os
import sys
from typing import Dict, List, Optional


class DocumentParser:
    """文档解析器"""

    @staticmethod
    def split_markdown_tables(content: str) -> List[str]:
        """
        分割 Markdown 表格

        Args:
            content: Markdown 文本内容

        Returns:
            表格列表
        """
        pattern = re.compile(r'(?:\|.\n)+')
        tables = pattern.findall(content)
        tables = [table.strip() for table in tables]
        # 过滤掉太短的（不是有效表格）
        tables = [table for table in tables if table.count('|') > 4]
        return tables

    @staticmethod
    def extract_section(content: str, section_title: str) -> str:
        """
        提取文档中的指定章节

        Args:
            content: 文档内容
            section_title: 章节标题

        Returns:
            章节内容
        """
        pattern = rf"{section_title}(.*?)(?=\n\s*\d+\.\d+|\n\s*[A-Z]|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict]:
        """
        从文本中提取 JSON 对象

        Args:
            text: 包含 JSON 的文本

        Returns:
            JSON 字典或 None
        """
        if not isinstance(text, str):
            text = str(text)

        # 尝试清洗 Markdown 代码块标记
        text_clean = re.sub(r'^json\s*', '', text, flags=re.MULTILINE)
        text_clean = re.sub(r'\s*$', '', text_clean, flags=re.MULTILINE)
        text_clean = text_clean.strip()

        # 尝试直接解析
        try:
            return json.loads(text_clean)
        except json.JSONDecodeError:
            pass

        # 尝试正则提取第一个 { 到最后一个 }
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # 尝试提取 JSON 数组
        match = re.search(r'\[(.*)\]', text, re.DOTALL)
        if match:
            json_str = '[' + match.group(1) + ']'
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        return None


class TestCaseValidator:
    """测试用例校验器"""

    REQUIRED_FIELDS = ['case_name', 'level', 'eval_step_descri', 'expected_result']
    OPTIONAL_FIELDS = ['pre_condition', 'need_generate_sql', 'tags']

    @classmethod
    def validate(cls, test_cases: List[Dict]) -> Dict:
        """
        校验测试用例格式

        Args:
            test_cases: 测试用例列表

        Returns:
            校验结果
        """
        errors = []
        warnings = []

        for i, case in enumerate(test_cases):
            # 检查必填字段
            for field in cls.REQUIRED_FIELDS:
                if field not in case:
                    errors.append(f"用例{i+1}: 缺少必填字段 '{field}'")

            # 检查命名规范
            if 'case_name' in case:
                name = case['case_name']
                if not re.match(r'\[(IT 用例 | 业务用例 | 配置调度)', name):
                    warnings.append(f"用例{i+1}: 命名可能不符合规范")

            # 检查 L3 描述是否具体
            if 'expected_result' in case:
                result = case['expected_result']
                if '正确' in result or '不受影响' in result:
                    warnings.append(f"用例{i+1}: 预期结果包含模糊词汇 '{result}'")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'count': len(test_cases)
        }


class SQLGenerator:
    """SQL 生成辅助工具"""

    @staticmethod
    def generate_pass_fail_sql(table: str, condition: str, schema: str = None) -> str:
        """
        生成 PASS/FAIL 判断 SQL

        Args:
            table: 表名
            condition: 判断条件
            schema: schema 名

        Returns:
            SQL 语句
        """
        full_table = f"{schema}.{table}" if schema else table
        return f"""
SELECT
  CASE WHEN {condition}
  THEN 'PASS' ELSE 'FAIL' END as test_result
FROM {full_table}
"""

    @staticmethod
    def generate_uniqueness_check(table: str, column: str, schema: str = None) -> str:
        """
        生成唯一性检查 SQL

        Args:
            table: 表名
            column: 列名
            schema: schema 名

        Returns:
            SQL 语句
        """
        full_table = f"{schema}.{table}" if schema else table
        return f"""
SELECT
  CASE WHEN COUNT({column}) = COUNT(DISTINCT {column})
  THEN 'PASS' ELSE 'FAIL' END as test_result
FROM {full_table}
"""

    @staticmethod
    def generate_completeness_check(table: str, column: str, threshold: float = 0.9, schema: str = None) -> str:
        """
        生成完整性 (有值率) 检查 SQL

        Args:
            table: 表名
            column: 列名
            threshold: 阈值
            schema: schema 名

        Returns:
            SQL 语句
        """
        full_table = f"{schema}.{table}" if schema else table
        return f"""
SELECT
  CASE WHEN COUNT({column}) * 1.0 / COUNT(*) >= {threshold}
  THEN 'PASS' ELSE 'FAIL' END as test_result
FROM {full_table}
"""


def main():
    """主函数 - 命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python3 ai4test_helper.py <command> [args]")
        print("可用命令:")
        print("  validate <json_file>  - 校验测试用例 JSON")
        print("  extract_tables <md_file> - 提取 Markdown 表格")
        print("  generate_sql <type> <table> <column> - 生成 SQL")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'validate':
        if len(sys.argv) < 3:
            print("请提供 JSON 文件路径")
            sys.exit(1)

        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            test_cases = json.load(f)

        result = TestCaseValidator.validate(test_cases)
        print(f"校验结果：{'通过' if result['valid'] else '失败'}")
        print(f"用例数量：{result['count']}")
        if result['errors']:
            print("错误:")
            for err in result['errors']:
                print(f"  - {err}")
        if result['warnings']:
            print("警告:")
            for warn in result['warnings']:
                print(f"  - {warn}")

    elif command == 'extract_tables':
        if len(sys.argv) < 3:
            print("请提供 Markdown 文件路径")
            sys.exit(1)

        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            content = f.read()

        tables = DocumentParser.split_markdown_tables(content)
        print(f"找到 {len(tables)} 个表格:")
        for i, table in enumerate(tables):
            print(f"\n=== 表格 {i+1} ===")
            print(table)

    elif command == 'generate_sql':
        if len(sys.argv) < 5:
            print("用法：generate_sql <type> <table> <column> [schema]")
            sys.exit(1)

        sql_type = sys.argv[2]
        table = sys.argv[3]
        column = sys.argv[4]
        schema = sys.argv[5] if len(sys.argv) > 5 else None

        if sql_type == 'uniqueness':
            sql = SQLGenerator.generate_uniqueness_check(table, column, schema)
        elif sql_type == 'completeness':
            sql = SQLGenerator.generate_completeness_check(table, column, schema=schema)
        else:
            print(f"未知的 SQL 类型：{sql_type}")
            sys.exit(1)

        print(sql)

    else:
        print(f"未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
