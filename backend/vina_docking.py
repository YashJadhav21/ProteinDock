# AutoDock Vina Integration for ProteinDock
# This Python script handles molecular docking using AutoDock Vina

import sys
import json
import os
from pathlib import Path

# Debug: Print LD_LIBRARY_PATH
print(f"[Debug] LD_LIBRARY_PATH = {os.environ.get('LD_LIBRARY_PATH', 'NOT SET')}", file=sys.stderr)

def setup_vina_environment():
    """
    Check if Vina is available (binary or Python package)
    """
    import subprocess
    import platform
    
    # Check for vina binary (Windows: vina.exe, Linux: vina)
    vina_bin_dir = Path(__file__).parent / 'vina_bin'
    if platform.system() == 'Windows':
        vina_bin_path = vina_bin_dir / 'vina.exe'
    else:
        vina_bin_path = vina_bin_dir / 'vina'
    
    if vina_bin_path.exists():
        try:
            result = subprocess.run([str(vina_bin_path), '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if 'AutoDock Vina' in result.stdout or 'AutoDock Vina' in result.stderr:
                # Print to stderr so it doesn't interfere with JSON stdout
                print(f"[Vina] Using binary at {vina_bin_path}", file=sys.stderr)
                return True
        except Exception as e:
            print(f"[Vina] Binary found but not working: {str(e)}", file=sys.stderr)
    
    # Check for Python vina package
    try:
        __import__('vina')
        print("[Vina] Using Python package", file=sys.stderr)
        return True
    except ImportError:
        pass
    
    # Check other required packages
    required_packages = {
        'meeko': 'meeko',
        'rdkit': 'rdkit',
        'Bio': 'biopython'  # BioPython for PDB parsing
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    print(json.dumps({
        'status': 'error',
        'message': 'AutoDock Vina not available',
        'missing_packages': ['vina'] + missing,
        'install_command': f'pip install vina {" ".join(missing)}'
    }), file=sys.stderr)
    return False

def smiles_to_pdbqt(smiles, output_file):
    """
    Convert SMILES string to PDBQT format (MEMORY OPTIMIZED)
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from meeko import MoleculePreparation
        import gc
        
        # Convert SMILES to molecule
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        
        # Add hydrogens
        mol = Chem.AddHs(mol)
        num_atoms = mol.GetNumAtoms()
        
        print(f"[Ligand Prep] Generating 3D structure for {num_atoms} atoms", file=sys.stderr)
        
        # Use ETKDG for conformer generation
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        params.numThreads = 1  # Limit threads to save memory
        
        # Embed molecule
        result = AllChem.EmbedMolecule(mol, params)
        if result == -1:
            params.useRandomCoords = True
            result = AllChem.EmbedMolecule(mol, params)
            if result == -1:
                raise ValueError("Failed to generate 3D coordinates")
        
        print(f"[Ligand Prep] Optimizing geometry...", file=sys.stderr)
        
        # Optimize (use UFF for faster/lighter processing)
        AllChem.UFFOptimizeMolecule(mol, maxIts=1000)  # Reduced iterations
        
        # Prepare for docking
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        
        preparator = MoleculePreparation()
        mol_setups = preparator.prepare(mol)
        
        # Write PDBQT
        try:
            from meeko import PDBQTWriterLegacy
            writer = PDBQTWriterLegacy()
            pdbqt_string = writer.write_string(mol_setups[0])[0]
            with open(output_file, 'w') as f:
                f.write(pdbqt_string)
        except:
            preparator.write_pdbqt_file(output_file)
        
        # Cleanup
        del mol, preparator, mol_setups
        gc.collect()
        
        return True
    except Exception as e:
        raise Exception(f"SMILES to PDBQT conversion failed: {str(e)}")

def pdb_to_pdbqt_biopython(pdb_content, output_file):
    """
    Fallback: Convert PDB to PDBQT using RDKit directly (without Meeko)
    
    MEMORY OPTIMIZED: Processes in chunks and cleans up immediately
    """
    try:
        from Bio.PDB import PDBParser, PDBIO, Select
        from io import StringIO
        from rdkit import Chem
        from rdkit.Chem import AllChem
        import gc
        
        print(f"[Receptor Prep RDKit] Converting PDB to PDBQT (memory-optimized)", file=sys.stderr)
        
        # Parse PDB and extract protein only (no waters, ligands, ions)
        class ProteinSelect(Select):
            def accept_residue(self, residue):
                # Accept only standard amino acids
                return residue.id[0] == ' '
        
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', StringIO(pdb_content))
        
        # Write cleaned PDB (protein only)
        temp_pdb = output_file.replace('.pdbqt', '_clean.pdb')
        io = PDBIO()
        io.set_structure(structure)
        io.save(temp_pdb, ProteinSelect())
        
        # Free memory immediately
        del structure, parser, io
        gc.collect()
        
        print(f"[Receptor Prep RDKit] Loading molecule...", file=sys.stderr)
        
        # Read with RDKit (don't sanitize to save memory)
        mol = Chem.MolFromPDBFile(temp_pdb, removeHs=True, sanitize=False)  # Remove H first
        if mol is None:
            raise Exception("Failed to parse PDB with RDKit")
        
        num_atoms_initial = mol.GetNumAtoms()
        print(f"[Receptor Prep RDKit] Loaded {num_atoms_initial} atoms", file=sys.stderr)
        
        # Add only polar hydrogens (saves memory)
        mol = Chem.AddHs(mol, addCoords=True, onlyOnAtoms=None)
        print(f"[Receptor Prep RDKit] Now {mol.GetNumAtoms()} atoms with H", file=sys.stderr)
        
        # Compute Gasteiger charges in chunks to reduce memory
        print(f"[Receptor Prep RDKit] Computing charges...", file=sys.stderr)
        AllChem.ComputeGasteigerCharges(mol)
        
        # Write PDBQT in streaming mode (don't build huge array in memory)
        print(f"[Receptor Prep RDKit] Writing PDBQT...", file=sys.stderr)
        
        with open(output_file, 'w') as f:
            f.write("REMARK  Receptor prepared with RDKit (MGLTools fallback)\n")
            
            conf = mol.GetConformer()
            chunk_size = 500  # Process 500 atoms at a time
            total_atoms = mol.GetNumAtoms()
            
            for chunk_start in range(0, total_atoms, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_atoms)
                
                # Process chunk
                for atom_idx in range(chunk_start, chunk_end):
                    atom = mol.GetAtomWithIdx(atom_idx)
                    pos = conf.GetAtomPosition(atom_idx)
                    
                    # Get atom properties
                    atom_name = atom.GetSymbol()
                    residue_name = "UNK"
                    chain_id = "A"
                    residue_num = 1
                    
                    # Try to get PDB info if available
                    if atom.HasProp('_Name'):
                        atom_name = atom.GetProp('_Name')
                    if atom.GetMonomerInfo():
                        residue_name = atom.GetMonomerInfo().GetResidueName()
                        residue_num = atom.GetMonomerInfo().GetResidueNumber()
                        chain_id = atom.GetMonomerInfo().GetChainId()
                    
                    # Get charge
                    charge = 0.0
                    if atom.HasProp('_GasteigerCharge'):
                        try:
                            charge = float(atom.GetProp('_GasteigerCharge'))
                            if charge != charge:  # NaN check
                                charge = 0.0
                        except:
                            charge = 0.0
                    
                    # Determine AutoDock atom type
                    symbol = atom.GetSymbol()
                    if symbol == 'C':
                        atom_type = 'A' if atom.GetIsAromatic() else 'C'
                    elif symbol == 'N':
                        atom_type = 'NA' if atom.GetIsAromatic() else 'N'
                    elif symbol == 'O':
                        atom_type = 'OA' if atom.GetTotalValence() >= 2 else 'O'
                    elif symbol == 'S':
                        atom_type = 'SA'
                    elif symbol == 'H':
                        atom_type = 'HD'
                    else:
                        atom_type = symbol
                    
                    # Write PDBQT line directly to file
                    line = f"ATOM  {atom_idx+1:5d} {atom_name:^4s} {residue_name:3s} {chain_id:1s}{residue_num:4d}    "
                    line += f"{pos.x:8.3f}{pos.y:8.3f}{pos.z:8.3f}  1.00  0.00    "
                    line += f"{charge:6.3f} {atom_type:2s}\n"
                    f.write(line)
                
                # Print progress for large proteins
                if total_atoms > 1000:
                    progress = int((chunk_end / total_atoms) * 100)
                    print(f"[Receptor Prep RDKit] Writing: {progress}% ({chunk_end}/{total_atoms} atoms)", file=sys.stderr)
            
            f.write("TER\nENDMDL\n")
        
        print(f"[Receptor Prep RDKit] ✅ PDBQT created ({total_atoms} atoms)", file=sys.stderr)
        
        # Cleanup memory aggressively
        del mol, conf
        gc.collect()
        
        # Remove temp file
        if os.path.exists(temp_pdb):
            os.remove(temp_pdb)
        
        return True
        
    except Exception as e:
        print(f"[Receptor Prep RDKit Error] {str(e)}", file=sys.stderr)
        import traceback
        print(f"[Receptor Prep RDKit Traceback] {traceback.format_exc()}", file=sys.stderr)
        raise Exception(f"RDKit PDB to PDBQT conversion failed: {str(e)}")

def pdb_to_pdbqt(pdb_content, output_file):
    """
    Convert PDB to PDBQT using MGLTools AutoDockTools prepare_receptor4.py
    
    This is the GOLD STANDARD receptor preparation tool from AutoDockTools.
    Creates proper PDBQT files with correct atom types, hydrogens, and Gasteiger charges.
    
    Uses bundled MGLTools scripts included in the repository.
    """
    try:
        import subprocess
        import tempfile
        import platform
        
        print(f"[Receptor Prep] Using AutoDockTools prepare_receptor4.py", file=sys.stderr)
        
        # Write PDB to temporary file
        temp_pdb = output_file.replace('.pdbqt', '_input.pdb')
        with open(temp_pdb, 'w') as f:
            f.write(pdb_content)
        
        # Detect platform and set MGLTools paths accordingly
        script_dir = Path(__file__).parent
        system = platform.system()
        
        if system == 'Windows':
            # Windows: Use installed MGLTools
            mgltools_path = r"C:\Program Files (x86)\MGLTools-1.5.7\Lib\site-packages\AutoDockTools\Utilities24"
            prepare_receptor = os.path.join(mgltools_path, "prepare_receptor4.py")
            mgltools_python = r"C:\Program Files (x86)\MGLTools-1.5.7\python.exe"
        else:
            # Linux/Render: Use bundled MGLTools scripts from repo
            mgltools_path = script_dir / "mgltools" / "AutoDockTools" / "Utilities24"
            prepare_receptor = mgltools_path / "prepare_receptor4.py"
            # MGLTools scripts are Python 2 - try python2.7, python2, or fallback to conversion
            mgltools_python = None
            for py2_cmd in ['python2.7', 'python2', '/usr/bin/python2.7', '/usr/bin/python2']:
                try:
                    result = subprocess.run([py2_cmd, '--version'], capture_output=True, timeout=2)
                    if result.returncode == 0:
                        mgltools_python = py2_cmd
                        print(f"[Receptor Prep] Found Python 2: {py2_cmd}", file=sys.stderr)
                        break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            if not mgltools_python:
                # No Python 2 available - will use fallback RDKit conversion
                print(f"[Receptor Prep] Python 2 not available, using RDKit fallback", file=sys.stderr)
        
        print(f"[Receptor Prep] Platform: {system}", file=sys.stderr)
        print(f"[Receptor Prep] Script path: {prepare_receptor}", file=sys.stderr)
        
        # If Python 2 not available on Linux, use RDKit fallback
        if system != 'Windows' and not mgltools_python:
            print(f"[Receptor Prep] Using RDKit fallback (no Python 2)", file=sys.stderr)
            return pdb_to_pdbqt_biopython(pdb_content, output_file)
        
        if not os.path.exists(prepare_receptor):
            raise Exception(f"prepare_receptor4.py not found at: {prepare_receptor}")
        
        # On Windows, check if MGLTools python exists
        if system == 'Windows' and not os.path.exists(mgltools_python):
            raise Exception(f"Python executable not found at: {mgltools_python}")
        
        print(f"[Receptor Prep] Using Python: {mgltools_python}", file=sys.stderr)
        print(f"[Receptor Prep] Using script: {prepare_receptor}", file=sys.stderr)
        
        # Run prepare_receptor4.py
        # -r: input receptor PDB file
        # -o: output PDBQT file
        # -A: automatically add hydrogens and merge non-polar hydrogens
        # -U: cleanup (remove lone pairs, add hydrogens, etc.)
        cmd = [
            str(mgltools_python),
            str(prepare_receptor),
            '-r', temp_pdb,      # Receptor PDB input
            '-o', output_file,   # PDBQT output
            '-A', 'hydrogens',   # Add all hydrogens
            '-U', 'nphs_lps'     # Cleanup: merge non-polar hydrogens, remove lone pairs
        ]
        
        print(f"[Receptor Prep] Running: {' '.join(cmd)}", file=sys.stderr)
        
        # Set PYTHONPATH for Linux to find bundled MGLTools modules
        env = os.environ.copy()
        if system != 'Windows':
            mgltools_base = script_dir / "mgltools"
            env['PYTHONPATH'] = str(mgltools_base) + os.pathsep + env.get('PYTHONPATH', '')
            print(f"[Receptor Prep] PYTHONPATH: {env['PYTHONPATH']}", file=sys.stderr)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(output_file),
            env=env  # Pass environment with PYTHONPATH
        )
        
        if result.returncode != 0:
            print(f"[Receptor Prep] stderr: {result.stderr}", file=sys.stderr)
            print(f"[Receptor Prep] stdout: {result.stdout}", file=sys.stderr)
            raise Exception(f"prepare_receptor4.py failed: {result.stderr}")
        
        print(f"[Receptor Prep] stdout: {result.stdout}", file=sys.stderr)
        
        # Verify output file was created
        if not os.path.exists(output_file):
            raise Exception(f"Output PDBQT file not created: {output_file}")
        
        # Verify it has content and fix formatting issues
        with open(output_file, 'r') as f:
            content = f.read()
            if len(content) < 100:
                raise Exception(f"Output PDBQT file is too small: {len(content)} bytes")
        
        # Fix malformed PDBQT coordinates (MGLTools bug with some PDB files)
        fixed_lines = []
        fixes_applied = 0
        for line in content.split('\n'):
            if line.startswith('ATOM') or line.startswith('HETATM'):
                # Check if coordinate fields are properly formatted
                # PDBQT format: columns 31-38 (x), 39-46 (y), 47-54 (z)
                if len(line) >= 54:
                    try:
                        # Extract coordinate substring
                        coords_str = line[30:54]
                        # Try to parse as three floats
                        parts = coords_str.split()
                        if len(parts) >= 3:
                            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                            # Rebuild line with proper formatting
                            fixed_line = line[:30] + f"{x:8.3f}{y:8.3f}{z:8.3f}" + line[54:]
                            fixed_lines.append(fixed_line)
                            if coords_str != f"{x:8.3f}{y:8.3f}{z:8.3f}":
                                fixes_applied += 1
                            continue
                    except (ValueError, IndexError):
                        pass
            fixed_lines.append(line)
        
        if fixes_applied > 0:
            print(f"[Receptor Prep] Fixed {fixes_applied} malformed coordinate lines", file=sys.stderr)
            with open(output_file, 'w') as f:
                f.write('\n'.join(fixed_lines))
        
        print(f"[Receptor Prep] ✅ PDBQT created successfully with prepare_receptor4.py", file=sys.stderr)
        
        # Cleanup temporary PDB
        if os.path.exists(temp_pdb):
            os.remove(temp_pdb)
        
        return True
        
    except Exception as e:
        print(f"[Receptor Prep Error] {str(e)}", file=sys.stderr)
        import traceback
        print(f"[Receptor Prep Traceback] {traceback.format_exc()}", file=sys.stderr)
        raise Exception(f"PDB to PDBQT conversion failed: {str(e)}")

def run_vina_docking(receptor_pdbqt, ligand_pdbqt, config):
    """
    Run AutoDock Vina docking (MEMORY OPTIMIZED)
    
    Args:
        receptor_pdbqt: Path to receptor PDBQT file
        ligand_pdbqt: Path to ligand PDBQT file
        config: Dictionary with docking parameters
    """
    import subprocess
    import tempfile
    import gc
    
    try:
        # Validate input files exist
        if not os.path.exists(receptor_pdbqt):
            raise Exception(f"Receptor file not found: {receptor_pdbqt}")
        if not os.path.exists(ligand_pdbqt):
            raise Exception(f"Ligand file not found: {ligand_pdbqt}")
        
        # Get Vina binary path
        import platform
        vina_bin_dir = Path(__file__).parent / 'vina_bin'
        if platform.system() == 'Windows':
            vina_bin_path = vina_bin_dir / 'vina.exe'
        else:
            vina_bin_path = vina_bin_dir / 'vina'
        
        if not vina_bin_path.exists():
            # Try Python vina as fallback
            try:
                from vina import Vina
                return run_vina_docking_python(receptor_pdbqt, ligand_pdbqt, config)
            except ImportError:
                raise Exception("Vina binary not found and Python package not installed")
        
        # Prepare configuration
        center = config.get('gridCenter', {'x': 0, 'y': 0, 'z': 0})
        size = config.get('gridSize', {'x': 20, 'y': 20, 'z': 20})
        exhaustiveness = config.get('exhaustivity', 8)
        n_poses = config.get('numPoses', 9)
        
        # MEMORY OPTIMIZATION: Limit CPU count and adjust exhaustivity
        import multiprocessing
        cpu_count = min(2, multiprocessing.cpu_count())  # Limit to 2 cores to save memory
        
        # Reduce exhaustivity if too high (saves memory)
        if exhaustiveness > 8:
            print(f"[Vina] Reducing exhaustivity from {exhaustiveness} to 8 (memory optimization)", file=sys.stderr)
            exhaustiveness = 8
        
        # Reduce poses if too many
        if n_poses > 5:
            print(f"[Vina] Reducing poses from {n_poses} to 5 (memory optimization)", file=sys.stderr)
            n_poses = 5
        
        # Validate grid size
        min_size = min(size['x'], size['y'], size['z'])
        if min_size < 15:
            print(f"[Vina Warning] Small grid box ({min_size}Å)", file=sys.stderr)
        except Exception:
            pass
        
        # Validate exhaustiveness
        if exhaustiveness < 1:
            print(f"[Vina Warning] Exhaustiveness too low ({exhaustiveness}), setting to 1", file=sys.stderr)
            exhaustiveness = 1
        if exhaustiveness > 32:
        
        # Output file
        output_file = ligand_pdbqt.replace('.pdbqt', '_out.pdbqt')
        
        # Create config file
        config_fd, config_file = tempfile.mkstemp(suffix='.txt', text=True)
        try:
            with os.fdopen(config_fd, 'w') as conf:
                conf.write(f"receptor = {receptor_pdbqt}\n")
                conf.write(f"ligand = {ligand_pdbqt}\n")
                conf.write(f"center_x = {center['x']}\n")
                conf.write(f"center_y = {center['y']}\n")
                conf.write(f"center_z = {center['z']}\n")
                conf.write(f"size_x = {size['x']}\n")
                conf.write(f"size_y = {size['y']}\n")
                conf.write(f"size_z = {size['z']}\n")
                conf.write(f"exhaustiveness = {exhaustiveness}\n")
                conf.write(f"cpu = {cpu_count}\n")
                conf.write(f"num_modes = {n_poses}\n")
                conf.write(f"out = {output_file}\n")
                conf.flush()
                os.fsync(conf.fileno())
        except Exception:
            os.close(config_fd)
            raise
        
        print(f"[Vina] Using {cpu_count} cores, exhaustivity={exhaustiveness}, poses={n_poses}", file=sys.stderr)
        
        # Start Vina (no progress monitoring to save memory)
        print(f"[Vina] Starting docking...", file=sys.stderr)
        
        process = subprocess.Popen(
            [str(vina_bin_path), '--config', config_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for completion (15 min timeout for memory-limited environment)
        try:
            stdout, stderr = process.communicate(timeout=900)  # 15 min timeout
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            raise Exception(f"Vina timed out after 15 minutes")
        
        # Cleanup
        os.unlink(config_file)
        gc.collect()
        
        if process.returncode != 0:
            raise Exception(f"Vina execution failed: {stderr}")
        
        print(f"[Vina] Docking complete", file=sys.stderr)
        
        # Parse results from output
        poses = []
        for line in stdout.split('\n'):
            # Look for lines like: "   1        -7.5      0.000      0.000"
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0].isdigit():
                try:
                    pose_num = int(parts[0])
                    affinity = float(parts[1])
                    rmsd_lb = float(parts[2]) if len(parts) > 2 else 0.0
                    rmsd_ub = float(parts[3]) if len(parts) > 3 else 0.0
                    
                    poses.append({
                        'poseId': pose_num,
                        'score': affinity,
                        'rmsd_lb': rmsd_lb,
                        'rmsd_ub': rmsd_ub
                    })
                except (ValueError, IndexError):
                    continue
        
        if not poses:
            raise Exception("No poses found in Vina output")
        
        return {
            'status': 'success',
            'poses': poses,
            'output_file': output_file,
            'best_affinity': poses[0]['score'] if poses else None
        }
        
    except subprocess.TimeoutExpired:
        raise Exception("Vina docking timed out (>30 minutes). Try reducing exhaustivity or grid size.")
    except Exception as e:
        raise Exception(f"Vina docking failed: {str(e)}")

def run_vina_docking_python(receptor_pdbqt, ligand_pdbqt, config):
    """
    Run AutoDock Vina docking using Python bindings (fallback)
    """
    from vina import Vina
    
    # Initialize Vina
    v = Vina(sf_name='vina', verbosity=0)
    
    # Set receptor
    v.set_receptor(receptor_pdbqt)
    
    # Set ligand
    v.set_ligand_from_file(ligand_pdbqt)
    
    # Set search space
    center = config.get('gridCenter', {'x': 0, 'y': 0, 'z': 0})
    size = config.get('gridSize', {'x': 20, 'y': 20, 'z': 20})
    
    v.compute_vina_maps(
        center=[center['x'], center['y'], center['z']],
        box_size=[size['x'], size['y'], size['z']]
    )
    
    # Run docking
    exhaustiveness = config.get('exhaustivity', 8)
    n_poses = config.get('numPoses', 9)
    
    v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    
    # Get results
    energies = v.energies()
    poses = []
    
    for i in range(len(energies)):
        poses.append({
            'poseId': i + 1,
            'score': float(energies[i][0]),
            'rmsd_lb': float(energies[i][1]) if len(energies[i]) > 1 else 0.0,
            'rmsd_ub': float(energies[i][2]) if len(energies[i]) > 2 else 0.0
        })
    
    # Write output poses
    output_file = ligand_pdbqt.replace('.pdbqt', '_out.pdbqt')
    v.write_poses(output_file, n_poses=n_poses, overwrite=True)
    
    return {
        'status': 'success',
        'poses': poses,
        'output_file': output_file,
        'best_affinity': float(energies[0][0]) if energies else None
    }

def detect_binding_site(pdb_content):
    """
    Automatically detect binding site from PDB structure
    
    Priority order:
    1. Co-crystallized ligand (HETATM records)
    2. Center of mass (fallback)
    
    Returns:
        dict: {
            'center': {'x': float, 'y': float, 'z': float},
            'size': {'x': float, 'y': float, 'z': float},
            'method': str,
            'confidence': str
        }
    """
    try:
        from Bio.PDB import PDBParser
        from io import StringIO
        import numpy as np
        
        # Parse PDB structure
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', StringIO(pdb_content))
        
        # Method 1: Look for co-crystallized ligand (HETATM)
        # Skip: water, ions, solvents, glycerol, buffers
        skip_residues = {
            'HOH', 'WAT', 'H2O', 'DOD', 'D2O',  # Water
            'NA', 'CL', 'K', 'BR', 'I', 'F',     # Ions
            'MG', 'CA', 'ZN', 'FE', 'MN', 'CU', 'NI', 'CO',  # Metal ions
            'SO4', 'PO4', 'NO3', 'ACT', 'EDO', 'GOL', 'PEG',  # Buffers/additives
            'DMS', 'DMSO', 'BME', 'DTT', 'TRS', 'EPE',  # Solvents/reducing agents
            'PG4', 'P6G', 'PEG', 'P33', 'PE8', 'PE7',  # Polyethylene glycol
            'SO3', 'SUL', 'FMT', 'AZI', 'IOD', 'CIT'   # Other common additives
        }
        
        # Collect all hetero residues with their atoms
        hetero_groups = {}
        
        for model in structure:
            for chain in model:
                for residue in chain:
                    if residue.id[0].startswith('H_'):
                        resname = residue.resname.strip()
                        if resname not in skip_residues:
                            if resname not in hetero_groups:
                                hetero_groups[resname] = []
                            for atom in residue:
                                hetero_groups[resname].append(atom.coord)
        
        # Find the largest ligand (most likely the inhibitor, not cofactor)
        if hetero_groups:
            largest_ligand = max(hetero_groups.items(), key=lambda x: len(x[1]))
            ligand_name = largest_ligand[0]
            ligand_coords = np.array(largest_ligand[1])
            
            # Calculate center and bounding box
            center = np.mean(ligand_coords, axis=0)
            min_coords = np.min(ligand_coords, axis=0)
            max_coords = np.max(ligand_coords, axis=0)
            span = max_coords - min_coords
            
            # Intelligent sizing based on ligand size
            # Small ligands (< 20 atoms): 22Å box
            # Medium ligands (20-50 atoms): 25Å box
            # Large ligands (> 50 atoms): 28Å box
            num_atoms = len(ligand_coords)
            if num_atoms < 20:
                base_size = 22.0
            elif num_atoms < 50:
                base_size = 25.0
            else:
                base_size = 28.0
            
            # Use larger of: base_size or ligand_span + 12Å padding
            size = np.maximum(span + 12.0, base_size)
            
            # Cap at 35Å to avoid excessive search space
            size = np.minimum(size, 35.0)
            
            print(f"[Grid Detection] Found {len(hetero_groups)} hetero residues, using largest: {ligand_name} ({num_atoms} atoms)", file=sys.stderr)
            print(f"[Grid Detection] Ligand center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})", file=sys.stderr)
            print(f"[Grid Detection] Grid size: ({size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f}) Å", file=sys.stderr)
            
            return {
                'center': {'x': float(center[0]), 'y': float(center[1]), 'z': float(center[2])},
                'size': {'x': float(size[0]), 'y': float(size[1]), 'z': float(size[2])},
                'method': f'co-crystallized ligand ({ligand_name}, {num_atoms} atoms)',
                'confidence': 'high'
            }
        
        # Method 2: Center of mass (fallback)
        protein_coords = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    if residue.id[0] == ' ':  # Standard amino acids only
                        for atom in residue:
                            if atom.name == 'CA':  # C-alpha atoms only
                                protein_coords.append(atom.coord)
        
        if len(protein_coords) > 0:
            coords_array = np.array(protein_coords)
            center = np.mean(coords_array, axis=0)
            
            # Use generous grid size (30Å cube) for whole protein search
            size = np.array([30.0, 30.0, 30.0])
            
            print(f"[Grid Detection] No ligand found - using center of mass", file=sys.stderr)
            print(f"[Grid Detection] Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})", file=sys.stderr)
            print(f"[Grid Detection] Grid size: 30x30x30 Å (whole protein search)", file=sys.stderr)
            
            return {
                'center': {'x': float(center[0]), 'y': float(center[1]), 'z': float(center[2])},
                'size': {'x': 30.0, 'y': 30.0, 'z': 30.0},
                'method': 'center of mass (whole protein)',
                'confidence': 'low'
            }
        
        raise Exception("Could not extract coordinates from PDB")
        
    except Exception as e:
        print(f"[Grid Detection Error] {str(e)}", file=sys.stderr)
        # Ultimate fallback
        return {
            'center': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'size': {'x': 25.0, 'y': 25.0, 'z': 25.0},
            'method': 'default (failed detection)',
            'confidence': 'none'
        }

def split_vina_poses(output_pdbqt, work_dir):
    """
    Split multi-model PDBQT file into individual pose files
    
    Vina outputs all poses in one file. This function separates them.
    """
    import os
    
    try:
        if not os.path.exists(output_pdbqt):
            raise FileNotFoundError(f"Output file not found: {output_pdbqt}")
        
        # Read the output file
        with open(output_pdbqt, 'r') as f:
            content = f.read()
        
        # Split by MODEL records
        poses = []
        current_pose = []
        pose_num = 0
        
        for line in content.split('\n'):
            if line.startswith('MODEL'):
                pose_num += 1
                current_pose = [line + '\n']
            elif line.startswith('ENDMDL'):
                current_pose.append(line + '\n')
                poses.append(''.join(current_pose))
                current_pose = []
            elif current_pose:
                current_pose.append(line + '\n')
        
        # Write individual pose files
        pose_files = []
        for i, pose_content in enumerate(poses, 1):
            pose_file = os.path.join(work_dir, f'pose_{i}.pdbqt')
            with open(pose_file, 'w') as f:
                f.write(pose_content)
            pose_files.append(pose_file)
            print(f"[Pose Separation] Created pose file: pose_{i}.pdbqt", file=sys.stderr)
        
        print(f"[Pose Separation] Successfully split {len(poses)} poses", file=sys.stderr)
        return pose_files
        
    except Exception as e:
        print(f"[Pose Separation Error] {str(e)}", file=sys.stderr)
        return []

def pdbqt_to_pdb(pdbqt_file, pdb_file):
    """
    Convert PDBQT file to PDB format
    
    Simple conversion: remove charge and atom type columns
    """
    try:
        with open(pdbqt_file, 'r') as f:
            lines = f.readlines()
        
        pdb_lines = []
        for line in lines:
            if line.startswith(('ATOM', 'HETATM')):
                # PDBQT format has charge and atom type in last columns
                # PDB format doesn't need them
                pdb_line = line[:66] + '\n'  # Truncate extra columns
                pdb_lines.append(pdb_line)
            elif line.startswith(('MODEL', 'ENDMDL', 'TER', 'END')):
                pdb_lines.append(line)
        
        with open(pdb_file, 'w') as f:
            f.writelines(pdb_lines)
        
        print(f"[PDBQT→PDB] Converted: {pdbqt_file} → {pdb_file}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"[PDBQT→PDB Error] {str(e)}", file=sys.stderr)
        return False

def create_complex(receptor_pdb, ligand_pdb, complex_pdb):
    """
    Create protein-ligand complex by merging PDB files
    
    Args:
        receptor_pdb: Path to receptor PDB file
        ligand_pdb: Path to ligand PDB file (single pose)
        complex_pdb: Path to output complex PDB file
    """
    try:
        # Read receptor
        with open(receptor_pdb, 'r') as f:
            receptor_lines = f.readlines()
        
        # Read ligand
        with open(ligand_pdb, 'r') as f:
            ligand_lines = f.readlines()
        
        # Combine: receptor + TER + ligand
        complex_lines = []
        
        # Add receptor (skip END records)
        for line in receptor_lines:
            if not line.startswith('END'):
                complex_lines.append(line)
        
        # Add separator
        complex_lines.append('TER\n')
        
        # Add ligand (skip MODEL/ENDMDL if present)
        for line in ligand_lines:
            if not line.startswith(('MODEL', 'ENDMDL', 'END')):
                complex_lines.append(line)
        
        # Add final END
        complex_lines.append('END\n')
        
        # Write complex
        with open(complex_pdb, 'w') as f:
            f.writelines(complex_lines)
        
        print(f"[Complex] Created: {complex_pdb}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"[Complex Error] {str(e)}", file=sys.stderr)
        return False

def parse_interactions(complex_pdb_path):
    """
    Analyze protein-ligand interactions using custom interaction analyzer
    
    Args:
        complex_pdb_path: Path to complex PDB file
    
    Returns:
        Dictionary with interaction details
    """
    try:
        # Import interaction analyzer
        from interaction_analysis import analyze_complex
        
        # Analyze interactions
        interactions = analyze_complex(complex_pdb_path)
        return interactions
        
    except Exception as e:
        print(f"[Interaction Analysis Error] {str(e)}", file=sys.stderr)
        return {
            'hBonds': [],
            'hydrophobic': [],
            'piStacking': [],
            'ionic': [],
            'summary': {'error': str(e)}
        }

def generate_visualizations(complex_pdb_path, output_dir):
    """
    Generate interactive HTML visualization for protein-ligand complex
    
    Args:
        complex_pdb_path: Path to complex PDB file
        output_dir: Directory to save visualization HTML
    
    Returns:
        Dictionary with viewer information
    """
    try:
        # Import visualization module
        from visualization import generate_interactive_viewer
        
        # Generate interactive HTML viewer (auto-expires in 30 minutes)
        viewer_info = generate_interactive_viewer(
            complex_pdb_path, 
            output_dir,
            view_type='publication',
            expire_minutes=30
        )
        
        return viewer_info
        
    except Exception as e:
        print(f"[Visualization Error] {str(e)}", file=sys.stderr)
        return {}

def main():
    """
    Main entry point for Vina docking
    Expected input (via stdin): JSON with smiles, pdb_content, and config
    OR {"check_only": true} to just check if Vina is available
    """
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Handle check_only mode
        if input_data.get('check_only'):
            if setup_vina_environment():
                print(json.dumps({'status': 'success', 'available': True}), flush=True)
                sys.exit(0)
            else:
                sys.exit(1)
        
        # Check environment for actual docking
        if not setup_vina_environment():
            sys.exit(1)
        
        smiles = input_data.get('smiles')
        pdb_content = input_data.get('pdb_content')
        config = input_data.get('config', {})
        work_dir = input_data.get('work_dir', './docking_temp')
        auto_grid = input_data.get('auto_grid', True)  # Enable auto-detection by default
        
        # Create working directory
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        
        # File paths
        ligand_pdbqt = os.path.join(work_dir, 'ligand.pdbqt')
        receptor_pdbqt = os.path.join(work_dir, 'receptor.pdbqt')
        receptor_pdb = os.path.join(work_dir, 'receptor.pdb')
        
        # Convert SMILES to PDBQT
        print(json.dumps({'progress': 15, 'message': 'Preparing ligand...'}), flush=True)
        smiles_to_pdbqt(smiles, ligand_pdbqt)
        
        # Force garbage collection after ligand prep
        import gc
        gc.collect()
        
        # Save receptor PDB for later use
        with open(receptor_pdb, 'w') as f:
            f.write(pdb_content)
        
        # Auto-detect binding site if requested
        if auto_grid:
            print(json.dumps({'progress': 25, 'message': 'Detecting binding site...'}), flush=True)
            grid_info = detect_binding_site(pdb_content)
            
            # Override config with detected values
            config['gridCenter'] = grid_info['center']
            config['gridSize'] = grid_info['size']
            
            print(json.dumps({
                'progress': 30, 
                'message': f'Grid detected using {grid_info["method"]}',
                'grid_info': grid_info
            }), flush=True)
            
            # Cleanup
            gc.collect()
        
        # Convert PDB to PDBQT
        print(json.dumps({'progress': 40, 'message': 'Preparing receptor...'}), flush=True)
        pdb_to_pdbqt(pdb_content, receptor_pdbqt)
        
        # Force garbage collection after receptor prep (biggest memory use)
        gc.collect()
        
        # Run docking
        print(json.dumps({'progress': 50, 'message': 'Running Vina docking...'}), flush=True)
        result = run_vina_docking(receptor_pdbqt, ligand_pdbqt, config)
        
        # Cleanup after docking
        gc.collect()
        
        # Split poses into individual files
        print(json.dumps({'progress': 85, 'message': 'Separating poses...'}), flush=True)
        pose_files = split_vina_poses(result['output_file'], work_dir)
        
        # Convert best pose to PDB and create complex
        if pose_files and len(pose_files) > 0:
            print(json.dumps({'progress': 90, 'message': 'Creating complex...'}), flush=True)
            
            # Convert best pose PDBQT → PDB
            best_pose_pdbqt = pose_files[0]  # Poses are already sorted by score
            best_pose_pdb = best_pose_pdbqt.replace('.pdbqt', '.pdb')
            pdbqt_to_pdb(best_pose_pdbqt, best_pose_pdb)
            
            # Create complex
            complex_pdb = os.path.join(work_dir, 'complex.pdb')
            create_complex(receptor_pdb, best_pose_pdb, complex_pdb)
            
            # Add to results
            result['best_pose_pdb'] = best_pose_pdb
            result['complex_pdb'] = complex_pdb
            result['pose_files'] = pose_files
        
        # Analyze interactions (skip if low memory)
        print(json.dumps({'progress': 93, 'message': 'Analyzing interactions...'}), flush=True)
        if 'complex_pdb' in result:
            try:
                interactions = parse_interactions(result['complex_pdb'])
                result['interactions'] = interactions
                
                # Add interaction summary to best pose
                if len(result['poses']) > 0:
                    result['poses'][0]['interactions'] = interactions
            except Exception as e:
                print(f"[Interaction Analysis] Skipped due to error: {str(e)}", file=sys.stderr)
                result['interactions'] = {'error': 'Analysis skipped to save memory'}
        
        # Cleanup before visualization
        gc.collect()
        
        # Generate visualizations (skip if low memory)
        print(json.dumps({'progress': 96, 'message': 'Generating viewer...'}), flush=True)
        if 'complex_pdb' in result:
            try:
                viewer_info = generate_visualizations(result['complex_pdb'], work_dir)
                result['viewer'] = viewer_info
            except Exception as e:
                print(f"[Visualization] Skipped due to error: {str(e)}", file=sys.stderr)
                result['viewer'] = {'error': 'Visualization skipped to save memory'}
        
        # Add grid information to results
        if auto_grid:
            result['grid_detection'] = grid_info
        
        # Final cleanup
        gc.collect()
        
        # Return results
        result['progress'] = 100
        result['message'] = 'Docking completed successfully'
        print(json.dumps(result), flush=True)
        
    except Exception as e:
        import traceback
        error_result = {
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        print(json.dumps(error_result), flush=True)
        print(f"[Error Details] {traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
