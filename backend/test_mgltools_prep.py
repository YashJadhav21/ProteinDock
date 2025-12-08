"""
Test MGLTools AutoDockTools prepare_receptor4.py integration

This script tests the new receptor preparation using prepare_receptor4.py
from MGLTools, which is the gold standard for AutoDock receptor preparation.
"""

import os
import sys
import subprocess

def test_prepare_receptor4():
    """Test prepare_receptor4.py with a sample PDB"""
    
    print("=" * 60)
    print("Testing MGLTools prepare_receptor4.py")
    print("=" * 60)
    
    # Paths
    mgltools_path = r"C:\Program Files (x86)\MGLTools-1.5.7\Lib\site-packages\AutoDockTools\Utilities24"
    prepare_receptor = os.path.join(mgltools_path, "prepare_receptor4.py")
    mgltools_python = r"C:\Program Files (x86)\MGLTools-1.5.7\python.exe"
    
    # Check if files exist
    print(f"\n1. Checking MGLTools installation...")
    if os.path.exists(prepare_receptor):
        print(f"   ✅ prepare_receptor4.py found: {prepare_receptor}")
    else:
        print(f"   ❌ prepare_receptor4.py NOT found: {prepare_receptor}")
        return False
    
    if os.path.exists(mgltools_python):
        print(f"   ✅ python.exe found: {mgltools_python}")
    else:
        print(f"   ❌ python.exe NOT found: {mgltools_python}")
        return False
    
    # Create a minimal PDB for testing (1HSG binding site)
    test_pdb = "test_receptor.pdb"
    test_pdbqt = "test_receptor.pdbqt"
    
    print(f"\n2. Creating test PDB file...")
    # Simple PDB with just a few atoms for quick testing
    pdb_content = """ATOM      1  N   PRO A  25      13.100  22.500   5.600  1.00 20.00           N  
ATOM      2  CA  PRO A  25      14.200  23.400   6.100  1.00 20.00           C  
ATOM      3  C   PRO A  25      15.300  22.800   6.900  1.00 20.00           C  
ATOM      4  O   PRO A  25      15.100  21.700   7.400  1.00 20.00           O  
END
"""
    
    with open(test_pdb, 'w') as f:
        f.write(pdb_content)
    print(f"   ✅ Test PDB created: {test_pdb}")
    
    # Run prepare_receptor4.py
    print(f"\n3. Running prepare_receptor4.py...")
    cmd = [
        mgltools_python,
        prepare_receptor,
        '-r', test_pdb,
        '-o', test_pdbqt,
        '-A', 'hydrogens',
        '-U', 'nphs_lps'
    ]
    
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\n   Return code: {result.returncode}")
        
        if result.stdout:
            print(f"   STDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"   STDERR:\n{result.stderr}")
        
        # Check if output was created
        if os.path.exists(test_pdbqt):
            print(f"\n   ✅ PDBQT file created successfully!")
            
            # Read and display first few lines
            with open(test_pdbqt, 'r') as f:
                lines = f.readlines()
                print(f"\n   PDBQT content ({len(lines)} lines):")
                print("   " + "-" * 50)
                for i, line in enumerate(lines[:10]):
                    print(f"   {line.rstrip()}")
                if len(lines) > 10:
                    print(f"   ... ({len(lines) - 10} more lines)")
            
            # Cleanup
            os.remove(test_pdbqt)
            os.remove(test_pdb)
            
            print(f"\n✅ SUCCESS: prepare_receptor4.py works correctly!")
            return True
        else:
            print(f"\n   ❌ PDBQT file was NOT created")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n   ❌ Command timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prepare_receptor4()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ MGLTools prepare_receptor4.py is ready to use!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ MGLTools prepare_receptor4.py test failed")
        print("=" * 60)
        sys.exit(1)
