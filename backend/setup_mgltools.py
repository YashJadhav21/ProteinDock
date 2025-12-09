#!/usr/bin/env python3
"""
Download and setup MGLTools AutoDockTools utilities for Linux deployment

This script downloads the minimal MGLTools components needed for prepare_receptor4.py
without requiring the full MGLTools installation.
"""

import os
import sys
import urllib.request
import tarfile
import shutil
from pathlib import Path

def download_mgltools():
    """Download MGLTools for Linux"""
    
    script_dir = Path(__file__).parent
    mgltools_dir = script_dir / "mgltools"
    
    print("Setting up MGLTools AutoDockTools utilities...")
    
    # MGLTools download URL (Linux 64-bit)
    # Using the AutoDockTools standalone package which is lighter
    url = "http://mgltools.scripps.edu/downloads/downloads/tars/releases/REL1.5.7/mgltools_x86_64Linux2_1.5.7.tar.gz"
    
    print(f"Downloading from: {url}")
    print("This may take a few minutes...")
    
    # Download
    tar_file = script_dir / "mgltools.tar.gz"
    
    try:
        urllib.request.urlretrieve(url, tar_file)
        print(f"Downloaded to: {tar_file}")
        
        # Extract
        print("Extracting MGLTools...")
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(script_dir / "mgltools_temp")
        
        print("Extraction complete!")
        
        # Copy only the needed files (AutoDockTools/Utilities24)
        temp_dir = script_dir / "mgltools_temp" / "mgltools_x86_64Linux2_1.5.7"
        source_path = temp_dir / "MGLToolsPckgs"
        
        if source_path.exists():
            # Copy the entire MGLToolsPckgs folder
            print(f"Copying MGLTools packages to {mgltools_dir}...")
            if mgltools_dir.exists():
                shutil.rmtree(mgltools_dir)
            shutil.copytree(source_path, mgltools_dir / "MGLToolsPckgs")
            print("MGLTools setup complete!")
        else:
            print(f"Error: Source path not found: {source_path}")
            sys.exit(1)
        
        # Cleanup
        print("Cleaning up temporary files...")
        shutil.rmtree(script_dir / "mgltools_temp")
        os.remove(tar_file)
        
        # Verify installation
        prepare_receptor = mgltools_dir / "MGLToolsPckgs" / "AutoDockTools" / "Utilities24" / "prepare_receptor4.py"
        if prepare_receptor.exists():
            print(f"\n✅ SUCCESS! prepare_receptor4.py is ready at:")
            print(f"   {prepare_receptor}")
            print("\nMGLTools is now ready for production deployment!")
        else:
            print(f"\n❌ ERROR: prepare_receptor4.py not found at expected location")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAlternative: You can manually download MGLTools from:")
        print("http://mgltools.scripps.edu/downloads")
        sys.exit(1)

if __name__ == "__main__":
    download_mgltools()
