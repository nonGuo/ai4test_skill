# 基础用法示例

## 场景 1: 首次生成测试用例

用户上传 Mapping 文档和 TS 文档，请求生成测试用例。

### 输入

```
用户上传文件:
- mapping.xlsx (Excel 格式，包含表级 mapping 和字段级 mapping 两个工作表)
- TS.docx (表结构设计文档)

用户输入:
"帮我生成这个表的测试用例，我的工号是 q00797588"
```

### 系统执行流程

1. **文档解析**: 
   - 读取 Excel mapping 文件，转换为 Markdown 表格
   - 提取 TS 文档内容
2. **意图识别**: 分类为 class_type=3 (初次生成)
3. **TS 要素提取**: 提取 schema、表名、主键、分布方式
4. **知识检索**: 检索测试用例设计规范
5. **脑图生成**: Agent 生成 Mermaid 格式测试用例脑图
6. **等待确认**: 输出脑图并请求用户确认

### Excel 转 Markdown 处理

系统内部自动执行：
```python
# 读取 Excel 表级 mapping
表级 mapping = excel_to_markdown('mapping.xlsx', sheet_name='表级 mapping')

# 读取 Excel 字段级 mapping
字段级 mapping = excel_to_markdown('mapping.xlsx', sheet_name='字段级 mapping')
```

转换后提供给 LLM 的格式：
```markdown
## 表级 mapping

| 序号 | 目标表 | 来源表 | 关联条件 | 过滤条件 |
|------|--------|--------|----------|----------|
| 1 | fin_dwb.table_i | src.table_a | a.id = b.id | a.status = 'Y' |

## 字段级 mapping

| 目标字段 | 来源字段 | 转换规则 | 说明 |
|----------|----------|----------|------|
| id | id | 直接复制 | 主键 |
| name | name | 直接复制 | 名称 |
```

### 输出示例

```markdown
## 测试要点脑图

graph LR
    root("dwb_ltc_invoice_i<br/>测试用例脑图")
    
    L1_1("用户指定的测试要点")
    L1_2("基础一致性")
    L1_3("字段级逻辑")
    
    root --> L1_1
    root --> L1_2
    root --> L1_3
    
    L1_1 --> L3_1_1("IT 用例表视图检查_dwb_ltc_invoice_i_目标表存在检查")
    L1_1 --> L3_1_2("IT 用例表视图检查_dwb_ltc_invoice_i_验证整表有数")
    L1_2 --> L3_2_1("IT 用例表视图检查_dwb_ltc_invoice_i_来源表与目标表记录数一致")
    L1_3 --> L3_3_1("IT 用例字段检查_dwb_ltc_invoice_i_发票编码验证枚举值有效性")
    L1_3 --> L3_3_2("IT 用例字段检查_dwb_ltc_invoice_i_发票编码转维成功率 100%")

## 解释

已为您生成 5 个测试用例，包含：
- 表视图检查：验证目标表存在且有数据
- 基础一致性：验证来源表与目标表记录数一致
- 字段级逻辑：验证发票编码的枚举值和转维成功率

请问该测试用例脑图生成是否正确？
如需修改请直接告诉我，无需修改请回复"**确认脑图正确，生成测试用例**"。
```

---

## 场景 2: 确认脑图并生成详细用例

用户确认脑图正确，请求生成详细测试用例和 SQL。

### 输入

```
用户输入: "确认脑图正确，生成测试用例"
```

### 系统执行流程

1. **意图识别**: 分类为 class_type=2 (确认执行)
2. **迭代处理**: 遍历每个测试用例
   - 提取 mapping 关键信息
   - 查询知识库 few-shot
   - 生成验证 SQL
   - 执行 SQL 验证
3. **结果聚合**: 合并所有测试用例
4. **Excel 导出**: 调用 HTTP 服务生成 Excel
5. **发送通知**: 发送完成消息到用户 w3 账号

### 输出示例

```markdown
## 正在处理测试用例 1/5 (目标表主键不重复校验)

### 测试用例内容
| Key | Value |
|-----|-------|
| case_name | IT 用例表视图检查_dwb_ltc_invoice_i_主键唯一性检查 |
| level | level1 |
| expected_result | COUNT(invoice_id) = COUNT(DISTINCT invoice_id) |

### 生成的验证 SQL
```sql
SELECT 
  CASE WHEN COUNT(invoice_id) = COUNT(DISTINCT invoice_id) 
  THEN 'PASS' ELSE 'FAIL' END as test_result
FROM fin_dwb.dwb_ltc_invoice_i
WHERE YYYYMM = '202601'
```

### SQL 执行结果
- 状态：SUCCESS
- 结果：PASS
- 执行时间：2.3s

...

## 任务完成

✅ 已生成 5 个测试用例，Excel 文件已发送到您的 welink
📧 接收人：q00797588
```

---

## 场景 3: 修改脑图

用户对生成的脑图提出修改意见。

### 输入

```
用户输入: "脑图中增加一个分区验证的测试点，验证按 YYYYMM 跨年数据跑数正确"
```

### 系统执行流程

1. **意图识别**: 分类为 class_type=1 (修正脑图)
2. **Agent 重新规划**: 在脑图中添加新的测试点
3. **展示修改后脑图**: 等待用户再次确认

### 输出示例

```markdown
## 修改后的测试用例脑图

graph LR
    root("dwb_ltc_invoice_i<br/>测试用例脑图")
    
    L1_1("用户指定的测试要点")
    L1_4("性能相关")
    
    root --> L1_1
    root --> L1_4
    
    L1_1 --> L3_1_1("IT 用例表视图检查_dwb_ltc_invoice_i_目标表存在检查")
    L1_4 --> L3_4_1("可选 -IT 用例表视图检查_dwb_ltc_invoice_i_验证按 YYYYMM 跨年数据跑数正确")

已为您添加分区验证测试点，请确认是否继续生成详细用例？
```
