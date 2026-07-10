#!/usr/bin/env python3
"""
Test runner script

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py unit              # Run unit tests only
    python run_tests.py integration       # Run integration tests only
    python run_tests.py migration         # Run migration tests only
    python run_tests.py coverage          # Run tests and generate a coverage report
    python run_tests.py quick             # Quick test (skip slow tests)
    python run_tests.py parallel          # Run tests in parallel
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result"""
    if description:
        print(f"\n{'='*60}")
        print(f"🔄 {description}")
        print(f"{'='*60}")

    print(f"Running command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"Error output: {result.stderr}")

        if result.returncode != 0:
            print(f"❌ Command failed with exit code: {result.returncode}")
            return False
        else:
            print("✅ Command succeeded")
            return True

    except Exception as e:
        print(f"❌ Error while running command: {e}")
        return False


def setup_test_environment():
    """Set up test environment"""
    print("🔧 Set up test environment...")

    # Ensure we are in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Check virtual environment
    if not Path(".venv").exists():
        print("❌ Virtual environment does not exist, please create it first")
        return False

    # Install test dependencies
    if not run_command("pip install -r requirements-test.txt", "Install test dependencies"):
        return False

    # Set up test database
    setup_test_database_cmd = (
        'python -c "import importlib.util;'
        " name='app.core.test_database' if importlib.util.find_spec('app.core.test_database')"
        " else 'tests.unit.test_database';"
        " mod=__import__(name, fromlist=['setup_test_database']);"
        ' mod.setup_test_database()"'
    )
    if not run_command(setup_test_database_cmd, "Set up test database"):
        return False

    return True


def run_unit_tests():
    """Run unit tests"""
    cmd = "pytest tests/ -m unit -v"
    return run_command(cmd, "Run unit tests")


def run_integration_tests():
    """Run integration tests"""
    cmd = "pytest tests/ -m integration -v"
    return run_command(cmd, "Run integration tests")


def run_migration_tests():
    """Run migration tests"""
    cmd = "pytest tests/test_migrations.py -v"
    return run_command(cmd, "Run migration tests")


def run_api_tests():
    """Run API tests"""
    cmd = "pytest tests/test_api.py -v"
    return run_command(cmd, "Run API tests")


def run_model_tests():
    """Run model tests"""
    cmd = "pytest tests/test_models.py -v"
    return run_command(cmd, "Run model tests")


def run_e2e_tests():
    """Run end-to-end tests"""
    cmd = "pytest tests/ -m e2e -v"
    return run_command(cmd, "Run end-to-end tests")


def run_all_tests():
    """Run all tests"""
    cmd = "pytest tests/ -v"
    return run_command(cmd, "Run all tests")


def run_quick_tests():
    """Run quick tests (skip slow tests)"""
    cmd = "pytest tests/ -m 'not slow' -v"
    return run_command(cmd, "Run quick tests")


def run_parallel_tests():
    """Run tests in parallel"""
    cmd = "pytest tests/ -n auto -v"
    return run_command(cmd, "Run tests in parallel")


def run_coverage_tests():
    """Run tests and generate a coverage report"""
    cmd = "pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml"
    success = run_command(cmd, "Run tests and generate a coverage report")

    if success:
        print("\n📊 Coverage report generated:")
        print("  - HTML report: htmlcov/index.html")
        print("  - XML report: coverage.xml")
        print("  - Terminal report: shown above")

    return success


def run_specific_test(test_path):
    """Run a specific test"""
    cmd = f"pytest {test_path} -v"
    return run_command(cmd, f"Run a specific test: {test_path}")


def lint_code():
    """Code quality check"""
    print("\n🔍 Code quality check...")

    # Install linting tools
    run_command("pip install flake8 black isort", "Install code quality tools")

    # Run flake8
    if not run_command(
        "flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503",
        "Run flake8 checks",
    ):
        print("⚠️  flake8 found issues")

    # Run black checks
    if not run_command("black --check app/ tests/", "Run black formatting checks"):
        print("⚠️  black formatting issues found")
        print("💡 Run 'black app/ tests/' to format the code automatically")

    # Run isort checks
    if not run_command("isort --check-only app/ tests/", "Run isort import checks"):
        print("⚠️  isort import issues found")
        print("💡 Run 'isort app/ tests/' to sort imports automatically")


def clean_test_artifacts():
    """Clean test artifacts"""
    print("\n🧹 Clean test artifacts...")

    artifacts = [
        "htmlcov/",
        "coverage.xml",
        "test-results.xml",
        ".coverage",
        ".pytest_cache/",
        "__pycache__/",
        "*.pyc",
        "test.db",
        "test_*.db",
    ]

    for artifact in artifacts:
        if "*" in artifact:
            run_command(f"find . -name '{artifact}' -delete", f"Delete {artifact}")
        else:
            run_command(f"rm -rf {artifact}", f"Delete {artifact}")

    print("✅ Test artifact cleanup complete")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test runner script")
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=[
            "all",
            "unit",
            "integration",
            "migration",
            "api",
            "model",
            "e2e",
            "coverage",
            "quick",
            "parallel",
            "lint",
            "clean",
            "setup",
        ],
        help="Test type to run",
    )
    parser.add_argument("--test", "-t", help="Run a specific test file or function")
    parser.add_argument("--no-setup", action="store_true", help="Skip environment setup")

    args = parser.parse_args()

    # Set up test environment
    if not args.no_setup and args.command != "clean":
        if not setup_test_environment():
            print("❌ Test environment setup failed")
            sys.exit(1)

    # Execute the corresponding command
    success = True

    if args.test:
        success = run_specific_test(args.test)
    elif args.command == "all":
        success = run_all_tests()
    elif args.command == "unit":
        success = run_unit_tests()
    elif args.command == "integration":
        success = run_integration_tests()
    elif args.command == "migration":
        success = run_migration_tests()
    elif args.command == "api":
        success = run_api_tests()
    elif args.command == "model":
        success = run_model_tests()
    elif args.command == "e2e":
        success = run_e2e_tests()
    elif args.command == "coverage":
        success = run_coverage_tests()
    elif args.command == "quick":
        success = run_quick_tests()
    elif args.command == "parallel":
        success = run_parallel_tests()
    elif args.command == "lint":
        lint_code()
    elif args.command == "clean":
        clean_test_artifacts()
    elif args.command == "setup":
        success = setup_test_environment()

    if success:
        print("\n🎉 Tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test execution failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
