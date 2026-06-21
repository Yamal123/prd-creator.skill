# PRD chapter framework

Use only chapters supported by project evidence or user requirements. Number files as `01-项目背景.md`; each generated chapter must have one H1 and at least two H2 sections.

| No. | Chapter | Evidence |
|---|---|---|
| 01 | 项目背景 | README, existing PRD, user input |
| 02 | 技术路线 | architecture docs, manifests, configuration |
| 03 | 功能介绍 | routes, components, API definitions |
| 04 | 用户场景 | user input, user stories |
| 05–16 | 需求详述 | feature modules, documents, user requirements |
| 17 | 非功能性需求 | explicit performance, security, availability requirements |
| 18 | 数据设计 | schemas and migrations |
| 19 | 验收标准 | functional requirements and user confirmation |
| 20 | 项目计划 | TODOs, milestones, Git history |
| 21 | 度量体系 | analytics code and user-defined metrics |
| 22 | 附件 | source document and terminology index |

## Content rules

- Link to existing project documents instead of copying them wholesale.
- Label inferred content and cite the source file where useful.
- Write `> 待确认: 具体问题` when business input is required.
- Omit unsupported claims; never fabricate metrics, deadlines, users, or acceptance criteria.
- Keep requirements testable and traceable to evidence.
