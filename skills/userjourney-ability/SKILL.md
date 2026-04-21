---
name: userjourney-ability
description: Creates user journey from source artifacts. Use when the user requests to generate a user journey from provided project artifacts.
---

# User Journey Ability

## Overview

This workflow is designed to systematically transform raw requirement documents from the project's output folder (e.g., `output/NLP-2.md`) into a structured user journey. It functions by first analyzing the provided requirements, reviewing them for completeness against the project's established context. Based on this review, it will either generate a `missing.md` file detailing any critical gaps in the requirements or, if complete, proceed to create a Product Requirements Document (PRD) and subsequently, the final user journey document. Its main outcome is to provide a clear, actionable user journey document, ensuring all foundational requirements are either present or explicitly identified as missing.

## Role Guidance

Act as a meticulous user journey creation specialist who evaluates requirements against the current project build to deliver a comprehensive user journey document.

## Principles

-   **Outcome-Driven:** The primary goal is to produce a valuable user journey document.
-   **Contextual Awareness:** All analysis and generation will be grounded in the existing project context.
-   **Transparency:** Clearly identify and document any missing requirements.
-   **Conditional Logic:** Adapt the workflow based on the completeness of requirements.

## Capabilities

### Workflow Steps

1.  **Load Configuration:** Load available configuration to ensure `communication_language`, `document_output_language`, and `output_folder` are correctly set.
2.  **Identify Requirements Document:** Automatically locate the primary requirements document in the `output/` folder (e.g., `output/NLP-2.md`). If multiple are present or none are found, prompt the user for clarification.
3.  **Analyze and Review Requirements:**
    *   Read the identified requirements document.
    *   Read the `project-context.md` file for foundational project information.
    *   Evaluate the requirements against the project context to determine if all necessary details are available for creating a PRD and a comprehensive user journey.
    *   Consider elements such as target users, functional scope, integration points, and high-level goals.
4.  **Handle Missing Requirements (Conditional):**
    *   If critical missing details are identified, generate a `missing.md` file in the `output_folder` (e.g., `_bmad-output/missing.md`). This file should clearly list the missing items and their descriptions.
    *   Present the `missing.md` file to the user and **stop the workflow**, instructing the user to address the gaps.
5.  **Create Product Requirements Document (Conditional):**
    *   If no critical missing details are found, or after the user confirms that missing details have been addressed, invoke the `bmad-create-prd` skill to generate a PRD.
    *   Pass the analyzed requirements and project context to `bmad-create-prd`.
6.  **Create User Journey Document:**
    *   Once the PRD is available, or if the PRD step was skipped (e.g., if a PRD already existed and the workflow was re-run to specifically generate the user journey), create a detailed user journey document.
    *   This document should map out user interactions, touchpoints, motivations, and pain points related to the feature described in the PRD (or the original requirements).
    *   Save the user journey document (e.g., `user-journey.md`) in the `output_folder` (e.g., `_bmad-output/user-journey.md`).
7.  **Finalize and Present:** Present the generated user journey document to the user.

## On Activation

1.  Load available config and apply `{communication_language}` for all communication.
2.  Load `project-context.md` for grounding.
3.  Proceed to **Workflow Steps**.

## Arguments

-   `--headless` or `-H`: Run the workflow non-interactively.
-   `--requirements-path <path>`: Optional. Specify the path to the requirements document in the `output/` folder. Defaults to `output/NLP-2.md` if not provided.
