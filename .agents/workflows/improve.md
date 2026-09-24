---
description: Run an autonomous improvement cycle on an existing system component
---

When the user types `/improve <target>`, analyze the targeted component, draft architectural improvements, gain approval, and execute enhancements.

### Execution Sequence:
1. **Product Manager (@pm)**: Analyze `<target>`, inspect existing code in `src/`, draft an improvement specification in `production_artifacts/Technical_Specification.md`, and pause for user approval.
2. **Full-Stack Engineer (@engineer) & Quant (@quant)**: Implement the optimized algorithms, upgraded UI/UX, or enhanced data pipelines.
3. **QA Engineer (@qa)**: Execute test suite (`pytest tests/`), add regression tests for the improved component, and verify all diagnostics pass.
4. **DevOps Master (@devops)**: Launch the server, verify endpoints, and present the improved feature.
