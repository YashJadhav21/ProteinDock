"""
Quick Docking Test - Ritonavir + 1HSG with MGLTools

Tests the complete pipeline with:
- Ritonavir (FDA-approved HIV protease inhibitor)
- 1HSG HIV-1 Protease
- MGLTools prepare_receptor4.py for receptor preparation
- Correct grid parameters for binding site
"""

import sys
import os
import json

# Simple test without complex argument parsing
if __name__ == "__main__":
    print("=" * 70)
    print("QUICK DOCKING TEST - Ritonavir + 1HSG")
    print("=" * 70)
    
    # Test configuration
    test_data = {
        "protein": {
            "_id": "69313695196d1cda93abd42d",
            "pdbId": "1HSG",
            "structure": ""  # Will be loaded from database
        },
        "ligand": {
            "_id": "69319c11e920b87470027cac",
            "name": "Ritonavir",
            "smiles": "CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C"
        },
        "config": {
            "gridCenter": {"x": 13.1, "y": 22.5, "z": 5.6},
            "gridSize": {"x": 25, "y": 20, "z": 19},
            "exhaustivity": 2,  # Low for quick test
            "numPoses": 3
        },
        "outputDir": "./quick_test_output"
    }
    
    print(f"\nTest Parameters:")
    print(f"  Protein: {test_data['protein']['pdbId']}")
    print(f"  Ligand: {test_data['ligand']['name']}")
    print(f"  Grid Center: ({test_data['config']['gridCenter']['x']}, {test_data['config']['gridCenter']['y']}, {test_data['config']['gridCenter']['z']})")
    print(f"  Grid Size: {test_data['config']['gridSize']['x']} x {test_data['config']['gridSize']['y']} x {test_data['config']['gridSize']['z']} Å")
    print(f"  Exhaustiveness: {test_data['config']['exhaustivity']} (quick test)")
    print(f"  Output: {test_data['config']['exhaustivity']}")
    print("=" * 70)
    
    # Create output directory
    os.makedirs(test_data['outputDir'], exist_ok=True)
    
    # Write input as JSON to stdin
    import subprocess
    
    cmd = [
        sys.executable,
        "vina_docking.py",
        "--protein-id", test_data['protein']['_id'],
        "--ligand-id", test_data['ligand']['_id'],
        "--center", str(test_data['config']['gridCenter']['x']), 
                   str(test_data['config']['gridCenter']['y']), 
                   str(test_data['config']['gridCenter']['z']),
        "--size", str(test_data['config']['gridSize']['x']), 
                 str(test_data['config']['gridSize']['y']), 
                 str(test_data['config']['gridSize']['z']),
        "--exhaustiveness", str(test_data['config']['exhaustivity']),
        "--output-dir", test_data['outputDir']
    ]
    
    print(f"\nRunning command:")
    print(f"  {' '.join(cmd)}")
    print("\n" + "=" * 70)
    print("DOCKING IN PROGRESS...")
    print("=" * 70 + "\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=600  # 10 minute timeout for quick test
        )
        
        print("\n" + "=" * 70)
        if result.returncode == 0:
            print("✅ DOCKING COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            
            # Try to read results
            result_file = os.path.join(test_data['outputDir'], 'result.json')
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    results = json.load(f)
                    
                print(f"\nResults Summary:")
                print(f"  Status: {results.get('status', 'unknown')}")
                
                if 'poses' in results and results['poses']:
                    print(f"  Number of poses: {len(results['poses'])}")
                    print(f"\n  Best Pose:")
                    best = results['poses'][0]
                    print(f"    Binding Affinity: {best.get('score', 'N/A')} kcal/mol")
                    print(f"    RMSD (lb): {best.get('rmsd_lb', 'N/A')} Å")
                    print(f"    RMSD (ub): {best.get('rmsd_ub', 'N/A')} Å")
                    
                    if len(results['poses']) > 1:
                        print(f"\n  All Poses:")
                        for i, pose in enumerate(results['poses'], 1):
                            print(f"    {i}. Affinity: {pose.get('score', 'N/A')} kcal/mol")
                    
                    # Check if result is realistic
                    best_affinity = best.get('score', 0)
                    print(f"\n  ⚠️  Expected affinity for Ritonavir: -9 to -11 kcal/mol")
                    print(f"  📊 Actual affinity: {best_affinity} kcal/mol")
                    
                    if -11 <= best_affinity <= -9:
                        print(f"  ✅ EXCELLENT! Result matches expected range!")
                    elif -12 <= best_affinity <= -8:
                        print(f"  ✓  GOOD! Result is close to expected range")
                    else:
                        print(f"  ⚠️  Result differs from expected - may need investigation")
                
                print(f"\n  Output files in: {test_data['outputDir']}")
            else:
                print(f"  ⚠️  Result file not found: {result_file}")
        else:
            print("❌ DOCKING FAILED!")
            print(f"Exit code: {result.returncode}")
            print("=" * 70)
            
    except subprocess.TimeoutExpired:
        print("\n" + "=" * 70)
        print("❌ DOCKING TIMED OUT (10 minutes)")
        print("=" * 70)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
