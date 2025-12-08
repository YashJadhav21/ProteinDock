#!/usr/bin/env python
"""
Verification script to test all docking components
Run this before testing with real docking
"""

import sys
import json

def check_dependencies():
    """Check all required Python packages"""
    required = {
        'rdkit': 'RDKit',
        'meeko': 'Meeko',
        'Bio': 'BioPython',
        'numpy': 'NumPy'
    }
    
    print("=" * 60)
    print("CHECKING PYTHON DEPENDENCIES")
    print("=" * 60)
    
    all_ok = True
    for module, name in required.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {name:15s} - Version {version}")
        except ImportError:
            print(f"❌ {name:15s} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_vina_binary():
    """Check if Vina binary exists and works"""
    from pathlib import Path
    import subprocess
    
    print("\n" + "=" * 60)
    print("CHECKING AUTODOCK VINA BINARY")
    print("=" * 60)
    
    vina_path = Path(__file__).parent / 'vina_bin' / 'vina.exe'
    
    if not vina_path.exists():
        print(f"❌ Vina binary not found at: {vina_path}")
        return False
    
    print(f"✅ Vina binary found: {vina_path}")
    
    try:
        result = subprocess.run(
            [str(vina_path), '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout + result.stderr
        if 'AutoDock Vina' in output:
            # Extract version
            for line in output.split('\n'):
                if 'AutoDock Vina' in line:
                    print(f"✅ {line.strip()}")
                    return True
        else:
            print("❌ Vina binary exists but version check failed")
            return False
    except Exception as e:
        print(f"❌ Error running Vina: {e}")
        return False

def test_ligand_preparation():
    """Test SMILES to PDBQT conversion"""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    
    print("\n" + "=" * 60)
    print("TESTING LIGAND PREPARATION")
    print("=" * 60)
    
    # Test with aspirin (simple molecule)
    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"
    print(f"Test SMILES: {test_smiles} (Aspirin)")
    
    try:
        mol = Chem.MolFromSmiles(test_smiles)
        if mol is None:
            print("❌ Failed to parse SMILES")
            return False
        
        mol = Chem.AddHs(mol)
        print(f"✅ Molecule created: {mol.GetNumAtoms()} atoms (with H)")
        
        # Test 3D generation
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        result = AllChem.EmbedMolecule(mol, params)
        
        if result == -1:
            print("❌ 3D embedding failed")
            return False
        
        print("✅ 3D coordinates generated")
        
        # Test MMFF optimization
        if AllChem.MMFFHasAllMoleculeParams(mol):
            mmff_props = AllChem.MMFFGetMoleculeProperties(mol)
            ff = AllChem.MMFFGetMoleculeForceField(mol, mmff_props)
            ff.Minimize(maxIts=200)
            print("✅ MMFF optimization successful")
        else:
            AllChem.UFFOptimizeMolecule(mol, maxIts=200)
            print("✅ UFF optimization successful (MMFF not available)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_receptor_preparation():
    """Test PDB cleaning with BioPython"""
    from Bio import PDB
    import tempfile
    
    print("\n" + "=" * 60)
    print("TESTING RECEPTOR PREPARATION")
    print("=" * 60)
    
    # Create minimal PDB content for testing
    test_pdb = """ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N  
ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C  
ATOM      3  C   ALA A   1       2.009   1.420   0.000  1.00  0.00           C  
ATOM      4  O   ALA A   1       1.251   2.385   0.000  1.00  0.00           O  
HETATM    5  O   HOH A   2       5.000   5.000   5.000  1.00  0.00           O  
TER
END
"""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as f:
            f.write(test_pdb)
            temp_pdb_path = f.name
        
        parser = PDB.PDBParser(QUIET=True)
        structure = parser.get_structure('test', temp_pdb_path)
        
        print(f"✅ BioPython PDB parsing works")
        
        # Test protein selection
        class ProteinSelect(PDB.Select):
            def accept_residue(self, residue):
                return residue.get_id()[0] == ' '
        
        io = PDB.PDBIO()
        io.set_structure(structure)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_clean.pdb', delete=False) as f:
            io.save(f.name, ProteinSelect())
            print(f"✅ Protein selection/filtering works")
        
        import os
        os.unlink(temp_pdb_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " PROTEINDOCK VINA DOCKING - SYSTEM VERIFICATION ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run all checks
    results.append(("Dependencies", check_dependencies()))
    results.append(("Vina Binary", check_vina_binary()))
    results.append(("Ligand Prep", test_ligand_preparation()))
    results.append(("Receptor Prep", test_receptor_preparation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED - Ready for real docking!")
        print("\nYou can now test with:")
        print("  - Protein: 1HSG (HIV protease)")
        print("  - Ligand: Ritonavir")
        print("  - Expected affinity: -8 to -11 kcal/mol")
        return 0
    else:
        print("\n⚠️  SOME CHECKS FAILED - Fix issues before docking")
        return 1

if __name__ == '__main__':
    sys.exit(main())
