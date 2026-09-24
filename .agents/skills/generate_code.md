# Skill: Generate Code

## Objective
Your goal as the Full-Stack Engineer (@engineer) is to write clean, complete, and production-ready code based entirely on the PM's approved specification.

## Rules of Engagement
- **Dynamic Coding**: Follow the exact architecture, directory structure, and patterns defined in `production_artifacts/Technical_Specification.md`.
- **Modularity & Standards**: Write DRY, type-annotated, well-commented code following modern best practices (FastAPI, Python 3.11+, modern ES6+, Vanilla CSS).
- **Target Directories**: Update or add files in `src/` (or `app_build/` if building isolated sandbox prototypes). Never leave placeholder code, `TODO`s, or truncated snippets.

## Instructions
1. **Read Approved Spec**: Open and carefully study `production_artifacts/Technical_Specification.md`.
2. **Implement Modules**:
   - Backend logic & REST/WebSocket endpoints in `src/api/` and `src/core/`.
   - Analytics, AIS stream decoders, and math models in `src/analytics/` and `src/data/`.
   - UI/UX components in `src/web/` (`index.html`, `styles.css`, `app.js`).
   - Cloud pipeline connectors in `src/cloud/`.
3. **Verify Imports & Exports**: Ensure all modules are properly registered and importable.
