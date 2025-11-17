# Test Schemas

This directory contains **independent schema models** that represent the expected API contract.

## Purpose

These schemas are the **specification** - they define what the API should return according to requirements. They are **independent** from `app/schemas/` to ensure tests validate that the app implementation satisfies the requirements, not just that it's internally consistent.

## TDD Workflow

1. **Requirement changes**: Update the test schema first (e.g., add `new_att` field)
2. **Run tests**: Tests will fail (RED phase) - this is expected
3. **Implement in app**: Update app code to satisfy the test schema
4. **Tests pass**: Implementation now matches specification (GREEN phase)
5. **Refactor**: Improve code while keeping tests green

## Example

```python
# tests/infrastructure/schemas/user.py
class UserSpec(BaseModel):
    id: int
    email: EmailStr
    new_att: str  # ← New requirement added here first

# tests/integration/test_user_crud.py
def test_get_user(client, db_session):
    response = await client.get("/users/1")
    user = UserSpec(**response.json())  # Validates against spec
    assert user.new_att == expected_value  # Business logic validation
```

## Reusability

These schemas can be reused across:
- **Unit tests**: Validate domain logic
- **Integration tests**: Validate API endpoints
- **E2E tests**: Validate complete flows
- **Load tests**: Validate response structure under load

## Naming Convention

- Suffix with `Spec` to distinguish from app schemas: `UserSpec`, `ProjectSpec`, etc.
- Keep structure aligned with API responses, not internal app structure
- Document any business rules or constraints in docstrings
- Note: Avoid "Test" prefix as pytest collects classes starting with "Test" as test classes

## Benefits

1. **Single source of truth**: Test schema defines the contract
2. **Early failure**: Tests fail when app doesn't meet requirements
3. **Documentation**: Schemas document expected API behavior
4. **Refactoring safety**: Changes in app are validated against spec
5. **Version testing**: Can test different API versions independently

