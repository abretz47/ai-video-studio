#!/usr/bin/env python3
"""
AIimage generate Zi Dong Hua test Jiao Ben

Du Li run test Jiao Ben，Wu Xu Qi DongFastAPIserver
"""

import asyncio
import json
import sys
from pathlib import Path

# Tian Jia project Gen Mu Lu toPythonpath
sys.path.append(str(Path(__file__).parent))

from app.services.diagnostic_service import DiagnosticService


async def main():
    """main test function"""
    print("🚀 AIimage generate Zi Dong Hua test Jiao Ben")
    print("=" * 50)

    diagnostic = DiagnosticService()

    # run complete Zhen Duan
    print("\n📋 run complete Zhen Duan test...")
    result = await diagnostic.run_full_diagnostic()

    # output Jie Guo
    print("\n" + "=" * 50)
    print("📊 Zhen Duan Jie Guo Zong Jie")
    print("=" * 50)

    summary = result["summary"]
    print(
        f"Zong Ti status: {'✅ PASS' if summary['overall_status'] == 'PASS' else '❌ FAIL'}"
    )
    print(f"test Zong Shu: {summary['total_tests']}")
    print(f"pass test: {summary['passed_tests']}")
    print(f"failed test: {summary['failed_tests']}")
    print(f"Cheng Gong Lv: {summary['success_rate']}")

    # display Xiang Xi Jie Guo
    print("\n📝 Xiang Xi test Jie Guo:")
    for test_name, test_result in result["test_results"].items():
        status = "✅" if test_result["success"] else "❌"
        print(f"{status} {test_name}")
        if test_result["details"]:
            # Suo Jin display Xiang Xi Xin Xi
            for line in test_result["details"].split("\n"):
                if line.strip():
                    print(f"    {line.strip()}")
        if test_result["error"]:
            print(f"    error: {test_result['error']}")

    # display error list
    if result["errors"]:
        print("\n❌ discover issue:")
        for error in result["errors"]:
            print(f"  • {error}")

    # display Jian Yi
    if result["recommendations"]:
        print("\n🔧 repair Jian Yi:")
        for rec in result["recommendations"]:
            print(f"  {rec}")

    # Bao Cun complete Bao Gao to file
    report_file = "diagnostic_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 complete Bao Gao already Bao Cun to: {report_file}")

    # Ru Guo have error，Tui Chu Ma Wei1
    if result["errors"]:
        print(f"\n❌ test complete，discover {len(result['errors'])} Ge issue")
        sys.exit(1)
    else:
        print("\n🎉 test complete，Suo You function normal！")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  test be user Zhong Duan")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 test Jiao Ben exception: {e}")
        sys.exit(1)
