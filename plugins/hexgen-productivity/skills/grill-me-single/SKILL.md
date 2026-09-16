---
name: grill-me-single
description: 逐题澄清计划、设计、决策或想法；每次只问一个问题并附推荐答案。已授权执行的任务逐项确认、实施和验证；仅讨论或只读审查保持讨论。
---

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Keep routine questions concise: state the issue, your recommendation, and material consequences. Do not append repeated skill names, links, quotations, or explanations of the one-question rule. Explain an additional approval requirement or genuine blocker when necessary.

Honor the task's existing scope. Discussion-only and read-only review requests remain non-mutating; a design answer alone does not authorize implementation.

For an authorized implementation or remediation task, reach shared understanding per actionable item: clarify it, obtain the user's decision, implement the agreed change, perform appropriate validation, then briefly report what changed, why, and any remaining risk before moving to the next item. Reuse existing implementation authorization; do not wait for a separate confirmation that the whole discussion is complete.

If the current item depends on unresolved decisions, ask those one at a time before implementing. If implementation or validation is blocked, state the specific blocker instead of silently moving to an unrelated item. Do not widen the approved scope.
