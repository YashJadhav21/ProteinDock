"""
Molecular Visualization Module
Generates interactive 3D visualizations for protein-ligand complexes
Uses py3Dmol to create interactive HTML viewers (no storage needed)
Auto-cleanup after viewing session
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Optional
import uuid
import time
from datetime import datetime, timedelta


class InteractiveMolecularViewer:
    """
    Generate interactive 3D molecular visualizations using py3Dmol
    Creates temporary HTML files that auto-expire
    """
    
    # Store active viewers with expiration times
    _active_viewers = {}
    
    def __init__(self, complex_pdb_path: str):
        """
        Initialize viewer with complex PDB file
        
        Args:
            complex_pdb_path: Path to PDB file containing protein and ligand
        """
        self.complex_pdb = complex_pdb_path
        
        # Read PDB content
        with open(complex_pdb_path, 'r') as f:
            self.pdb_content = f.read()
        
        print(f"[Interactive Viewer] Loaded complex: {complex_pdb_path}", file=sys.stderr)
    
    def generate_interactive_html(self, 
                                  output_html: str,
                                  view_type: str = 'publication',
                                  width: int = 800,
                                  height: int = 600,
                                  expire_minutes: int = 30) -> Dict[str, str]:
        """
        Generate interactive HTML viewer using py3Dmol
        
        Args:
            output_html: Path to save HTML file
            view_type: Type of view ('publication', 'binding_site', 'surface', 'all')
            width: Viewer width in pixels
            height: Viewer height in pixels
            expire_minutes: Minutes before file auto-expires
        
        Returns:
            Dictionary with file path and viewer ID
        """
        try:
            viewer_id = str(uuid.uuid4())
            
            # Generate HTML with embedded py3Dmol viewer
            html_content = self._generate_html_content(view_type, width, height, viewer_id)
            
            # Write HTML file
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Register for auto-cleanup
            expiration = datetime.now() + timedelta(minutes=expire_minutes)
            self._active_viewers[viewer_id] = {
                'file_path': output_html,
                'expiration': expiration,
                'created': datetime.now()
            }
            
            print(f"[Interactive Viewer] Created viewer: {output_html}", file=sys.stderr)
            print(f"[Interactive Viewer] Expires in {expire_minutes} minutes", file=sys.stderr)
            
            return {
                'viewerId': viewer_id,
                'htmlPath': output_html,
                'expiresAt': expiration.isoformat(),
                'urlPath': f'/api/docking/viewer/{viewer_id}'
            }
            
        except Exception as e:
            print(f"[Interactive Viewer Error] {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {}
    
    def _generate_html_content(self, view_type: str, width: int, height: int, viewer_id: str) -> str:
        """
        Generate HTML content with embedded 3D viewer
        
        Args:
            view_type: Type of visualization
            width: Viewer width
            height: Viewer height
            viewer_id: Unique viewer identifier
        
        Returns:
            Complete HTML document as string
        """
        # Escape PDB content for JavaScript
        pdb_escaped = self.pdb_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        
        # Style configuration based on view type
        styles = self._get_view_styles(view_type)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Protein-Ligand Complex Viewer</title>
    <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            width: 100%;
            height: 100vh;
            margin: 0;
            background: white;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 12px 15px;
            text-align: center;
            flex-shrink: 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }}
        .header p {{
            margin: 4px 0 0 0;
            opacity: 0.9;
            font-size: 12px;
        }}
        #viewer {{
            flex: 1;
            width: 100%;
            min-height: 0;
            background: #f5f5f5;
            position: relative;
        }}
        .controls {{
            padding: 12px 15px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            flex-shrink: 0;
            max-height: 40vh;
            overflow-y: auto;
        }}
        .control-group {{
            margin-bottom: 12px;
        }}
        .control-group:last-child {{
            margin-bottom: 0;
        }}
        .control-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
            font-size: 12px;
        }}
        select, button {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        select {{
            width: 100%;
            background: white;
        }}
        select:hover {{
            border-color: #667eea;
        }}
        .button-group {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }}
        button {{
            background: #667eea;
            color: white;
            border: none;
            font-weight: 500;
            width: 100%;
        }}
        button:hover {{
            background: #5568d3;
        }}
        button:active {{
            transform: scale(0.98);
        }}
        .info {{
            padding: 10px 15px;
            background: #e8f4f8;
            border-top: 1px solid #b3dde6;
            font-size: 11px;
            color: #2c5f77;
            flex-shrink: 0;
        }}
        .info strong {{
            color: #1a3d4d;
        }}
        .legend {{
            padding: 12px 15px;
            background: white;
            border-top: 1px solid #e0e0e0;
            flex-shrink: 0;
        }}
        .legend h3 {{
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #333;
        }}
        .legend-items {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #ddd;
        }}
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 14px;
            color: #667eea;
            font-weight: 500;
        }}
        
        /* Desktop styles */
        @media (min-width: 768px) {{
            body {{
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                height: auto;
                min-height: 90vh;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .header h1 {{
                font-size: 24px;
            }}
            .header p {{
                font-size: 14px;
            }}
            #viewer {{
                height: 600px;
            }}
            .controls {{
                padding: 20px 30px;
                max-height: none;
            }}
            .button-group {{
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
            }}
            .legend {{
                padding: 20px 30px;
            }}
            .legend h3 {{
                font-size: 16px;
            }}
            .legend-items {{
                gap: 20px;
            }}
            .legend-item {{
                font-size: 13px;
            }}
            .legend-color {{
                width: 20px;
                height: 20px;
            }}
            .info {{
                font-size: 13px;
                padding: 15px 30px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 Protein-Ligand Complex Viewer</h1>
            <p>Interactive 3D Molecular Visualization</p>
        </div>
        
        <div id="viewer">
            <div class="loading" id="loading">Loading structure...</div>
        </div>
        
        <div class="legend">
            <h3>Color Legend</h3>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color" style="background: #00CED1;"></div>
                    <span>Protein Backbone</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #FFA500;"></div>
                    <span>Ligand</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #90EE90;"></div>
                    <span>Binding Site</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>Visualization Style:</label>
                <select id="styleSelector" onchange="changeStyle()">
                    <option value="publication">Publication Quality</option>
                    <option value="binding_site">Binding Site Focus</option>
                    <option value="surface">Surface View</option>
                    <option value="cartoon">Cartoon (Protein Only)</option>
                    <option value="detailed">Detailed (All Atoms)</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Quick Actions:</label>
                <div class="button-group">
                    <button onclick="resetView()">🔄 Reset View</button>
                    <button onclick="toggleSpin()">🔄 Toggle Spin</button>
                    <button onclick="zoomToLigand()">🔍 Focus Ligand</button>
                    <button onclick="showBindingSite()">🎯 Show Binding Site</button>
                </div>
            </div>
        </div>
        
        <div class="info">
            <strong>💡 Tip:</strong> Click and drag to rotate • Scroll to zoom • Right-click drag to pan
            <br>
            <strong>⏱️ Session expires in 30 minutes</strong> - This visualization will be automatically deleted
        </div>
    </div>

    <script>
        let viewer;
        let spinning = false;
        const pdbData = `{pdb_escaped}`;
        
        // Initialize 3Dmol viewer
        function initViewer() {{
            const element = document.getElementById('viewer');
            const config = {{ backgroundColor: 'white' }};
            viewer = $3Dmol.createViewer(element, config);
            
            // Load PDB structure
            viewer.addModel(pdbData, 'pdb');
            
            // Apply initial style
            applyPublicationStyle();
            
            viewer.zoomTo();
            viewer.render();
            
            // Hide loading message
            document.getElementById('loading').style.display = 'none';
            
            console.log('3Dmol viewer initialized successfully');
        }}
        
        function applyPublicationStyle() {{
            viewer.setStyle({{}}, {{ }});  // Clear all styles
            
            // Protein backbone - cartoon
            viewer.setStyle(
                {{not: {{hetflag: true}}}},
                {{cartoon: {{color: 'cyan', opacity: 0.7}}}}
            );
            
            // Ligand - stick representation
            viewer.setStyle(
                {{hetflag: true}},
                {{stick: {{colorscheme: 'orangeCarbon', radius: 0.3}}}}
            );
            
            viewer.render();
        }}
        
        function applyBindingSiteStyle() {{
            viewer.setStyle({{}}, {{ }});
            
            // Ligand - prominent display
            viewer.setStyle(
                {{hetflag: true}},
                {{stick: {{colorscheme: 'orangeCarbon', radius: 0.4}}, sphere: {{scale: 0.3}}}}
            );
            
            // Nearby residues (within 5Å)
            const ligandAtoms = viewer.selectedAtoms({{hetflag: true}});
            if (ligandAtoms.length > 0) {{
                viewer.setStyle(
                    {{not: {{hetflag: true}}, withinDistance: {{distance: 5, sel: {{hetflag: true}}}}}},
                    {{stick: {{colorscheme: 'greenCarbon', radius: 0.25}}}}
                );
            }}
            
            viewer.zoomTo({{hetflag: true}});
            viewer.render();
        }}
        
        function applySurfaceStyle() {{
            viewer.setStyle({{}}, {{ }});
            
            // Protein surface
            viewer.addSurface(
                $3Dmol.SurfaceType.VDW,
                {{opacity: 0.7, color: 'lightblue'}},
                {{not: {{hetflag: true}}}}
            );
            
            // Ligand as spheres
            viewer.setStyle(
                {{hetflag: true}},
                {{sphere: {{colorscheme: 'orangeCarbon', scale: 0.6}}}}
            );
            
            viewer.render();
        }}
        
        function applyCartoonStyle() {{
            viewer.setStyle({{}}, {{ }});
            
            viewer.setStyle(
                {{not: {{hetflag: true}}}},
                {{cartoon: {{color: 'spectrum'}}}}
            );
            
            viewer.setStyle(
                {{hetflag: true}},
                {{stick: {{colorscheme: 'default'}}}}
            );
            
            viewer.render();
        }}
        
        function applyDetailedStyle() {{
            viewer.setStyle({{}}, {{ }});
            
            // Show all atoms as sticks
            viewer.setStyle(
                {{not: {{hetflag: true}}}},
                {{stick: {{colorscheme: 'chainHetatm', radius: 0.15}}}}
            );
            
            viewer.setStyle(
                {{hetflag: true}},
                {{stick: {{colorscheme: 'orangeCarbon', radius: 0.3}}, sphere: {{scale: 0.25}}}}
            );
            
            viewer.render();
        }}
        
        function changeStyle() {{
            const style = document.getElementById('styleSelector').value;
            
            switch(style) {{
                case 'publication':
                    applyPublicationStyle();
                    break;
                case 'binding_site':
                    applyBindingSiteStyle();
                    break;
                case 'surface':
                    applySurfaceStyle();
                    break;
                case 'cartoon':
                    applyCartoonStyle();
                    break;
                case 'detailed':
                    applyDetailedStyle();
                    break;
            }}
        }}
        
        function resetView() {{
            viewer.zoomTo();
            viewer.render();
        }}
        
        function toggleSpin() {{
            spinning = !spinning;
            if (spinning) {{
                viewer.spin(true);
            }} else {{
                viewer.spin(false);
            }}
        }}
        
        function zoomToLigand() {{
            viewer.zoomTo({{hetflag: true}});
            viewer.render();
        }}
        
        function showBindingSite() {{
            document.getElementById('styleSelector').value = 'binding_site';
            applyBindingSiteStyle();
        }}
        
        // Initialize when page loads
        window.addEventListener('load', initViewer);
    </script>
</body>
</html>"""
        
        return html
    
    def _get_view_styles(self, view_type: str) -> Dict:
        """
        Get style configuration for different view types
        
        Args:
            view_type: Type of view
        
        Returns:
            Dictionary with style parameters
        """
        styles = {
            'publication': {
                'protein': 'cartoon',
                'ligand': 'stick',
                'colors': {'protein': 'cyan', 'ligand': 'orange'}
            },
            'binding_site': {
                'protein': 'stick',
                'ligand': 'stick+sphere',
                'show_nearby': True,
                'distance': 5.0
            },
            'surface': {
                'protein': 'surface',
                'ligand': 'sphere',
                'surface_opacity': 0.7
            },
            'all': {
                'include_all': True
            }
        }
        
        return styles.get(view_type, styles['publication'])
    
    @classmethod
    def cleanup_expired_viewers(cls):
        """
        Clean up expired viewer files
        Should be called periodically
        """
        now = datetime.now()
        expired_ids = []
        
        for viewer_id, info in cls._active_viewers.items():
            if now > info['expiration']:
                try:
                    file_path = Path(info['file_path'])
                    if file_path.exists():
                        file_path.unlink()
                        print(f"[Cleanup] Deleted expired viewer: {file_path}", file=sys.stderr)
                    expired_ids.append(viewer_id)
                except Exception as e:
                    print(f"[Cleanup Error] {str(e)}", file=sys.stderr)
        
        # Remove from tracking
        for viewer_id in expired_ids:
            del cls._active_viewers[viewer_id]
        
        if expired_ids:
            print(f"[Cleanup] Removed {len(expired_ids)} expired viewers", file=sys.stderr)
    
    @classmethod
    def force_cleanup(cls, viewer_id: str):
        """
        Force cleanup of a specific viewer
        
        Args:
            viewer_id: ID of viewer to cleanup
        """
        if viewer_id in cls._active_viewers:
            info = cls._active_viewers[viewer_id]
            try:
                file_path = Path(info['file_path'])
                if file_path.exists():
                    file_path.unlink()
                    print(f"[Force Cleanup] Deleted viewer: {file_path}", file=sys.stderr)
                del cls._active_viewers[viewer_id]
            except Exception as e:
                print(f"[Force Cleanup Error] {str(e)}", file=sys.stderr)


def generate_interactive_viewer(complex_pdb_path: str, 
                                output_dir: str,
                                view_type: str = 'publication',
                                expire_minutes: int = 30) -> Dict[str, str]:
    """
    Standalone function to generate interactive viewer
    
    Args:
        complex_pdb_path: Path to complex PDB file
        output_dir: Directory to save HTML file
        view_type: Type of view
        expire_minutes: Minutes before auto-expiration
    
    Returns:
        Dictionary with viewer information
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        viewer = InteractiveMolecularViewer(complex_pdb_path)
        viewer_id = str(uuid.uuid4())
        output_html = os.path.join(output_dir, f'viewer_{viewer_id}.html')
        
        result = viewer.generate_interactive_html(
            output_html, 
            view_type=view_type,
            expire_minutes=expire_minutes
        )
        
        return result
    
    except Exception as e:
        print(f"[Interactive Viewer Error] {str(e)}", file=sys.stderr)
        return {}


if __name__ == '__main__':
    # For standalone testing
    if len(sys.argv) > 2:
        complex_file = sys.argv[1]
        output_dir = sys.argv[2]
        
        result = generate_interactive_viewer(complex_file, output_dir)
        print(json.dumps(result, indent=2))
