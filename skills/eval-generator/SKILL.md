---
name: eval-generator
description: Generate automated eval tests from Jira acceptance criteria for validation
---

# Eval Generator

Generate automated eval test files from Jira acceptance criteria. Converts human-readable acceptance criteria into executable pytest tests for validation.

## When to Use This Skill

Use this skill to:
- Convert Jira acceptance criteria into automated tests
- Generate eval test structure for an issue
- Create validation tests before implementation
- Ensure acceptance criteria are testable

## Usage

```bash
# Generate evals from Jira issue
/eval-generator ABI-123

# Generate with custom test framework
/eval-generator ABI-123 --framework pytest

# Dry run (show tests without creating files)
/eval-generator ABI-123 --dry-run
```

## Acceptance Criteria Format

### Expected Format in Jira

Acceptance criteria should be structured in the issue description or a custom field:

```markdown
## Acceptance Criteria

### Functional
- [ ] API rate limiting enforces 100 requests/minute per user
- [ ] Rate limit headers included in response (X-RateLimit-Remaining, X-RateLimit-Reset)
- [ ] 429 status code returned when limit exceeded
- [ ] Rate limit resets after 1 minute window

### Performance
- [ ] Rate limit check adds < 10ms latency to API calls
- [ ] System handles 1000 concurrent users without degradation
- [ ] Memory usage remains stable under load

### Quality
- [ ] Unit test coverage ≥ 80%
- [ ] Integration tests validate rate limiting behavior
- [ ] No security vulnerabilities (passed Snyk scan)
- [ ] API documentation updated

### Edge Cases
- [ ] Handles missing user context gracefully
- [ ] Works with distributed rate limit store (Redis)
- [ ] Correctly handles clock skew scenarios
```

### Alternative Formats

**Simple checklist:**
```markdown
Acceptance Criteria:
- API returns 429 when rate limit exceeded
- Rate limit is 100 req/min per user
- Response includes rate limit headers
```

**Given/When/Then:**
```markdown
Scenario: Rate limiting enforcement
Given a user makes 100 requests in 1 minute
When the user makes the 101st request
Then the API returns 429 status code
And the response includes X-RateLimit-Reset header
```

## Process

### Step 1: Fetch Jira Issue

Get issue details including acceptance criteria:

```javascript
const issue = await mcp__atlassian__jira_get_issue({
  issueKey: issueKey,
  fields: ['description', 'summary', 'customfield_*']
})
```

Extract acceptance criteria from:
1. Custom field (if configured): `issue.customfield_xxxxx`
2. Description section: Parse "## Acceptance Criteria" section
3. Description body: Look for checklist items

### Step 2: Parse Acceptance Criteria

Parse criteria into categories:

```javascript
const criteria = {
  functional: [
    "API rate limiting enforces 100 requests/minute per user",
    "Rate limit headers included in response",
    "429 status code returned when limit exceeded"
  ],
  performance: [
    "Rate limit check adds < 10ms latency",
    "System handles 1000 concurrent users"
  ],
  quality: [
    "Unit test coverage ≥ 80%",
    "Integration tests validate behavior"
  ],
  edgeCases: [
    "Handles missing user context gracefully",
    "Works with distributed store"
  ]
}
```

### Step 3: Generate Test Structure

Create directory structure:

```
tests/evals/{issue-key}/
├── __init__.py
├── test_functional.py
├── test_performance.py
├── test_quality.py
├── test_edge_cases.py
├── conftest.py           # Fixtures and setup
└── README.md             # Test documentation
```

### Step 4: Generate Functional Tests

Convert functional criteria to pytest tests:

**Input:**
```
- API rate limiting enforces 100 requests/minute per user
```

**Output (`test_functional.py`):**
```python
import pytest
from tests.helpers import api_client

def test_rate_limiting_enforces_limit():
    """API rate limiting enforces 100 requests/minute per user"""
    user_id = "test-user"
    
    # Make 100 requests - should all succeed
    for i in range(100):
        response = api_client.get('/api/endpoint', user=user_id)
        assert response.status_code == 200, f"Request {i+1} failed"
    
    # 101st request should be rate limited
    response = api_client.get('/api/endpoint', user=user_id)
    assert response.status_code == 429, "Expected 429 Too Many Requests"

def test_rate_limit_headers_included():
    """Rate limit headers included in response"""
    response = api_client.get('/api/endpoint', user='test-user')
    
    assert 'X-RateLimit-Remaining' in response.headers, \
        "Missing X-RateLimit-Remaining header"
    assert 'X-RateLimit-Reset' in response.headers, \
        "Missing X-RateLimit-Reset header"
    
    # Validate header values
    remaining = int(response.headers['X-RateLimit-Remaining'])
    assert 0 <= remaining <= 100, "Invalid remaining count"

def test_429_status_on_limit_exceeded():
    """429 status code returned when limit exceeded"""
    user_id = "test-user-2"
    
    # Exhaust rate limit
    for _ in range(100):
        api_client.get('/api/endpoint', user=user_id)
    
    # Next request should return 429
    response = api_client.get('/api/endpoint', user=user_id)
    assert response.status_code == 429
    assert 'Retry-After' in response.headers or 'X-RateLimit-Reset' in response.headers
```

### Step 5: Generate Performance Tests

Convert performance criteria to benchmark tests:

**Input:**
```
- Rate limit check adds < 10ms latency
```

**Output (`test_performance.py`):**
```python
import pytest
import time
from tests.helpers import api_client

def test_rate_limit_latency():
    """Rate limit check adds < 10ms latency to API calls"""
    # Measure baseline latency without rate limiting
    response = api_client.get('/api/health')  # No rate limit
    
    # Measure latency with rate limiting
    start = time.time()
    response = api_client.get('/api/endpoint', user='perf-test')
    latency = (time.time() - start) * 1000  # Convert to ms
    
    assert response.status_code == 200
    assert latency < 10, f"Rate limit check took {latency:.2f}ms (expected < 10ms)"

@pytest.mark.benchmark
def test_concurrent_users_performance():
    """System handles 1000 concurrent users without degradation"""
    import concurrent.futures
    
    def make_request(user_id):
        start = time.time()
        response = api_client.get('/api/endpoint', user=f'user-{user_id}')
        duration = time.time() - start
        return response.status_code, duration
    
    # Simulate 1000 concurrent users
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request, i) for i in range(1000)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # Check all requests succeeded
    success_count = sum(1 for status, _ in results if status == 200)
    assert success_count >= 950, f"Only {success_count}/1000 requests succeeded"
    
    # Check response times remain reasonable
    avg_duration = sum(d for _, d in results) / len(results)
    assert avg_duration < 0.1, f"Average response time {avg_duration:.3f}s too high"
```

### Step 6: Generate Quality Tests

Convert quality criteria to coverage/lint tests:

**Input:**
```
- Unit test coverage ≥ 80%
```

**Output (`test_quality.py`):**
```python
import pytest
import subprocess
import json

def test_unit_test_coverage():
    """Unit test coverage ≥ 80%"""
    # Run pytest with coverage
    result = subprocess.run(
        ['pytest', '--cov=src', '--cov-report=json', '--cov-report=term'],
        capture_output=True,
        text=True
    )
    
    # Read coverage report
    with open('coverage.json', 'r') as f:
        coverage_data = json.load(f)
    
    total_coverage = coverage_data['totals']['percent_covered']
    assert total_coverage >= 80, \
        f"Coverage is {total_coverage:.1f}% (expected ≥ 80%)"

def test_security_scan_passes():
    """No security vulnerabilities (passed Snyk scan)"""
    result = subprocess.run(
        ['snyk', 'test', '--json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        scan_results = json.loads(result.stdout)
        vulnerabilities = scan_results.get('vulnerabilities', [])
        high_severity = [v for v in vulnerabilities if v['severity'] == 'high']
        
        assert len(high_severity) == 0, \
            f"Found {len(high_severity)} high-severity vulnerabilities"
```

### Step 7: Generate Edge Case Tests

Convert edge cases to test scenarios:

**Input:**
```
- Handles missing user context gracefully
```

**Output (`test_edge_cases.py`):**
```python
import pytest
from tests.helpers import api_client

def test_handles_missing_user_context():
    """Handles missing user context gracefully"""
    # Request without user context
    response = api_client.get('/api/endpoint')  # No user header
    
    # Should return 401 or use default rate limit
    assert response.status_code in [200, 401], \
        "Should handle missing user gracefully"
    
    if response.status_code == 200:
        # If allows anonymous access, should still rate limit
        assert 'X-RateLimit-Remaining' in response.headers

def test_distributed_rate_limit_store():
    """Works with distributed rate limit store (Redis)"""
    # Make requests that should share rate limit across instances
    user_id = "distributed-test"
    
    # Request 1 - increment counter
    response1 = api_client.get('/api/endpoint', user=user_id)
    remaining1 = int(response1.headers['X-RateLimit-Remaining'])
    
    # Request 2 - should see decremented counter
    response2 = api_client.get('/api/endpoint', user=user_id)
    remaining2 = int(response2.headers['X-RateLimit-Remaining'])
    
    assert remaining2 == remaining1 - 1, \
        "Distributed rate limit not working correctly"
```

### Step 8: Generate Test Configuration

Create `conftest.py` with fixtures:

```python
import pytest
from your_app import create_app
from tests.helpers import APIClient

@pytest.fixture(scope="session")
def app():
    """Create application instance for testing"""
    app = create_app(config='testing')
    return app

@pytest.fixture(scope="session")
def api_client(app):
    """Create API client for testing"""
    return APIClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limits between tests"""
    # Clear Redis or rate limit store
    yield
    # Cleanup after test
```

Create `README.md`:

```markdown
# Eval Tests for ABI-123: Add API Rate Limiting

## Overview

Automated validation tests for acceptance criteria.

## Running Tests

### All tests
\`\`\`bash
pytest tests/evals/ABI-123/ -v
\`\`\`

### By category
\`\`\`bash
pytest tests/evals/ABI-123/test_functional.py
pytest tests/evals/ABI-123/test_performance.py
pytest tests/evals/ABI-123/test_quality.py
\`\`\`

### With coverage
\`\`\`bash
pytest tests/evals/ABI-123/ --cov=src --cov-report=html
\`\`\`

## Acceptance Criteria Coverage

- ✓ Functional: 4/4 tests
- ✓ Performance: 2/2 tests
- ✓ Quality: 2/2 tests
- ✓ Edge Cases: 2/2 tests

Total: 10 tests covering all acceptance criteria
```

### Step 9: Output Summary

Return summary of generated tests:

```markdown
Generated eval tests for ABI-123: Add API Rate Limiting

Test Structure:
📁 tests/evals/ABI-123/
  ✓ test_functional.py (4 tests)
  ✓ test_performance.py (2 tests)
  ✓ test_quality.py (2 tests)
  ✓ test_edge_cases.py (2 tests)
  ✓ conftest.py (fixtures)
  ✓ README.md (documentation)

Total: 10 tests generated

Next steps:
1. Review generated tests
2. Implement the feature
3. Run evals: pytest tests/evals/ABI-123/ -v
4. All tests must pass before creating PR
```

## Output Schema

```json
{
  "issueKey": "ABI-123",
  "testDirectory": "tests/evals/ABI-123",
  "tests": {
    "functional": {
      "file": "test_functional.py",
      "count": 4,
      "tests": [
        "test_rate_limiting_enforces_limit",
        "test_rate_limit_headers_included",
        "test_429_status_on_limit_exceeded",
        "test_rate_limit_resets"
      ]
    },
    "performance": {
      "file": "test_performance.py",
      "count": 2,
      "tests": [
        "test_rate_limit_latency",
        "test_concurrent_users_performance"
      ]
    },
    "quality": {
      "file": "test_quality.py",
      "count": 2,
      "tests": [
        "test_unit_test_coverage",
        "test_security_scan_passes"
      ]
    },
    "edgeCases": {
      "file": "test_edge_cases.py",
      "count": 2,
      "tests": [
        "test_handles_missing_user_context",
        "test_distributed_rate_limit_store"
      ]
    }
  },
  "totalTests": 10,
  "filesCreated": [
    "tests/evals/ABI-123/__init__.py",
    "tests/evals/ABI-123/test_functional.py",
    "tests/evals/ABI-123/test_performance.py",
    "tests/evals/ABI-123/test_quality.py",
    "tests/evals/ABI-123/test_edge_cases.py",
    "tests/evals/ABI-123/conftest.py",
    "tests/evals/ABI-123/README.md"
  ]
}
```

## Running Generated Evals

### Basic execution

```bash
# All evals for issue
pytest tests/evals/ABI-123/ -v

# Specific category
pytest tests/evals/ABI-123/test_functional.py

# With output
pytest tests/evals/ABI-123/ -v --tb=short
```

### With coverage

```bash
pytest tests/evals/ABI-123/ --cov=src --cov-report=html --cov-report=term
```

### Performance benchmarks

```bash
pytest tests/evals/ABI-123/test_performance.py -v --benchmark-only
```

### CI/CD integration

```bash
pytest tests/evals/ABI-123/ --junitxml=results.xml --cov-report=xml
```

## Customization

### Test templates

Place custom test templates in `.claude/eval-templates/`:

```
.claude/eval-templates/
├── functional_template.py
├── performance_template.py
└── conftest_template.py
```

Templates use Jinja2 syntax with variables:
- `{{ issue_key }}`
- `{{ criteria }}`
- `{{ test_name }}`

### Test framework support

**pytest (default):**
```bash
/eval-generator ABI-123 --framework pytest
```

**unittest:**
```bash
/eval-generator ABI-123 --framework unittest
```

**jest (for JavaScript):**
```bash
/eval-generator ABI-123 --framework jest
```

## Integration with Implementation

**Used by `/autonomous-implement`:**
```javascript
// Step 1: Generate evals from acceptance criteria
const evals = await skill('eval-generator', issue.key)

// Step 2: Implement feature
await skill('implement-plan', plan)

// Step 3: Run evals
const results = await runPytest(`tests/evals/${issue.key}/`)

// Step 4: Only create PR if evals pass
if (results.passed === results.total) {
  await skill('create-pr')
}
```

## Error Handling

**No acceptance criteria found:**
```
Error: No acceptance criteria found for ABI-123

Add acceptance criteria to:
- Custom field "Acceptance Criteria"
- Issue description under "## Acceptance Criteria"
- Issue description as checklist items

Example:
## Acceptance Criteria
- [ ] Feature works as expected
- [ ] Performance meets requirements
```

**Cannot parse criteria:**
```
Warning: Could not parse some acceptance criteria

Unparsed items:
- "Something happens" (too vague)
- "Works correctly" (not specific)

Add specific, testable criteria like:
- API returns 200 status code
- Response time < 100ms
- Coverage ≥ 80%
```

## Success Criteria

- [x] Parses acceptance criteria from Jira
- [x] Categorizes criteria (functional, performance, quality, edge cases)
- [x] Generates pytest test files
- [x] Creates test fixtures and configuration
- [x] Generates README documentation
- [x] Returns structured output with test details
- [x] Handles various acceptance criteria formats

## Notes

**Test quality:**
- Generated tests are starting points, not final tests
- Review and customize for your specific needs
- Add assertions based on actual implementation

**Coverage:**
- Aims to cover all acceptance criteria
- May need manual tests for complex scenarios
- Visual/UX criteria may need manual validation

**Maintenance:**
- Update tests when acceptance criteria change
- Keep evals in sync with implementation
- Remove or update tests when features evolve
