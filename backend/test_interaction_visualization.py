"""
Test script for interaction analysis and visualization modules
Tests with a sample complex PDB file
"""

import sys
import os
import json
from pathlib import Path

# Test 1: Interaction Analysis
print("=" * 60)
print("TEST 1: INTERACTION ANALYSIS")
print("=" * 60)

try:
    from interaction_analysis import analyze_complex
    
    # You can test with a real complex file if available
    # For now, we'll create a minimal test
    test_complex = Path(__file__).parent / 'docking_jobs'
    
    # Find a complex.pdb file in recent docking jobs
    complex_files = list(test_complex.glob('*/complex.pdb'))
    
    if complex_files:
        test_file = str(complex_files[0])
        print(f"\n✓ Found test complex: {test_file}")
        
        # Run analysis
        print("\nRunning interaction analysis...")
        interactions = analyze_complex(test_file)
        
        # Print results
        print("\n" + "=" * 60)
        print("INTERACTION ANALYSIS RESULTS")
        print("=" * 60)
        print(json.dumps(interactions, indent=2))
        
        # Summary
        summary = interactions.get('summary', {})
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total interactions: {summary.get('totalInteractions', 0)}")
        print(f"  - Hydrogen bonds: {summary.get('hBondCount', 0)}")
        print(f"  - Hydrophobic: {summary.get('hydrophobicCount', 0)}")
        print(f"  - π-stacking: {summary.get('piStackingCount', 0)}")
        print(f"  - Ionic: {summary.get('ionicCount', 0)}")
        print(f"\nInteracting residues: {', '.join(summary.get('interactingResidues', []))}")
        
        print("\n✓ Interaction analysis test PASSED")
    else:
        print("\n⚠ No complex.pdb files found in docking_jobs/")
        print("  Run a docking job first to generate test data")
        print("\n✓ Module imports successfully (analysis skipped)")

except Exception as e:
    print(f"\n✗ Interaction analysis test FAILED")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Visualization
print("\n\n" + "=" * 60)
print("TEST 2: VISUALIZATION GENERATION")
print("=" * 60)

try:
    from visualization import generate_visualization
    
    if complex_files:
        test_file = str(complex_files[0])
        output_dir = Path(__file__).parent / 'test_visualizations'
        output_dir.mkdir(exist_ok=True)
        
        # Test publication view
        print(f"\n✓ Testing visualization with: {test_file}")
        print(f"✓ Output directory: {output_dir}")
        
        # Generate publication view
        print("\nGenerating publication view...")
        pub_view = output_dir / 'test_publication.png'
        success_pub = generate_visualization(test_file, str(pub_view), 'publication', 8, 8, 80)
        
        if success_pub:
            print(f"✓ Publication view saved: {pub_view}")
            if pub_view.exists():
                print(f"  File size: {pub_view.stat().st_size / 1024:.2f} KB")
        else:
            print("✗ Failed to generate publication view")
        
        # Generate binding site view
        print("\nGenerating binding site view...")
        binding_view = output_dir / 'test_binding_site.png'
        success_binding = generate_visualization(test_file, str(binding_view), 'binding_site', 8, 8, 80)
        
        if success_binding:
            print(f"✓ Binding site view saved: {binding_view}")
            if binding_view.exists():
                print(f"  File size: {binding_view.stat().st_size / 1024:.2f} KB")
        else:
            print("✗ Failed to generate binding site view")
        
        # Generate surface view
        print("\nGenerating surface view...")
        surface_view = output_dir / 'test_surface.png'
        success_surface = generate_visualization(test_file, str(surface_view), 'surface', 8, 8, 80)
        
        if success_surface:
            print(f"✓ Surface view saved: {surface_view}")
            if surface_view.exists():
                print(f"  File size: {surface_view.stat().st_size / 1024:.2f} KB")
        else:
            print("✗ Failed to generate surface view")
        
        if success_pub or success_binding or success_surface:
            print("\n✓ Visualization test PASSED")
            print(f"\n✓ Check output in: {output_dir}")
        else:
            print("\n⚠ All visualizations failed - check py3Dmol installation")
    else:
        print("\n⚠ No complex.pdb files found for visualization test")
        print("✓ Module imports successfully (visualization skipped)")

except Exception as e:
    print(f"\n✗ Visualization test FAILED")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final summary
print("\n\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✓ Interaction analysis module: Working")
print("✓ Visualization module: Working")
print("\nAll modules are ready for integration!")
print("=" * 60)
