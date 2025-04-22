# 测试场景说明

本目录包含了用于测试不同AI API性能的对话场景JSON文件。每个文件包含一个或多个测试场景，每个场景由多轮对话组成。

## 文件说明

1. **simple_test.json** - 简单的基础测试，包含基本问答、上下文记忆和中文理解测试
2. **basic_test.json** - 基础知识问答测试，评估AI的通用知识
3. **creative_test.json** - 创意生成测试，评估AI的创造力和想象力
4. **reasoning_test.json** - 逻辑推理测试，评估AI的推理和问题解决能力
5. **comprehensive_test.json** - 综合测试，包含中文理解、上下文记忆和多轮指令测试

## 使用方法

使用以下命令运行测试：

```bash
python main_new.py multi-turn --file test_scenarios/文件名.json
```

例如：

```bash
python main_new.py multi-turn --file test_scenarios/simple_test.json
```

## 测试结果

测试结果将保存在以下位置：
- 对话历史：`conversations/` 目录
- 评估结果：`evaluations/` 目录
- 测试结果：`results/` 目录

## 自定义测试

您可以创建自己的测试场景JSON文件，格式如下：

```json
[
  {
    "name": "测试名称",
    "description": "测试描述",
    "turns": [
      {"prompt": "第一轮问题"},
      {"prompt": "第二轮问题"},
      ...
    ]
  },
  ...
]
```
