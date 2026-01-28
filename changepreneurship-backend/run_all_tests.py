#!/usr/bin/env python3
"""
Comprehensive Test Runner
Executes all test suites and generates detailed reports
"""
import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime


class TestRunner:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {
                'total_passed': 0,
                'total_failed': 0,
                'total_skipped': 0,
                'total_duration': 0
            }
        }
        self.reports_dir = Path(__file__).parent.parent / 'test-reports'
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_test_suite(self, name, test_file, markers=None):
        """Run a specific test suite"""
        print(f"\n{'='*70}")
        print(f"🧪 Running {name}")
        print(f"{'='*70}\n")
        
        cmd = [
            sys.executable, '-m', 'pytest',
            test_file,
            '-v',
            '--tb=short',
            '--color=yes',
            f'--junitxml={self.reports_dir}/{name}-results.xml',
            '--json-report',
            f'--json-report-file={self.reports_dir}/{name}-report.json'
        ]
        
        if markers:
            cmd.extend(['-m', markers])
            
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        # Parse results
        passed = result.stdout.count(' PASSED')
        failed = result.stdout.count(' FAILED')
        skipped = result.stdout.count(' SKIPPED')
        
        self.results['test_suites'][name] = {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': duration,
            'exit_code': result.returncode
        }
        
        self.results['summary']['total_passed'] += passed
        self.results['summary']['total_failed'] += failed
        self.results['summary']['total_skipped'] += skipped
        self.results['summary']['total_duration'] += duration
        
        # Print summary for this suite
        status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
        print(f"\n{status} - {name}")
        print(f"   Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        print(f"   Duration: {duration:.2f}s")
        
        return result.returncode == 0
        
    def run_all_tests(self):
        """Run all test suites in order"""
        print("\n" + "="*70)
        print("🚀 CHANGEPRENEURSHIP - COMPREHENSIVE TEST EXECUTION")
        print("="*70)
        print(f"Started at: {self.results['timestamp']}")
        
        test_suites = [
            {
                'name': 'Smoke Tests',
                'file': 'tests/test_smoke.py',
                'description': 'Critical path verification'
            },
            {
                'name': 'Unit Tests - Authentication',
                'file': 'tests/test_auth.py',
                'description': 'Auth service tests'
            },
            {
                'name': 'Unit Tests - Assessment',
                'file': 'tests/test_assessment.py',
                'description': 'Assessment model tests'
            },
            {
                'name': 'API Tests',
                'file': 'tests/test_comprehensive_api.py',
                'description': 'All API endpoints'
            },
            {
                'name': 'E2E Tests',
                'file': 'tests/test_e2e.py',
                'description': 'Complete user journeys'
            }
        ]
        
        all_passed = True
        for suite in test_suites:
            try:
                passed = self.run_test_suite(suite['name'], suite['file'])
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ Error running {suite['name']}: {e}")
                all_passed = False
                
        return all_passed
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*70)
        
        summary = self.results['summary']
        total_tests = summary['total_passed'] + summary['total_failed'] + summary['total_skipped']
        pass_rate = (summary['total_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"  ✅ Passed:  {summary['total_passed']}")
        print(f"  ❌ Failed:  {summary['total_failed']}")
        print(f"  ⏭️  Skipped: {summary['total_skipped']}")
        print(f"\nPass Rate: {pass_rate:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        
        print("\n" + "-"*70)
        print("Test Suites Breakdown:")
        print("-"*70)
        
        for name, results in self.results['test_suites'].items():
            status = "✅" if results['exit_code'] == 0 else "❌"
            print(f"{status} {name:30} P:{results['passed']:3} F:{results['failed']:3} S:{results['skipped']:3} ({results['duration']:.2f}s)")
            
        # Save JSON report
        report_file = self.reports_dir / 'test-summary.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Generate markdown report
        self.generate_markdown_report()
        
        return summary['total_failed'] == 0
        
    def generate_markdown_report(self):
        """Generate markdown test report"""
        md_content = f"""# Test Execution Report

**Generated:** {self.results['timestamp']}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {self.results['summary']['total_passed'] + self.results['summary']['total_failed'] + self.results['summary']['total_skipped']} |
| ✅ Passed | {self.results['summary']['total_passed']} |
| ❌ Failed | {self.results['summary']['total_failed']} |
| ⏭️ Skipped | {self.results['summary']['total_skipped']} |
| Pass Rate | {(self.results['summary']['total_passed'] / (self.results['summary']['total_passed'] + self.results['summary']['total_failed']) * 100) if (self.results['summary']['total_passed'] + self.results['summary']['total_failed']) > 0 else 0:.1f}% |
| Duration | {self.results['summary']['total_duration']:.2f}s |

## Test Suites

| Suite | Status | Passed | Failed | Skipped | Duration |
|-------|--------|--------|--------|---------|----------|
"""
        
        for name, results in self.results['test_suites'].items():
            status = "✅ PASSED" if results['exit_code'] == 0 else "❌ FAILED"
            md_content += f"| {name} | {status} | {results['passed']} | {results['failed']} | {results['skipped']} | {results['duration']:.2f}s |\n"
            
        md_content += f"""
## Coverage

Run `pytest --cov=src --cov-report=html` to generate coverage report.

## Next Steps

"""
        
        if self.results['summary']['total_failed'] > 0:
            md_content += "- ❌ Fix failing tests before deployment\n"
            md_content += "- Review test failure details in individual suite reports\n"
        else:
            md_content += "- ✅ All tests passed - ready for deployment\n"
            
        md_file = self.reports_dir / 'TEST_REPORT.md'
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"📄 Markdown report saved to: {md_file}")


def main():
    """Main test execution"""
    runner = TestRunner()
    
    try:
        all_passed = runner.run_all_tests()
        report_passed = runner.generate_report()
        
        print("\n" + "="*70)
        if all_passed and report_passed:
            print("✅ ALL TESTS PASSED - SYSTEM READY")
            print("="*70 + "\n")
            return 0
        else:
            print("❌ SOME TESTS FAILED - REVIEW REQUIRED")
            print("="*70 + "\n")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
