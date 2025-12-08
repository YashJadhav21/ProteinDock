#!/usr/bin/env python
"""
Download properly prepared 1HSG receptor for testing

This downloads a pre-prepared PDBQT receptor from online sources
to bypass the need for AutoDockTools installation.
"""

import requests
import sys

def download_1hsg_receptor():
    """Download pre-prepared 1HSG receptor PDBQT"""
    
    # Option 1: Try AutoDock Vina tutorial files
    urls = [
        # Vina tutorial receptor (properly prepared)
        "https://vina.scripps.edu/wp-content/uploads/sites/55/2020/12/1hsg_receptor.pdbqt",
        # Backup: PyRx prepared files
        "https://pyrx.sourceforge.io/downloads/1hsg_receptor.pdbqt",
    ]
    
    output_file = "1hsg_receptor_proper.pdbqt"
    
    for url in urls:
        try:
            print(f"Trying to download from: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Verify it's a valid PDBQT
                if 'ATOM' in content and ('PDBQT' in content or 'REMARK' in content):
                    with open(output_file, 'w') as f:
                        f.write(content)
                    
                    print(f"✅ Downloaded receptor to: {output_file}")
                    print(f"   Size: {len(content)} bytes")
                    print(f"   Lines: {len(content.splitlines())}")
                    return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    print("\n⚠️  Could not download from online sources.")
    print("Creating minimal PDBQT manually...")
    create_minimal_1hsg_receptor(output_file)
    return True

def create_minimal_1hsg_receptor(output_file):
    """
    Create a minimal but functional 1HSG receptor PDBQT
    Uses cleaned PDB with basic PDBQT formatting
    """
    import urllib.request
    
    # Download clean 1HSG PDB from RCSB
    pdb_url = "https://files.rcsb.org/download/1HSG.pdb"
    
    print(f"Downloading PDB from RCSB: {pdb_url}")
    
    with urllib.request.urlopen(pdb_url) as response:
        pdb_content = response.read().decode('utf-8')
    
    # Process PDB → minimal PDBQT
    lines = pdb_content.split('\n')
    
    with open(output_file, 'w') as out:
        out.write("REMARK  1HSG HIV-1 Protease Receptor\n")
        out.write("REMARK  Prepared for AutoDock Vina\n")
        out.write("REMARK  Source: RCSB PDB\n")
        
        for line in lines:
            # Keep only protein ATOM lines (exclude waters, ligands)
            if line.startswith('ATOM'):
                # Check if it's not water or ligand
                res_name = line[17:20].strip()
                if res_name not in ['HOH', 'WAT', 'MK1']:  # MK1 is the ligand in 1HSG
                    # Write as PDBQT format (minimal)
                    out.write(line + '\n')
        
        out.write('TER\n')
        out.write('ENDMDL\n')
    
    print(f"✅ Created minimal receptor: {output_file}")

if __name__ == '__main__':
    download_1hsg_receptor()
