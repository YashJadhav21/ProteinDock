#!/usr/bin/env python3
"""
Quick grid detection script for API endpoint
Returns JSON with grid center and size
"""
import sys
import json
from Bio.PDB import PDBParser, PDBIO
import numpy as np

def detect_grid_box(pdb_file):
    """Detect grid box for protein structure"""
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', pdb_file)
        
        # Get all heavy atoms (non-hydrogen)
        coords = []
        het_coords = []  # Heteroatoms (potential ligands)
        
        for model in structure:
            for chain in model:
                for residue in chain:
                    # Check if heteroatom (potential co-crystallized ligand)
                    is_het = residue.id[0] != ' '
                    
                    for atom in residue:
                        if atom.element != 'H':  # Skip hydrogens
                            coord = atom.get_coord()
                            coords.append(coord)
                            if is_het:
                                het_coords.append(coord)
        
        if len(het_coords) > 5:
            # Use co-crystallized ligand location
            coords_array = np.array(het_coords)
            center = coords_array.mean(axis=0)
            
            # Calculate size with padding
            min_coords = coords_array.min(axis=0)
            max_coords = coords_array.max(axis=0)
            size = max_coords - min_coords + 10  # Add 10Å padding
            
            # Ensure minimum size of 15Å
            size = np.maximum(size, 15)
            # Cap maximum at 30Å
            size = np.minimum(size, 30)
            
            result = {
                'center': {
                    'x': round(float(center[0]), 2),
                    'y': round(float(center[1]), 2),
                    'z': round(float(center[2]), 2)
                },
                'size': {
                    'x': round(float(size[0]), 2),
                    'y': round(float(size[1]), 2),
                    'z': round(float(size[2]), 2)
                },
                'method': 'ligand-based',
                'message': f'Grid detected from co-crystallized ligand ({len(het_coords)} atoms)'
            }
        else:
            # Use center of mass of protein
            coords_array = np.array(coords)
            center = coords_array.mean(axis=0)
            
            result = {
                'center': {
                    'x': round(float(center[0]), 2),
                    'y': round(float(center[1]), 2),
                    'z': round(float(center[2]), 2)
                },
                'size': {
                    'x': 25,
                    'y': 25,
                    'z': 25
                },
                'method': 'center-of-mass',
                'message': f'Grid centered at protein center of mass ({len(coords)} atoms)'
            }
        
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        # Return default on error
        result = {
            'center': {'x': 0, 'y': 0, 'z': 0},
            'size': {'x': 25, 'y': 25, 'z': 25},
            'method': 'default',
            'message': f'Error: {str(e)}'
        }
        print(json.dumps(result))
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({
            'center': {'x': 0, 'y': 0, 'z': 0},
            'size': {'x': 25, 'y': 25, 'z': 25},
            'method': 'default',
            'message': 'No PDB file provided'
        }))
        sys.exit(1)
    
    pdb_file = sys.argv[1]
    sys.exit(detect_grid_box(pdb_file))
