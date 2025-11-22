#!/usr/bin/env python
"""
Verify test environment setup and dependencies.

Usage:
    python tests/verify_setup.py
    
Checks:
- Python version
- Required packages
- Test file structure
- Full dataset availability
"""

import sys
from pathlib import Path
import importlib.util


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 12)
    
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version[:2] < required:
        print(f"  ⚠️  Warning: Python {required[0]}.{required[1]}+ recommended")
        return False
    
    return True


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    import_name = import_name or package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print(f"❌ {package_name}: NOT installed")
            return False
        
        print(f"✓ {package_name}: installed")
        return True
    except Exception as e:
        print(f"❌ {package_name}: Error - {e}")
        return False


def check_file_structure():
    """Check if test files exist"""
    project_root = Path(__file__).parent.parent
    
    required_files = [
        "tests/conftest.py",
        "tests/test_solve_e2e.py",
        "tests/fixtures/test_datasets_generator.py",
        "tests/E2E_TESTS_README.md",
    ]
    
    print("\n📁 File Structure:")
    all_exist = True
    
    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✓" if exists else "❌"
        print(f"{status} {file_path}")
        all_exist = all_exist and exists
    
    return all_exist


def check_datasets():
    """Check if datasets directory exists and has content"""
    project_root = Path(__file__).parent.parent
    datasets_dir = project_root / "tests" / "fixtures" / "test_datasets"
    
    print("\n📊 Test Datasets:")
    
    if datasets_dir.exists():
        json_files = list(datasets_dir.glob("*.json"))
        if json_files:
            print(f"✓ Datasets directory exists with {len(json_files)} files:")
            for f in sorted(json_files):
                size = f.stat().st_size / 1024
                print(f"  - {f.name} ({size:.1f} KB)")
            return True
        else:
            print("⚠️  Datasets directory exists but is empty")
            print("   Run: python -m tests.fixtures.test_datasets_generator")
            return False
    else:
        print("⚠️  Datasets directory not found")
        print("   Run: python -m tests.fixtures.test_datasets_generator")
        return False


def check_full_dataset():
    """Check if full_dataset.json exists"""
    project_root = Path(__file__).parent.parent
    dataset_path = project_root / "app" / "data" / "full_dataset.json"
    
    print("\n📄 Full Dataset:")
    
    if dataset_path.exists():
        size = dataset_path.stat().st_size / (1024 * 1024)
        print(f"✓ full_dataset.json exists ({size:.1f} MB)")
        return True
    else:
        print("❌ full_dataset.json not found")
        return False


def main():
    """Main verification"""
    print("="*70)
    print("E2E Test Environment Verification")
    print("="*70 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Pytest", lambda: check_package("pytest")),
        ("Pytest-asyncio", lambda: check_package("pytest-asyncio", "pytest_asyncio")),
        ("HTTPX", lambda: check_package("httpx")),
        ("SQLModel", lambda: check_package("sqlmodel")),
        ("Pydantic", lambda: check_package("pydantic")),
        ("FastAPI", lambda: check_package("fastapi")),
    ]
    
    print("📦 Required Packages:")
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
        except Exception as e:
            print(f"❌ {check_name}: Error - {e}")
            results[check_name] = False
    
    # Check file structure
    print()
    file_structure_ok = check_file_structure()
    
    # Check datasets
    datasets_ok = check_datasets()
    
    # Check full_dataset
    print()
    full_dataset_ok = check_full_dataset()
    
    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    
    all_packages_ok = all(results.values())
    
    if all_packages_ok and file_structure_ok and full_dataset_ok:
        print("✅ All checks passed! Ready to run tests.")
        print("\nNext steps:")
        if not datasets_ok:
            print("  1. Generate datasets: python -m tests.fixtures.test_datasets_generator")
            print("  2. Run tests: make test-e2e")
        else:
            print("  1. Run tests: make test-e2e")
        
        return 0
    else:
        print("❌ Some checks failed. See details above.")
        
        if not all_packages_ok:
            print("\n📦 Install missing packages:")
            print("  pip install pytest pytest-asyncio httpx")
        
        if not file_structure_ok:
            print("\n📁 Missing test files")
            print("  Regenerate tests from template")
        
        if not full_dataset_ok:
            print("\n📄 Missing full_dataset.json")
            print("  Ensure the file exists in app/data/")
        
        if not datasets_ok:
            print("\n📊 Generate test datasets:")
            print("  python -m tests.fixtures.test_datasets_generator")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
