#!/bin/bash
#
# AI4Test Skill 验证脚本
# 用于验证 Skill 目录结构和文件完整性
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "======================================"
echo "AI4Test Skill 结构验证"
echo "======================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数器
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 检查文件是否存在
check_file() {
    local file="$1"
    local desc="$2"
    if [ -f "$file" ]; then
        echo -e "${GREEN}[PASS]${NC} $desc: $file"
        ((PASS_COUNT++))
    else
        echo -e "${RED}[FAIL]${NC} $desc：$file"
        ((FAIL_COUNT++))
    fi
}

# 检查目录是否存在
check_dir() {
    local dir="$1"
    local desc="$2"
    if [ -d "$dir" ]; then
        echo -e "${GREEN}[PASS]${NC} $desc: $dir"
        ((PASS_COUNT++))
    else
        echo -e "${RED}[FAIL]${NC} $desc：$dir"
        ((FAIL_COUNT++))
    fi
}

# 警告检查
check_warn() {
    local file="$1"
    local desc="$2"
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -eq 0 ]; then
            echo -e "${YELLOW}[WARN]${NC} $desc 为空：$file"
            ((WARN_COUNT++))
        else
            echo -e "${GREEN}[PASS]${NC} $desc: $file ($size bytes)"
            ((PASS_COUNT++))
        fi
    else
        echo -e "${YELLOW}[WARN]${NC} $desc 可选：$file"
        ((WARN_COUNT++))
    fi
}

echo ""
echo "1. 检查目录结构..."
echo "--------------------------------------"
check_dir "$SKILL_DIR" "Skill 根目录"
check_dir "$SKILL_DIR/examples" "examples 目录"
check_dir "$SKILL_DIR/scripts" "scripts 目录"

echo ""
echo "2. 检查必需文件..."
echo "--------------------------------------"
check_file "$SKILL_DIR/SKILL.md" "SKILL.md"

echo ""
echo "3. 检查示例文件..."
echo "--------------------------------------"
check_warn "$SKILL_DIR/examples/1_basic_usage.md" "基础用法示例"
check_warn "$SKILL_DIR/examples/2_advanced_usage.md" "高级用法示例"

echo ""
echo "4. 检查脚本文件..."
echo "--------------------------------------"
check_warn "$SKILL_DIR/scripts/ai4test_helper.py" "辅助工具脚本"
check_warn "$SKILL_DIR/scripts/format_converter.py" "格式转换脚本"

echo ""
echo "5. Python 语法检查..."
echo "--------------------------------------"
for py_file in "$SKILL_DIR/scripts"/*.py; do
    if [ -f "$py_file" ]; then
        if python3 -m py_compile "$py_file" 2>/dev/null; then
            echo -e "${GREEN}[PASS]${NC} Python 语法检查：$(basename $py_file)"
            ((PASS_COUNT++))
        else
            echo -e "${RED}[FAIL]${NC} Python 语法错误：$(basename $py_file)"
            ((FAIL_COUNT++))
        fi
    fi
done

echo ""
echo "======================================"
echo "验证结果汇总"
echo "======================================"
echo -e "${GREEN}通过：$PASS_COUNT${NC}"
echo -e "${RED}失败：$FAIL_COUNT${NC}"
echo -e "${YELLOW}警告：$WARN_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ 验证通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 验证失败，请修复上述错误${NC}"
    exit 1
fi
