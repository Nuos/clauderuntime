# B2 → B3 Source Alignment Changelog

## 1. HTML 交付修复

B2 HTML 被用户反馈无法正常查看。B3 做以下修复：

- 所有 HTML 都是完整 `<!doctype html>` 文档；
- 明确 `<meta charset="utf-8">`；
- CSS 全部 inline；
- 不引用本地图片；
- 不依赖 CDN；
- 不依赖 JavaScript framework；
- 根目录放置 `index.html`；
- 每个主 HTML 均可单独离线打开；
- 生成后执行 HTML parse、UTF-8、link/resource dependency 检查。

## 2. 14 横切机制重构

B2 把旧 AUX lifecycle loops 直接命名为 Runtime Crosscut-14，层级不够准确。

B3 按用户提供 `index.html` 重构为真正横切 Harness：

1. Hook Runtime
2. Authorization Pipeline
3. Context Shaping
4. Context Assembly
5. Capability Assembly
6. Tool Orchestration
7. Streaming Tool Execution
8. Recovery
9. Result Processing/Budget
10. Session/Transcript
11. Subagent Orchestration
12. Isolation
13. Trust Lifecycle
14. Runtime Config

旧 AUX 仍全部保留为 Lifecycle Verification Set，并映射到 B3 canonical owner。

## 3. 行为圣经扩大

v4.0 新增/强化：

- 13+ 设计原则；
- Policy/Authorization/Isolation 明确分层；
- 9-step agent turn；
- dual tool execution paths；
- 5 recovery families；
- 5 stop categories；
- Safety defense-in-depth；
- Permission mode vs behavior；
- 9 context sources；
- Tool Registry/Pool/Orchestration/Execution 四分法；
- Session/Transcript/Context/Memory 四分法；
- legacy AUX mapping；
- PR evidence gate；
- source-aligned completion state rules。

## 4. 优先级未放宽

B3 不引入新的产品优先级。

仍只有：

```text
CORE_REQUIRED
EVIDENCE_REQUIRED
DEFERRED
```

外围研发继续默认延期，直到 7/5/14 全部闭环。
