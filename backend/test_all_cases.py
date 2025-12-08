#!/usr/bin/env python3
"""
Comprehensive Test Script for ProteinDock
Tests all molecular docking cases and validates results against expected values
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Test cases with expected values
TEST_CASES = [
    {
        "id": "TC1",
        "name": "HIV Protease + Ritonavir",
        "protein_pdb": "1HSG",
        "ligand_name": "Ritonavir",
        "smiles": "CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -11.0,
        "expected_affinity_max": -9.0,
        "expected_time_max": 60,
        "auto_grid": True
    },
    {
        "id": "TC2",
        "name": "HIV Protease + Indinavir",
        "protein_pdb": "1HSG",
        "ligand_name": "Indinavir",
        "smiles": "CC(C)(C)NC(=O)[C@@H]1CN(CCN1Cc2cccnc2)C[C@H](C[C@H](Cc3ccccc3)C(=O)N[C@H]4c5ccccc5C[C@H]4O)O",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -12.0,
        "expected_affinity_max": -10.0,
        "expected_time_max": 40,
        "auto_grid": True
    },
    {
        "id": "TC3",
        "name": "Estrogen Receptor + Tamoxifen",
        "protein_pdb": "3ERT",
        "ligand_name": "Tamoxifen",
        "smiles": "CCC(=C(c1ccccc1)c2ccc(cc2)OCCN(C)C)c3ccccc3",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -10.0,
        "expected_affinity_max": -8.0,
        "expected_time_max": 20,
        "auto_grid": True
    },
    {
        "id": "TC4",
        "name": "Thrombin + Dabigatran",
        "protein_pdb": "2ZFF",
        "ligand_name": "Dabigatran",
        "smiles": "CCC(=O)N(c1ccc(cc1N)C(=O)N2CCN(CC2)c3nc4ccccc4n3C)c5ccc(cc5)C(=O)O",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -9.0,
        "expected_affinity_max": -7.0,
        "expected_time_max": 50,
        "auto_grid": True
    },
    {
        "id": "TC5",
        "name": "Acetylcholinesterase + Donepezil",
        "protein_pdb": "1EVE",
        "ligand_name": "Donepezil",
        "smiles": "COc1cc2c(cc1OC)CC(C2)CC(=O)Nc3c4ccccc4ccc3",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -11.0,
        "expected_affinity_max": -9.0,
        "expected_time_max": 25,
        "auto_grid": True
    },
    {
        "id": "TC6",
        "name": "COVID-19 Mpro + Nirmatrelvir",
        "protein_pdb": "7VH8",
        "ligand_name": "Nirmatrelvir",
        "smiles": "CC(C)(C)NC(=O)[C@H](C(C)(C)C)NC(=O)[C@H](F)c1cc2c(cc1F)C[C@@H]2C(=O)NC(C#N)C[C@H]3CCNC3=O",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -6.0,  # Covalent inhibitor - Vina only calculates non-covalent component
        "expected_affinity_max": -5.0,
        "expected_time_max": 90,
        "auto_grid": True,
        "note": "Covalent inhibitor - Vina only models non-covalent binding"
    },
    {
        "id": "TC7",
        "name": "ABL1 Kinase + Imatinib",
        "protein_pdb": "2HYY",
        "ligand_name": "Imatinib",
        "smiles": "CN1CCN(CC1)Cc2ccc(cc2)C(=O)Nc3ccc(c(c3)Nc4nccc(n4)c5cccnc5)C",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -10.0,
        "expected_affinity_max": -8.0,
        "expected_time_max": 45,
        "auto_grid": True
    },
    {
        "id": "TC8",
        "name": "COX-2 + Aspirin",
        "protein_pdb": "5KIR",
        "ligand_name": "Aspirin",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "exhaustivity": 2,
        "num_poses": 1,
        "expected_affinity_min": -7.0,
        "expected_affinity_max": -5.0,
        "expected_time_max": 15,
        "auto_grid": True,
        "note": "Weak binder as expected"
    }
]

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestLogger:
    """Logger for test results"""
    
    def __init__(self, log_file="test_results.log"):
        self.log_file = log_file
        self.start_time = datetime.now()
        self.results = []
        
        # Initialize log file
        with open(self.log_file, 'w') as f:
            f.write(f"ProteinDock Test Suite - Started at {self.start_time}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, message, level="INFO"):
        """Log message to both console and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Console output with colors
        if level == "ERROR":
            print(f"{Colors.FAIL}{log_message}{Colors.ENDC}")
        elif level == "SUCCESS":
            print(f"{Colors.OKGREEN}{log_message}{Colors.ENDC}")
        elif level == "WARNING":
            print(f"{Colors.WARNING}{log_message}{Colors.ENDC}")
        elif level == "INFO":
            print(f"{Colors.OKCYAN}{log_message}{Colors.ENDC}")
        else:
            print(log_message)
        
        # File output
        with open(self.log_file, 'a') as f:
            f.write(log_message + "\n")
    
    def log_test_result(self, test_case, result):
        """Log test case result"""
        self.results.append({
            "test_case": test_case,
            "result": result,
            "timestamp": datetime.now()
        })
        
        with open(self.log_file, 'a') as f:
            f.write("\n" + "-" * 80 + "\n")
            f.write(f"Test Case: {test_case['id']} - {test_case['name']}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Duration: {result.get('duration', 'N/A')} seconds\n")
            
            if result['status'] == 'PASSED':
                f.write(f"Actual Affinity: {result['affinity']:.2f} kcal/mol\n")
                f.write(f"Expected Range: {test_case['expected_affinity_min']:.1f} to {test_case['expected_affinity_max']:.1f} kcal/mol\n")
                f.write(f"Validation: {'✓ PASS' if result['affinity_in_range'] else '✗ FAIL - Out of range'}\n")
            elif result['status'] == 'FAILED':
                f.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
            f.write("-" * 80 + "\n\n")
    
    def generate_summary(self):
        """Generate test summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed = sum(1 for r in self.results if r['result']['status'] == 'PASSED' and r['result'].get('affinity_in_range', False))
        failed = sum(1 for r in self.results if r['result']['status'] == 'FAILED')
        out_of_range = sum(1 for r in self.results if r['result']['status'] == 'PASSED' and not r['result'].get('affinity_in_range', False))
        total = len(self.results)
        
        summary = f"""
{'=' * 80}
TEST SUMMARY
{'=' * 80}
Total Tests: {total}
Passed (In Range): {passed}
Passed (Out of Range): {out_of_range}
Failed: {failed}
Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%

Total Duration: {duration:.1f} seconds
Average Time per Test: {(duration/total) if total > 0 else 0:.1f} seconds
{'=' * 80}
"""
        
        print(f"{Colors.BOLD}{summary}{Colors.ENDC}")
        
        with open(self.log_file, 'a') as f:
            f.write(summary)
        
        # Detailed results
        print(f"\n{Colors.HEADER}{Colors.BOLD}DETAILED RESULTS:{Colors.ENDC}")
        for r in self.results:
            tc = r['test_case']
            res = r['result']
            
            if res['status'] == 'PASSED':
                status_icon = "✓" if res.get('affinity_in_range', False) else "⚠"
                status_color = Colors.OKGREEN if res.get('affinity_in_range', False) else Colors.WARNING
                affinity_str = f"{res['affinity']:.2f} kcal/mol"
                expected_str = f"[{tc['expected_affinity_min']:.1f} to {tc['expected_affinity_max']:.1f}]"
                print(f"{status_color}{status_icon} {tc['id']}: {tc['name']}{Colors.ENDC}")
                print(f"   Affinity: {affinity_str} {expected_str} | Time: {res['duration']:.1f}s")
            else:
                print(f"{Colors.FAIL}✗ {tc['id']}: {tc['name']}{Colors.ENDC}")
                print(f"   Error: {res.get('error', 'Unknown')}")
            
            if 'note' in tc:
                print(f"   Note: {tc['note']}")
            print()

def run_docking_test(test_case, logger):
    """Run a single docking test case"""
    logger.log(f"Starting test: {test_case['id']} - {test_case['name']}")
    
    start_time = time.time()
    result = {
        'status': 'FAILED',
        'duration': 0,
        'error': None
    }
    
    try:
        # Prepare command
        cmd = [
            sys.executable,
            'vina_docking.py',
            '--smiles', test_case['smiles'],
            '--receptor_pdb', test_case['protein_pdb'],
            '--exhaustiveness', str(test_case['exhaustivity']),
            '--num_poses', str(test_case['num_poses'])
        ]
        
        logger.log(f"Running: {' '.join(cmd)}", "INFO")
        
        # Run docking
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
        
        duration = time.time() - start_time
        result['duration'] = duration
        
        if process.returncode != 0:
            result['error'] = f"Process failed with code {process.returncode}: {stderr}"
            logger.log(f"Test failed: {result['error']}", "ERROR")
            return result
        
        # Parse output for affinity
        affinity = None
        for line in stdout.split('\n'):
            if 'Best affinity' in line or 'Affinity:' in line:
                # Extract number like "-9.5 kcal/mol"
                parts = line.split()
                for i, part in enumerate(parts):
                    try:
                        affinity = float(part)
                        break
                    except ValueError:
                        continue
                if affinity is not None:
                    break
        
        if affinity is None:
            # Try JSON output format
            try:
                output_data = json.loads(stdout)
                if 'poses' in output_data and len(output_data['poses']) > 0:
                    affinity = output_data['poses'][0]['affinity']
            except:
                pass
        
        if affinity is None:
            result['error'] = "Could not parse affinity from output"
            logger.log(f"Failed to parse affinity. Output: {stdout[:500]}", "ERROR")
            return result
        
        # Validate affinity range
        affinity_in_range = (test_case['expected_affinity_min'] <= affinity <= test_case['expected_affinity_max'])
        
        result['status'] = 'PASSED'
        result['affinity'] = affinity
        result['affinity_in_range'] = affinity_in_range
        
        # Log time validation
        if duration > test_case['expected_time_max']:
            logger.log(f"Warning: Test took {duration:.1f}s (expected max {test_case['expected_time_max']}s)", "WARNING")
        
        if affinity_in_range:
            logger.log(f"Test PASSED: Affinity {affinity:.2f} kcal/mol in expected range [{test_case['expected_affinity_min']}, {test_case['expected_affinity_max']}]", "SUCCESS")
        else:
            logger.log(f"Test PASSED but affinity OUT OF RANGE: {affinity:.2f} kcal/mol (expected [{test_case['expected_affinity_min']}, {test_case['expected_affinity_max']}])", "WARNING")
        
    except subprocess.TimeoutExpired:
        result['error'] = "Test timed out after 5 minutes"
        logger.log(result['error'], "ERROR")
    except Exception as e:
        result['error'] = str(e)
        logger.log(f"Test error: {e}", "ERROR")
    
    return result

def main():
    """Main test runner"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  ProteinDock Comprehensive Test Suite")
    print("=" * 80)
    print(f"{Colors.ENDC}\n")
    
    logger = TestLogger("test_results.log")
    
    # Check if we're in the right directory
    if not os.path.exists('vina_docking.py'):
        logger.log("Error: vina_docking.py not found. Please run from backend directory.", "ERROR")
        sys.exit(1)
    
    logger.log(f"Found {len(TEST_CASES)} test cases to run")
    
    # Run tests
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(TEST_CASES)}] Running: {test_case['name']}{Colors.ENDC}")
        
        result = run_docking_test(test_case, logger)
        logger.log_test_result(test_case, result)
        
        # Brief pause between tests
        if i < len(TEST_CASES):
            time.sleep(2)
    
    # Generate summary
    logger.generate_summary()
    
    logger.log("Test suite complete!", "SUCCESS")
    logger.log(f"Full results saved to: {os.path.abspath(logger.log_file)}")

if __name__ == "__main__":
    main()
