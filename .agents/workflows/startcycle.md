---
description: Start the Autonomous AI Developer Pipeline sequence with a new feature or idea
---

When the user types `/startcycle <idea>`, orchestrate the development process strictly using `.agents/agents.md` and `.agents/skills/`.

### Autonomous Execution Sequence:
1. **Product Manager (@pm)**: Execute `write_specs.md` using `<idea>`.
   - Write comprehensive specification to `production_artifacts/Technical_Specification.md`.
   - **Pause for user approval**: Ask the user explicitly:
     > "Do you approve of this tech stack and specification? You can safely open `production_artifacts/Technical_Specification.md` and add comments or modifications if you want me to rework anything!"
   - *Wait for user approval before continuing to step 2. If the user requests modifications, revise and ask again.*
2. **Full-Stack Engineer (@engineer)**: Once approved, execute `generate_code.md` to implement all components defined in `production_artifacts/Technical_Specification.md`.
3. **Quantitative Analyst (@quant)**: Review mathematical accuracy, geofencing models, and data streams.
4. **QA Engineer (@qa)**: Execute `audit_code.md` — run tests, identify flaws, and commit fixes.
5. **DevOps Master (@devops)**: Execute `deploy_app.md` or `deploy_cloud_run.md` to verify the local server or cloud deployment and present live links to the user.
