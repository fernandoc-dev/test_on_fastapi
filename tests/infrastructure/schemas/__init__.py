"""
Test schemas - Independent models that represent the expected API contract.

These schemas are the source of truth for what the API should return.
They are independent from app schemas to ensure tests validate that
the app implementation satisfies the requirements, not just that it's
internally consistent.

Following TDD principles:
- Test schemas define the specification (what the client expects)
- App schemas are the implementation (what the app provides)
- Tests validate that implementation matches specification
"""

