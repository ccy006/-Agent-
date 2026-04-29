# Multi-Agent Code Refactoring / Technical Debt Cleanup System

一个可运行的多 Agent 协作代码重构与技术债清理系统。

## 功能

- 扫描项目代码中的技术债：TODO、FIXME、长函数、过长文件、重复片段、复杂度风险
- 多 Agent 协作：
  - `AnalyzerAgent`：分析代码与技术债
  - `PlannerAgent`：制定重构计划
  - `RefactorAgent`：生成和应用安全补丁
  - `TestAgent`：运行测试 / 静态检查
  - `ReviewerAgent`：复核结果并输出报告
- 默认使用本地规则引擎，不依赖外部 API
- 预留 LLM 接口，后续可以接 OpenAI、Claude、本地模型等

## 快速开始

```bash
cd multi_agent_refactor_system
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python main.py --target ./sample_project --apply
```

## 不实际修改代码，只生成报告

```bash
python main.py --target ./sample_project
```

## 指定输出目录

```bash
python main.py --target ./sample_project --apply --out ./reports
```

## 项目结构

```text
multi_agent_refactor_system/
├─ main.py
├─ requirements.txt
├─ agents/
├─ core/
├─ sample_project/
└─ tests/
```

## 安全策略

默认只应用低风险重构：

- 删除行尾空格
- 规范文件末尾换行
- 把 `print()` 标记为可替换日志的技术债
- 生成建议，但不自动做危险重构

复杂重构建议先人工 review。
