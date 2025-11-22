# E2E Test Suite for Solve Endpoint

Comprehensive end-to-end testing framework for the problem-solving orchestration endpoint. Tests validate the complete flow from problem classification through service resolution to appeal generation.

## Overview

The test suite covers:

- ✅ **Valid Problems**: Multiple problem types across all categories
- ✅ **Invalid Inputs**: Validation error cases
- ✅ **Urgency Detection**: Emergency keywords and marking
- ✅ **Service Levels**: Building-level (OSBB), District (РА), City monopolists, Hotline
- ✅ **All Categories**: Lighting, Water, Heating, Gas, Elevator, Roads, Parking, etc.
- ✅ **Response Structure**: Complete validation of response format
- ✅ **Generated Datasets**: Automatic test case generation from full_dataset.json

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration & fixtures
├── test_solve_e2e.py               # Main E2E test suite
├── fixtures/
│   ├── test_datasets_generator.py  # Dataset generation script
│   └── test_datasets/              # Generated test datasets (JSON files)
│       ├── valid_problems.json
│       ├── invalid_problems.json
│       ├── urgent_problems.json
│       ├── non_urgent_problems.json
│       ├── service_level_*.json
│       ├── category_*.json
│       └── summary.json
```

## Three E2E Test Files (what to run)

There are three E2E test modules in this repository. Together they provide a full coverage suite (collectively ~120 tests).

- `tests/test_solve_e2e.py` (baseline)
  - Purpose: foundational end-to-end checks and validation logic (basic valid/invalid/urgency/service-level tests).
  - Typical size: the original baseline suite used for quick verification.

- `tests/test_solve_e2e_extended.py` (extended)
  - Purpose: additional category coverage and targeted regression checks (covers more categories and edge cases).
  - Typical size: an extended set of cases to validate model behavior across more examples.

- `tests/test_solve_e2e_comprehensive.py` (comprehensive)
  - Purpose: bulk examples and stress/accuracy checks — many examples per category, concurrency, and summary/accuracy reporting.
  - Typical size: the largest file; used to run full accuracy benchmarks and performance checks.

Why three files?
- Separation of concerns: quick smoke tests (`test_solve_e2e.py`), targeted expansion (`test_solve_e2e_extended.py`), and large-scale accuracy/performance runs (`test_solve_e2e_comprehensive.py`).
- This setup keeps quick feedback loops fast while still allowing exhaustive nightly/regression runs.

Unified runs
- Run all E2E tests (baseline + extended + comprehensive):
```bash
pytest tests/test_solve_e2e*.py -v
```

- Run only the comprehensive accuracy run (longer):
```bash
pytest tests/test_solve_e2e_comprehensive.py -v
```

- Run a quick smoke check (fast):
```bash
pytest tests/test_solve_e2e.py -q
```

If you prefer a single entry point, see the "Next Steps" section at the end of this document which explains how to add a small wrapper `tests/test_solve_e2e_all.py` or a Makefile target to run them sequentially.


## Test Categories

### 1. Valid Problem Tests (`TestSolveEndpointValid`)

Tests basic functionality with valid inputs:

```python
# Example: Basic valid problem
{
  "user_info": {
    "name": "Іван Петренко",
    "phone": "0501234567",
    "address": "вул. Львівська, 10",
    "city": "Львів"
  },
  "problem_text": "У підіззді вже тиждень не горить лампочка на сходах"
}
```

**Tests:**
- `test_solve_valid_problem_basic` - Basic valid submission
- `test_solve_urgent_water_supply` - Urgent water supply (monopolist)
- `test_solve_heating_problem` - Heating problem classification
- `test_solve_elevator_problem` - Building-level elevator issue
- `test_solve_road_problem_district_level` - District-level road issue
- `test_solve_with_all_categories` - Coverage across all categories

### 2. Invalid Input Tests (`TestSolveEndpointInvalid`)

Validates error handling:

```python
# Too short problem text
{
  "user_info": { ... },
  "problem_text": "x"  # Min length is 5
}

# Empty problem text
{
  "user_info": { ... },
  "problem_text": ""
}

# Missing required field
{
  "problem_text": "Valid text"
  # Missing user_info
}
```

### 3. Urgency Tests (`TestSolveEndpointUrgency`)

Tests emergency detection:

```python
# Emergency keywords
- "АВАРІЙНА СИТУАЦІЯ! Нема світла 3 години"
- "Критично! Протікає вода в підвалі"
- "Терміново! Застряг у ліфті"
- "Негайно потрібна допомога! Нема опалення"
```

### 4. Service Level Tests (`TestSolveEndpointServiceLevels`)

Validates correct service resolution:

**Building-level (OSBB/ЖЕК):**
- Elevator problems
- Entrance/stairwell issues
- Roof leaks

**District Administration (РА):**
- Roads/sidewalks
- Trees/landscaping
- Yard maintenance

**City Monopolists:**
- Water supply (Львівводоканал)
- Heating (Львівтеплоенерго)
- Gas (Львівгаз)
- Lighting (Львівсвітло)

**Hotline Fallback:**
- City hotline 1580 for unclassified

### 5. Response Structure Tests (`TestSolveEndpointResponseStructure`)

Validates complete response:

```json
{
  "user_info": {
    "name": "...",
    "phone": "...",
    "address": "...",
    "city": "..."
  },
  "classification": {
    "category_id": "lighting",
    "category_name": "Освітлення",
    "is_urgent": false,
    "confidence": 0.87
  },
  "service": {
    "service_info": {
      "service_type": "КП",
      "service_name": "Львівсвітло",
      "service_phone": "+380...",
      "service_email": "...",
      "service_address": "...",
      "service_website": "..."
    },
    "reasoning": "..."
  },
  "appeal_text": "Шановний виконавче,\n..."
}
```

### 6. Dataset Tests (`TestSolveEndpointWithDatasets`)

Tests using generated fixtures:

- `test_valid_problems_from_fixtures` - Tests generated valid cases
- `test_invalid_problems_from_fixtures` - Tests generated invalid cases
- `test_urgent_problems_from_fixtures` - Tests generated urgent cases

## Running Tests

### Generate Test Datasets

```bash
# Generate datasets from full_dataset.json
python -m tests.fixtures.test_datasets_generator

# Or using the provided script
./run_e2e_tests.sh
```

This creates JSON files in `tests/fixtures/test_datasets/`:
- `valid_problems.json` - Valid test cases
- `invalid_problems.json` - Invalid test cases
- `urgent_problems.json` - Urgent cases
- `non_urgent_problems.json` - Non-urgent cases
- `service_level_*.json` - Cases grouped by service level
- `category_*.json` - Cases grouped by category
- `summary.json` - Statistics

### Run All E2E Tests

```bash
# Run all tests with verbose output
pytest tests/test_solve_e2e.py -v

# Run specific test class
pytest tests/test_solve_e2e.py::TestSolveEndpointValid -v

# Run specific test
pytest tests/test_solve_e2e.py::TestSolveEndpointValid::test_solve_valid_problem_basic -v

# Run with markers
pytest tests/test_solve_e2e.py -v -m "not slow"

# Run with coverage
pytest tests/test_solve_e2e.py --cov=app --cov-report=html
```

### Using Docker

```bash
# Build and run tests in Docker
docker-compose run web pytest tests/test_solve_e2e.py -v

# Or using Makefile
make test-e2e
```

## Test Dataset Structure

Each test dataset has this structure:

```json
{
  "input": {
    "name": "User Name",
    "phone": "0501234567",
    "address": "Street Name, Building #",
    "problem_text": "Problem description"
  },
  "expected_output": {
    "category_id": "lighting",
    "category_name": "Освітлення",
    "is_urgent": false,
    "service_level": "citywide_monopolist",
    "district": "Шевченківський район",
    "confidence_min": 0.5
  },
  "metadata": {
    "source": "full_dataset",
    "original_id": "...",
    "description": "..."
  }
}
```

## Service Levels Classification

### Building-level (ОСББ/ЖЕК)
- Elevator problems
- Entrance doors/locks
- Roof leaks
- Stairwell issues
- Building facades

**Resolution:** Direct to building management company

### District Administration (РА)
- Roads and sidewalks
- Street maintenance
- Trees and landscaping
- Yard improvements
- Public spaces

**Resolution:** District regional administration

### City Monopolists
- **Water** (Львівводоканал) - Cold/hot water
- **Heating** (Львівтеплоенерго) - Radiators, heating
- **Gas** (Львівгаз) - Gas supply
- **Lighting** (Львівсвітло) - Street/public lighting

**Resolution:** Specialized city services

### Hotline (Гаряча лінія 1580)
- Unclassified problems
- Multiple services involved
- Emergency coordination
- General complaints

**Resolution:** City hotline for triage

## Problem Categories Tested

1. **Lighting (Освітлення)** - Street and building lighting
2. **Water Supply (Водопостачання)** - Water supply issues
3. **Heating (Опалення)** - Radiators and heating
4. **Gas (Газ)** - Gas supply and safety
5. **Elevator (Ліфт)** - Building elevators
6. **Sewage (Каналізація)** - Plumbing and drainage
7. **Roads (Дороги)** - Sidewalks and street repairs
8. **Parking (Паркування)** - Parking and vehicle issues
9. **Cleaning (Прибирання)** - Maintenance and cleaning
10. **Noise (Шум)** - Noise and disturbance
11. **Other** - Miscellaneous issues

## Urgency Keywords

Problems marked as urgent if they contain:
- "аварійн" (emergency)
- "критичн" (critical)
- "термінов" (urgent)
- "негайн" (immediate)
- "без світла" (no light)
- "без води" (no water)
- "протік" (leak)
- "витік" (leakage)
- "затоплення" (flooding)
- "пожежа" (fire)
- "небезпеч" (danger)

## Example Test Case

### Input
```python
{
  "user_info": {
    "name": "Марія Іванівна",
    "phone": "0671234567",
    "address": "вул. Личаківська, 38",
    "city": "Львів"
  },
  "problem_text": "АВАРІЙНА СИТУАЦІЯ! Ліфт застряг між 5-м та 6-м поверхом, людина в пастці"
}
```

### Expected Response
```json
{
  "user_info": { ... },
  "classification": {
    "category_id": "elevator",
    "category_name": "Ліфт",
    "is_urgent": true,
    "confidence": 0.95
  },
  "service": {
    "service_info": {
      "service_type": "КП",
      "service_name": "ЛКП 'Львівсвітло-ліфт'",
      "service_phone": "+380...",
      "service_email": "...",
      "service_address": "...",
      "service_website": "..."
    },
    "reasoning": "Ліфт - будинкова послуга. Терміновий виклик аварійної служби."
  },
  "appeal_text": "Шановні представники ЛКП 'Львівсвітло-ліфт'!...\n..."
}
```

## Coverage Goals

- **All Categories:** ✅ Coverage of all problem categories
- **All Service Levels:** ✅ OSBB, РА, Monopolists, Hotline
- **All Districts:** ✅ Different Lviv districts
- **Edge Cases:** ✅ Short addresses, special characters, variations
- **Error Handling:** ✅ Invalid inputs, missing fields
- **Response Validation:** ✅ Complete structure validation
- **Data Consistency:** ✅ Appeal text generation with real service data

## Fixtures and Datasets

### Generated Fixtures
Located in `tests/fixtures/test_datasets/`:

- `valid_problems.json` (10-30 cases) - Valid for all categories
- `invalid_problems.json` (5 cases) - Common validation errors
- `urgent_problems.json` - High-confidence urgent cases
- `non_urgent_problems.json` - Regular priority cases
- `service_level_*.json` - Grouped by resolution level
- `category_*.json` - Grouped by problem category
- `summary.json` - Statistics and metadata

### Sample Statistics
```json
{
  "total_valid_cases": 24,
  "total_invalid_cases": 5,
  "total_urgent_cases": 6,
  "total_non_urgent_cases": 18,
  "categories_covered": [
    "water_supply",
    "heating",
    "elevator",
    "roads",
    ...
  ],
  "service_levels_covered": [
    "citywide_monopolist",
    "district_administration",
    "osbb_building",
    "hotline"
  ]
}
```

## Updating Test Datasets

To regenerate datasets when `full_dataset.json` changes:

```bash
# Regenerate all datasets
python -m tests.fixtures.test_datasets_generator

# Or with custom parameters
python -c "
from tests.fixtures.test_datasets_generator import TestDatasetGenerator
gen = TestDatasetGenerator('app/data/full_dataset.json', 'tests/fixtures/test_datasets')
cases = gen.generate_test_cases(samples_per_category=5)
gen.save_test_datasets(cases)
"
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run E2E Tests
  run: |
    python -m tests.fixtures.test_datasets_generator
    pytest tests/test_solve_e2e.py -v --tb=short
```

### GitLab CI

```yaml
test_e2e:
  script:
    - python -m tests.fixtures.test_datasets_generator
    - pytest tests/test_solve_e2e.py -v --tb=short
```

## Troubleshooting

### Tests fail with "fixtures not found"
```bash
# Ensure datasets are generated first
python -m tests.fixtures.test_datasets_generator
```

### Async test errors
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Or ensure conftest.py event_loop fixture is set up
```

### Database errors
```bash
# Use in-memory SQLite for tests
# Check conftest.py test_db fixture
```

## Next Steps

1. ✅ Run dataset generator: `python -m tests.fixtures.test_datasets_generator`
2. ✅ Run E2E tests: `pytest tests/test_solve_e2e.py -v`
3. ✅ Check coverage: `pytest tests/test_solve_e2e.py --cov=app`
4. ✅ Integrate with CI/CD pipeline

---

