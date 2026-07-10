#!/usr/bin/env python3
"""
pytest runner script

Provides multiple test run options and convenience commands
"""

import argparse
import subprocess
import sys
from pathlib import Path


class PytestRunner:
    """pytest runner"""

    def __init__(self):
        self.project_root = Path(__file__).parent

    def run_command(self, cmd, description=None):
        """Run a command and display the result"""
        if description:
            print(f"\n🚀 {description}")
            print("=" * 50)

        print(f"Running command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=False)
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\n⏹️  测试被用户中断")
            return False
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        cmd = ["python", "-m", "pytest"]
        return self.run_command(cmd, "Run all tests")

    def run_unit_tests(self):
        """Run unit tests"""
        cmd = ["python", "-m", "pytest", "-m", "unit"]
        return self.run_command(cmd, "Run unit tests")

    def run_integration_tests(self):
        """Run integration tests"""
        cmd = ["python", "-m", "pytest", "-m", "integration"]
        return self.run_command(cmd, "Run integration tests")

    def run_diagnostic_tests(self):
        """Run diagnostic tests"""
        cmd = ["python", "-m", "pytest", "-m", "diagnostic", "-v"]
        return self.run_command(cmd, "Run diagnostic tests")

    def run_api_tests(self):
        """Run API tests"""
        cmd = ["python", "-m", "pytest", "-m", "api", "-v"]
        return self.run_command(cmd, "Run API tests")

    def run_external_tests(self):
        """Run external service tests"""
        cmd = ["python", "-m", "pytest", "-m", "external", "-v", "-s"]
        return self.run_command(cmd, "Run external service tests（需要API密钥）")

    def run_quick_tests(self):
        """Run quick tests (skip slow and external tests)"""
        cmd = ["python", "-m", "pytest", "-m", "not slow and not external"]
        return self.run_command(cmd, "Run quick tests")

    def run_coverage_tests(self):
        """Run coverage tests"""
        cmd = ["python", "-m", "pytest", "--cov-report=html", "--cov-report=term"]
        success = self.run_command(cmd, "Run coverage tests")

        if success:
            print("\n📊 覆盖率报告已生成:")
            print("  HTML report: htmlcov/index.html")
            print("  Open command: open htmlcov/index.html")

        return success

    def run_specific_test(self, test_path):
        """Run a specific test"""
        cmd = ["python", "-m", "pytest", test_path, "-v"]
        return self.run_command(cmd, f"Run a specific test: {test_path}")

    def check_environment(self):
        """Check test environment"""
        print("🔍 Check test environment...")

        # Check whether pytest is installed
        try:
            import pytest

            print(f"✅ pytest version: {pytest.__version__}")
        except ImportError:
            print("❌ pytest is not installed")
            return False

        # Check the tests directory
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            print(f"✅ Tests directory exists: {tests_dir}")
        else:
            print(f"❌ Tests directory does not exist: {tests_dir}")
            return False

        # Check the configuration file
        pytest_ini = self.project_root / "pytest.ini"
        if pytest_ini.exists():
            print(f"✅ pytest configuration file exists: {pytest_ini}")
        else:
            print(f"⚠️  pytest configuration file does not exist: {pytest_ini}")

        # Check dependencies
        required_packages = ["pytest-asyncio", "pytest-cov"]
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package} is installed")
            except ImportError:
                print(f"❌ {package} is not installed")
                print(f"   Install command: pip install {package}")

        print("✅ Environment check complete")
        return True

    def show_test_info(self):
        """Show test information"""
        cmd = ["python", "-m", "pytest", "--collect-only", "-q"]
        self.run_command(cmd, "Collect test information")

    def run_failed_tests(self):
        """Re-run failed tests"""
        cmd = ["python", "-m", "pytest", "--lf", "-v"]
        return self.run_command(cmd, "Re-run failed tests")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="pytest test runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--diagnostic", action="store_true", help="Run diagnostic tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--external", action="store_true", help="Run external service tests")
    parser.add_argument("--quick", action="store_true", help="Run quick tests")
    parser.add_argument("--coverage", action="store_true", help="Run coverage tests")
    parser.add_argument("--failed", action="store_true", help="Re-run failed tests")
    parser.add_argument("--info", action="store_true", help="Show test information")
    parser.add_argument("--check", action="store_true", help="Check test environment")
    parser.add_argument("--test", type=str, help="Run a specific test文件或函数")

    args = parser.parse_args()

    runner = PytestRunner()

    # Show help if no options are provided
    if not any(vars(args).values()):
        print("🧪 pytest test runner")
        print("=" * 50)
        print("Use --help to view all options")
        print("\n常用命令:")
        print("  --check      Check test environment")
        print("  --diagnostic Run diagnostic tests")
        print("  --quick      Run quick tests")
        print("  --all        Run all tests")
        print("  --coverage   Run coverage tests")
        return

    success = True

    if args.check:
        success &= runner.check_environment()

    if args.info:
        runner.show_test_info()

    if args.unit:
        success &= runner.run_unit_tests()

    if args.integration:
        success &= runner.run_integration_tests()

    if args.diagnostic:
        success &= runner.run_diagnostic_tests()

    if args.api:
        success &= runner.run_api_tests()

    if args.external:
        success &= runner.run_external_tests()

    if args.quick:
        success &= runner.run_quick_tests()

    if args.coverage:
        success &= runner.run_coverage_tests()

    if args.failed:
        success &= runner.run_failed_tests()

    if args.test:
        success &= runner.run_specific_test(args.test)

    if args.all:
        success &= runner.run_all_tests()

    # Show final result
    if success:
        print("\n🎉 测试完成！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
