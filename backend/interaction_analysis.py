"""
Molecular Interaction Analysis Module
Analyzes protein-ligand interactions without requiring PLIP/OpenBabel
Uses BioPython and geometric calculations
"""

import sys
import numpy as np
from Bio.PDB import PDBParser, Selection
from typing import Dict, List, Tuple
import math


class InteractionAnalyzer:
    """
    Analyze protein-ligand interactions using distance-based methods
    """
    
    # Van der Waals radii (Angstroms)
    VDW_RADII = {
        'H': 1.20, 'C': 1.70, 'N': 1.55, 'O': 1.52, 'F': 1.47,
        'P': 1.80, 'S': 1.80, 'CL': 1.75, 'BR': 1.85, 'I': 1.98
    }
    
    # Interaction cutoff distances (Angstroms)
    HBOND_DISTANCE = 3.5
    HYDROPHOBIC_DISTANCE = 4.0
    PI_STACKING_DISTANCE = 6.0
    IONIC_DISTANCE = 4.0
    
    # Amino acid properties
    HYDROPHOBIC_RESIDUES = {'ALA', 'VAL', 'ILE', 'LEU', 'MET', 'PHE', 'TRP', 'PRO'}
    AROMATIC_RESIDUES = {'PHE', 'TYR', 'TRP', 'HIS'}
    POSITIVE_RESIDUES = {'ARG', 'LYS', 'HIS'}
    NEGATIVE_RESIDUES = {'ASP', 'GLU'}
    
    # Hydrogen bond donor/acceptor atoms
    HBOND_DONORS = {'N', 'O'}  # Can donate H
    HBOND_ACCEPTORS = {'N', 'O', 'S'}  # Can accept H
    
    def __init__(self, complex_pdb_path: str):
        """
        Initialize analyzer with protein-ligand complex
        
        Args:
            complex_pdb_path: Path to PDB file containing protein and ligand
        """
        self.parser = PDBParser(QUIET=True)
        self.structure = self.parser.get_structure('complex', complex_pdb_path)
        
        # Separate protein and ligand
        self.protein_atoms = []
        self.ligand_atoms = []
        
        for model in self.structure:
            for chain in model:
                for residue in chain:
                    atoms = list(residue.get_atoms())
                    # HETATM records are typically ligands
                    if residue.id[0].strip() == '':  # Standard amino acids
                        self.protein_atoms.extend(atoms)
                    else:  # HETATM
                        self.ligand_atoms.extend(atoms)
        
        print(f"[Interaction Analysis] Protein atoms: {len(self.protein_atoms)}", file=sys.stderr)
        print(f"[Interaction Analysis] Ligand atoms: {len(self.ligand_atoms)}", file=sys.stderr)
    
    def distance(self, atom1, atom2) -> float:
        """Calculate Euclidean distance between two atoms"""
        return np.linalg.norm(atom1.coord - atom2.coord)
    
    def get_residue_name(self, atom) -> str:
        """Get residue name and number as string"""
        residue = atom.get_parent()
        return f"{residue.resname}{residue.id[1]}"
    
    def is_hydrogen_bond(self, atom1, atom2, distance: float) -> bool:
        """
        Check if two atoms can form hydrogen bond
        
        Criteria:
        - Distance < 3.5 Å
        - One donor (N, O with H) and one acceptor (N, O, S)
        """
        if distance > self.HBOND_DISTANCE:
            return False
        
        # Get element types (first character of atom name, usually)
        elem1 = atom1.element.strip().upper()
        elem2 = atom2.element.strip().upper()
        
        # Both should be potential H-bond atoms
        hbond_atoms = {'N', 'O', 'S'}
        if elem1 in hbond_atoms and elem2 in hbond_atoms:
            return True
        
        return False
    
    def is_hydrophobic_interaction(self, res_atom, lig_atom, distance: float) -> bool:
        """
        Check for hydrophobic interaction
        
        Criteria:
        - Distance < 4.0 Å
        - Both atoms are carbon
        - Residue is hydrophobic
        """
        if distance > self.HYDROPHOBIC_DISTANCE:
            return False
        
        residue = res_atom.get_parent()
        elem_res = res_atom.element.strip().upper()
        elem_lig = lig_atom.element.strip().upper()
        
        # Both should be carbon atoms
        if elem_res == 'C' and elem_lig == 'C':
            # Residue should be hydrophobic
            if residue.resname in self.HYDROPHOBIC_RESIDUES:
                return True
        
        return False
    
    def is_pi_stacking(self, res_atom, lig_atom, distance: float) -> bool:
        """
        Simplified π-π stacking detection
        
        Criteria:
        - Distance < 6.0 Å
        - Residue is aromatic
        - Ligand atom is carbon (proxy for aromatic)
        """
        if distance > self.PI_STACKING_DISTANCE:
            return False
        
        residue = res_atom.get_parent()
        elem_lig = lig_atom.element.strip().upper()
        
        if residue.resname in self.AROMATIC_RESIDUES and elem_lig == 'C':
            return True
        
        return False
    
    def is_ionic_interaction(self, res_atom, lig_atom, distance: float) -> bool:
        """
        Check for ionic/salt bridge
        
        Criteria:
        - Distance < 4.0 Å
        - Charged residue (ARG, LYS, ASP, GLU)
        - Opposite charges on ligand atoms (N for positive, O for negative)
        """
        if distance > self.IONIC_DISTANCE:
            return False
        
        residue = res_atom.get_parent()
        elem_res = res_atom.element.strip().upper()
        elem_lig = lig_atom.element.strip().upper()
        
        # Positive residue + negatively charged ligand atom
        if residue.resname in self.POSITIVE_RESIDUES and elem_lig == 'O':
            return True
        
        # Negative residue + positively charged ligand atom
        if residue.resname in self.NEGATIVE_RESIDUES and elem_lig == 'N':
            return True
        
        return False
    
    def analyze(self) -> Dict:
        """
        Perform complete interaction analysis
        
        Returns:
            Dictionary with interaction types and details
        """
        interactions = {
            'hBonds': [],
            'hydrophobic': [],
            'piStacking': [],
            'ionic': [],
            'summary': {}
        }
        
        # Track unique residues for summary
        interacting_residues = set()
        
        # Analyze each ligand atom against all protein atoms
        for lig_atom in self.ligand_atoms:
            for prot_atom in self.protein_atoms:
                distance = self.distance(lig_atom, prot_atom)
                
                # Skip if too far
                if distance > 6.0:
                    continue
                
                residue_name = self.get_residue_name(prot_atom)
                interacting_residues.add(residue_name)
                
                # Check hydrogen bond
                if self.is_hydrogen_bond(prot_atom, lig_atom, distance):
                    interactions['hBonds'].append({
                        'residue': residue_name,
                        'proteinAtom': prot_atom.name,
                        'ligandAtom': lig_atom.name,
                        'distance': float(round(distance, 2))  # Convert to Python float
                    })
                
                # Check hydrophobic interaction
                elif self.is_hydrophobic_interaction(prot_atom, lig_atom, distance):
                    interactions['hydrophobic'].append({
                        'residue': residue_name,
                        'proteinAtom': prot_atom.name,
                        'ligandAtom': lig_atom.name,
                        'distance': float(round(distance, 2))  # Convert to Python float
                    })
                
                # Check π-π stacking
                elif self.is_pi_stacking(prot_atom, lig_atom, distance):
                    interactions['piStacking'].append({
                        'residue': residue_name,
                        'proteinAtom': prot_atom.name,
                        'ligandAtom': lig_atom.name,
                        'distance': float(round(distance, 2))  # Convert to Python float
                    })
                
                # Check ionic interaction
                elif self.is_ionic_interaction(prot_atom, lig_atom, distance):
                    interactions['ionic'].append({
                        'residue': residue_name,
                        'proteinAtom': prot_atom.name,
                        'ligandAtom': lig_atom.name,
                        'distance': float(round(distance, 2))  # Convert to Python float
                    })
        
        # Remove duplicates and summarize
        interactions['hBonds'] = self._deduplicate_interactions(interactions['hBonds'])
        interactions['hydrophobic'] = self._deduplicate_interactions(interactions['hydrophobic'])
        interactions['piStacking'] = self._deduplicate_interactions(interactions['piStacking'])
        interactions['ionic'] = self._deduplicate_interactions(interactions['ionic'])
        
        # Summary statistics
        interactions['summary'] = {
            'totalInteractions': (
                len(interactions['hBonds']) +
                len(interactions['hydrophobic']) +
                len(interactions['piStacking']) +
                len(interactions['ionic'])
            ),
            'hBondCount': len(interactions['hBonds']),
            'hydrophobicCount': len(interactions['hydrophobic']),
            'piStackingCount': len(interactions['piStacking']),
            'ionicCount': len(interactions['ionic']),
            'interactingResidues': sorted(list(interacting_residues))
        }
        
        print(f"[Interaction Analysis] Found {interactions['summary']['totalInteractions']} interactions", file=sys.stderr)
        print(f"[Interaction Analysis] H-bonds: {interactions['summary']['hBondCount']}", file=sys.stderr)
        print(f"[Interaction Analysis] Hydrophobic: {interactions['summary']['hydrophobicCount']}", file=sys.stderr)
        print(f"[Interaction Analysis] π-stacking: {interactions['summary']['piStackingCount']}", file=sys.stderr)
        print(f"[Interaction Analysis] Ionic: {interactions['summary']['ionicCount']}", file=sys.stderr)
        
        return interactions
    
    def _deduplicate_interactions(self, interaction_list: List[Dict]) -> List[Dict]:
        """
        Remove duplicate interactions (keep shortest distance)
        """
        unique = {}
        for interaction in interaction_list:
            key = (interaction['residue'], interaction['ligandAtom'])
            if key not in unique or interaction['distance'] < unique[key]['distance']:
                unique[key] = interaction
        
        return sorted(list(unique.values()), key=lambda x: x['distance'])


def analyze_complex(complex_pdb_path: str) -> Dict:
    """
    Standalone function to analyze protein-ligand complex
    
    Args:
        complex_pdb_path: Path to PDB file with protein and ligand
    
    Returns:
        Dictionary with interaction details
    """
    try:
        analyzer = InteractionAnalyzer(complex_pdb_path)
        return analyzer.analyze()
    except Exception as e:
        print(f"[Interaction Analysis Error] {str(e)}", file=sys.stderr)
        return {
            'hBonds': [],
            'hydrophobic': [],
            'piStacking': [],
            'ionic': [],
            'summary': {'error': str(e)}
        }


if __name__ == '__main__':
    # For standalone testing
    import sys
    if len(sys.argv) > 1:
        complex_file = sys.argv[1]
        interactions = analyze_complex(complex_file)
        import json
        print(json.dumps(interactions, indent=2))
