---
name: builtin_python_sandbox
description: Creates an isolated python environment using uv, installs dependencies, and runs python code for data analysis or machine learning tasks.
parameters:
  type: object
  properties:
    session_id:
      type: string
      description: The current session ID provided in your system prompt.
    experiment_name:
      type: string
      description: A short, url-safe name for this experiment (e.g., 'xgboost_iris_test').
    code:
      type: string
      description: The full Python source code to execute.
    dependencies:
      type: array
      items:
        type: string
      description: List of pip packages to install (e.g., ['xgboost', 'pandas']).
  required:
    - session_id
    - experiment_name
    - code
---

# Built-in Python Sandbox

Provides agents with a secure, isolated sandbox to run arbitrary Python code, useful for training machine learning models or analyzing datasets safely.
