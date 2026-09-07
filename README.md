# Agent Travel Planner · 多 Agent 旅行规划助手

> 基于多 Agent + MCP 协议的端到端旅行规划应用，配套可靠性改进与自动化评测体系。
> 本仓库基于 [Datawhale hello-agents](https://github.com/datawhalechina/hello-agents) 第十三章教程扩展，新增工具降级、幻觉校验、自动化评测等工程化能力。

## 这是什么

一个面向"出行规划"场景的多 Agent Web 应用：用户填目的地 / 日期 / 偏好，系统自动生成带预算、地图、每日安排的可编辑行程。

和原教程相比，本仓库的**差异化**：

- **可靠性改进**：在 4 个专门 Agent 上落地工具调用降级与搜索结果幻觉校验策略
- **自动化评测**：搭建 30+ 条测试用例 + 成功率 / 完成率 / 幻觉率评分脚本
- **前后对比**：跑出"改造前 / 改造后"的硬数字，作为简历可引用证据

## 架构

```
┌─────────────┐   HTTP    ┌──────────────┐   MCP   ┌────────────┐
│  Vue3 + TS  │ ────────► │   FastAPI    │ ──────► │ amap MCP   │
│  Frontend   │           │   Backend    │         │  Server    │
└─────────────┘           └──────┬───────┘         └────────────┘
                                 │
                          ┌──────▼───────┐
                          │  4 个 Agent  │
                          │  - 景点搜索  │
                          │  - 天气查询  │
                          │  - 酒店推荐  │
                          │  - 行程规划  │
                          └──────────────┘
```

## 技术栈

| 层 | 选型 |
| --- | --- |
| 前端 | Vue3 + TypeScript + Axios |
| 后端 | Python 3.10+ / FastAPI / Pydantic |
| Agent | HelloAgents 框架（Datawhale 开源）+ 自定义 ToolDispatcher |
| 协议 | MCP（Model Context Protocol）/ amap-mcp-server |
| LLM | OpenAI 兼容 API（DeepSeek / 智谱 / OpenAI） |
| 评测 | 自研 Python 脚本 + 30 条测试集 |

## 快速开始

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api.main:app --reload

# 另一个终端
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 即可使用。

## 评测（与教程最大差异）

```bash
python scripts/run_eval.py --baseline
python scripts/run_eval.py
python scripts/score_eval.py
```

输出示例（待跑出真实数据后填）：

| 指标 | 改造前 | 改造后 | 样本量 |
| --- | --- | --- | --- |
| 成功率 | TBD | TBD | 30 |
| 完成率 | TBD | TBD | 30 |
| 幻觉率 | TBD | TBD | 30 |
| 平均时延 | TBD | TBD | 30 |

## 项目结构

```
agent-travel-planner/
├── backend/            # FastAPI + Agents
├── frontend/           # Vue3 + TypeScript
├── docs/
│   ├── eval-methodology.md
│   └── reliability-notes.md
└── README.md
```

## 进展

- [x] 完成 Datawhale hello-agents Ch13 全流程跟随实践
- [x] 搭建 FastAPI 后端 + Vue3 前端 + 4 个 Agent + MCP 集成
- [ ] 实现 ToolDispatcher（重试 + 降级 + 优雅失败）
- [ ] 实现 Pydantic 强约束 + 强制引用 prompt
- [ ] 跑 30 条样本 baseline
- [ ] 跑改造后数字
- [ ] 写对比报告

## 致谢

本仓库基于 [Datawhale hello-agents](https://github.com/datawhalechina/hello-agents) 第十三章教程扩展。
感谢 [Datawhale](https://github.com/datawhalechina) 社区的 HelloAgents 框架与高德 MCP 服务器。

## License

MIT
