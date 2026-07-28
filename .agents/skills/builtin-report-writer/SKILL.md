---
name: builtin_report_writer
description: Writes a structured markdown report to the designated session reports directory.
parameters:
  type: object
  properties:
    session_id:
      type: string
      description: The current session ID provided in your system prompt.
    report_name:
      type: string
      description: The name of the report file (e.g., 'xgboost_analysis').
    content:
      type: string
      description: The full markdown content of the report.
  required:
    - session_id
    - report_name
    - content
---

# Built-in Report Writer

Allows the agent to safely save its research findings, data analysis results, or final reports to the workspace in an organized folder structure.
