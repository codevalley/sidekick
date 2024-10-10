# Workflow for Bioscope Project

## Key Documents

### Primary Documents

1. **progress.md**
   - Purpose: Tracks current development chunk and task status
   - Content:
     - Current chunk title and description
     - Completed tasks (with checkmarks)
     - In-progress tasks (with status updates)
     - Pending tasks
     - Notes on blockers or issues

2. **completed.md**
   - Purpose: Archives completed tasks and milestones
   - Content: Comprehensive list of completed tasks, organized by development chunks

### Foundational Documents

1. **blueprint.md**
   - Purpose: Outlines project vision and high-level features
   - Content: Project goals, feature descriptions, and design philosophy

2. **spec.md**
   - Purpose: Details features, user journeys, and workflows
   - Content: In-depth descriptions of app functionalities and user flows

3. **TechDesign.md**
   - Purpose: Defines architecture and design patterns
   - Content: tech stack, architecture, design patterns, and best practices details

## Workflow Process

### Task Selection and Execution

1. Review `progress.md` to identify the current development chunk and available tasks.
2. Select a task based on priority and dependencies.
3. Before starting, review relevant sections in foundational documents:
   - `blueprint.md` for feature details
   - `spec.md` for UI/UX guidelines
   - `TechDesign.md` for data layer implementation

4. Execute the task, referring to the codebase and foundational documents as needed.
5. Update `progress.md` with task status and any notes or blockers encountered.

### Code Implementation Guidelines

1. Follow the clean architecture principles outlined in `TechDesign.md`.
2. Implement features as described in `Approach.md`.
3. Add tasks for testing and quality assurance, after finishing the feature implementation.
4. Ensure that the code is well-documented, with inline comments for complex logic.
5. Update relevant documentation if the implementation differs from the original plan.

### Testing and Quality Assurance

1. Write unit tests for new functionality.
2. Ensure UI components are responsive and follow the design language.
3. Test for edge cases and error scenarios.

### Documentation

1. Add inline comments for complex logic.
2. Update relevant documentation if the implementation differs from the original plan.

### Task Completion

1. Mark the task as completed in `progress.md`.
2. If the task completes a chunk, move the chunk details to `completed.md`.
3. Push code changes and update relevant documentation.

## Handling Blockers and Issues

1. Document any blockers or issues in `progress.md`.
2. If a blocker requires changes to the project plan or approach:
   - Note the suggested changes in the respective document under a "Suggestions" section.
   - Update `progress.md` with a reference to the suggested change.

## AI Agent Guidelines

1. Always start by reviewing `progress.md` and the current state of the project.
2. Consult foundational documents for context before implementing features.
3. Adhere strictly to the established architecture and design patterns.
4. When in doubt, refer to the existing codebase for implementation examples.
5. Communicate clearly about task progress, blockers, and completion in `progress.md`.
6. Suggest improvements or optimizations when appropriate, noting them in the relevant documents.
