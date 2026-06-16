# API Automation Framework

A data-driven API test framework built with Python, pytest, and Allure. Test cases are defined in YAML — no per-case code required.

<img width="1389" height="868" alt="image" src="https://github.com/user-attachments/assets/4d3d60cd-3529-4ea1-87b1-b540ba04b137" />

## Stack

- Python + pytest
- Allure report
- YAML-driven test cases (auto-generates pytest code)
- MySQL + Redis for data assertion and caching
- Faker for dynamic test data
- DingTalk / email notifications
- Jenkins CI support

## Features

- YAML test case definitions with auto-generated pytest code
- Multi-interface dependency (chain A → B → C response data)
- DB assertion: write SQL directly in the test case, no extra code
- Multi-assertion per case (response + SQL)
- Proxy recording to generate YAML cases from live traffic
- Parallel execution via pytest-xdist
- Structured logging with configurable levels
- Swagger → YAML case conversion

## Project Structure

```
├── common/          # Config and environment settings
├── data/            # YAML test case definitions
├── test_case/       # Auto-generated pytest code
├── utils/           # Assertion, cache, HTTP, notify helpers
├── logs/            # Run logs
├── report/          # Allure reports
└── run.py           # Entry point
```

## Reference

Based on the open-source framework by Yu Shaoqi:
[gitee.com/yu_xiao_qi/pytest-auto-api2](https://gitee.com/yu_xiao_qi/pytest-auto-api2)
