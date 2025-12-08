#!/usr/bin/env python
"""
Test docking with the CORRECT grid center (MK1 binding site)
"""
import sys
import json
from vina_docking import run_vina_docking

if __name__ == "__main__":
    # Protein and ligand IDs (from MongoDB)
    protein_id = "69314937b9807eeaf95f45d4"  # 1HSG
    ligand_id = "69314edfdcd6dab364652a38"   # Ritonavir (corrected SMILES)
    
    # CORRECT grid parameters from MK1 co-crystallized ligand
    config = {
        "protein_id": protein_id,
        "ligand_id": ligand_id,
        "grid_center": {"x": 13.1, "y": 22.5, "z": 5.6},  # MK1 binding site center
        "grid_size": {"x": 25, "y": 20, "z": 19},         # Sufficient to cover binding site
        "exhaustivity": 8,
        "num_poses": 9
    }
    
    print("=" * 80, file=sys.stderr)
    print("TESTING WITH CORRECT GRID CENTER", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Grid Center: ({config['grid_center']['x']}, {config['grid_center']['y']}, {config['grid_center']['z']})", file=sys.stderr)
    print(f"Grid Size: ({config['grid_size']['x']}, {config['grid_size']['y']}, {config['grid_size']['z']})", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Run docking
    result = run_vina_docking(config)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    if result.get("status") == "completed":
        poses = result.get("poses", [])
        if poses:
            best_affinity = poses[0].get("affinity")
            print(f"\n✅ BEST AFFINITY: {best_affinity} kcal/mol", file=sys.stderr)
            print(f"Expected range: -9 to -11 kcal/mol", file=sys.stderr)
            
            if best_affinity and float(best_affinity) < -7:
                print("🎉 SUCCESS! Realistic binding affinity achieved!", file=sys.stderr)
            else:
                print("⚠️  Still low, but closer to realistic values", file=sys.stderr)
