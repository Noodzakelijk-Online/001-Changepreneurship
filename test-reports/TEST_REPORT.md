# Test Execution Report

**Generated:** 2026-01-28T08:58:16.447869

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 48 |
| Passed | 25 |
| Failed | 23 |
| Skipped | 0 |
| Pass Rate | 52.1% |
| Duration | 19.96s |

## Test Suites

| Suite | Status | Passed | Failed | Skipped | Duration |
|-------|--------|--------|--------|---------|----------|
| Smoke Tests | FAILED | 3 | 5 | 0 | 3.58s |\n| Unit Tests - Authentication | FAILED | 0 | 1 | 0 | 2.32s |\n| Unit Tests - Assessment | PASSED | 4 | 0 | 0 | 2.09s |\n| API Tests | FAILED | 15 | 14 | 0 | 7.77s |\n| E2E Tests | FAILED | 3 | 3 | 0 | 4.21s |\n
## Coverage

Run `pytest --cov=src --cov-report=html` to generate coverage report.

## Next Steps

- Fix failing tests before deployment\n- Review test failure details in individual suite reports\n