"""
Full Docking Test with MGLTools prepare_receptor4.py

Tests the complete Ritonavir + 1HSG docking pipeline with:
- Corrected Ritonavir SMILES (106 chars)
- Proper ligand preparation (RDKit + Meeko)
- GOLD STANDARD receptor preparation (MGLTools prepare_receptor4.py)
- Correct grid center (13.1, 22.5, 5.6) from MK1 binding site
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from vina_docking import main

if __name__ == "__main__":
    # Test parameters for Ritonavir + 1HSG
    test_args = [
        "vina_docking.py",
        "--protein-id", "69313695196d1cda93abd42d",  # 1HSG
        "--ligand-id", "69314edfdcd6dab364652a38",    # Ritonavir (corrected SMILES)
        "--center", "13.1", "22.5", "5.6",             # Correct binding site
        "--size", "25", "20", "19",                    # Large enough for Ritonavir
        "--exhaustiveness", "4",                       # Good search
        "--output-dir", "./test_mgltools_docking"
    ]
    
    print("=" * 70)
    print("Testing Full Docking Pipeline with MGLTools prepare_receptor4.py")
    print("=" * 70)
    print(f"\nLigand: Ritonavir (MW ~721 g/mol, 118 atoms with H)")
    print(f"Receptor: 1HSG HIV-1 Protease")
    print(f"Grid Center: (13.1, 22.5, 5.6) - MK1 binding site")
    print(f"Grid Size: 25 x 20 x 19 Å")
    print(f"Exhaustiveness: 8")
    print(f"\nExpected Binding Affinity: -9 to -11 kcal/mol")
    print("=" * 70)
    
    sys.argv = test_args
    main()
