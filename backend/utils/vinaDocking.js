const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

/**
 * AutoDock Vina Integration Module
 * Executes Python-based Vina docking and returns results
 */

class VinaDocking {
  constructor() {
    this.pythonScript = path.join(__dirname, '..', 'vina_docking.py');
    this.workDir = path.join(__dirname, '..', 'docking_jobs');
  }

  /**
   * Check if Vina is available
   */
  async checkVinaAvailability() {
    return new Promise((resolve) => {
      const python = spawn('python', [this.pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let output = '';

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.on('close', (code) => {
        try {
          const result = JSON.parse(output);
          if (result.status === 'error' && result.missing_packages) {
            resolve({
              available: false,
              missing: result.missing_packages,
              installCommand: result.install_command
            });
          } else {
            resolve({ available: true });
          }
        } catch (e) {
          resolve({ available: false, error: 'Python script error' });
        }
      });

      python.stdin.write(JSON.stringify({ check_only: true }));
      python.stdin.end();
    });
  }

  /**
   * Run AutoDock Vina docking
   * 
   * @param {Object} params - Docking parameters
   * @param {string} params.smiles - Ligand SMILES string
   * @param {string} params.pdbContent - Protein PDB file content
   * @param {Object} params.config - Docking configuration
   * @param {boolean} params.autoGrid - Enable automatic grid detection (default: true)
   * @param {Function} onProgress - Progress callback
   * @returns {Promise<Object>} Docking results
   */
  async runDocking(params, onProgress = null) {
    const { smiles, pdbContent, config, jobId, autoGrid = true } = params;

    // Create job-specific working directory
    const jobWorkDir = path.join(this.workDir, jobId);
    await fs.mkdir(jobWorkDir, { recursive: true });

    return new Promise((resolve, reject) => {
      console.log('[Vina] Starting docking job:', jobId);
      
      const python = spawn('python', [this.pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let outputBuffer = '';
      let stderrOutput = '';
      let lastProgress = 0;

      python.stdout.on('data', (data) => {
        const output = data.toString();
        outputBuffer += output;

        // Parse line-by-line for progress updates
        const lines = outputBuffer.split('\n');
        outputBuffer = lines.pop() || ''; // Keep incomplete line in buffer

        lines.forEach(line => {
          if (line.trim()) {
            try {
              const result = JSON.parse(line);
              
              if (result.progress !== undefined && onProgress) {
                if (result.progress > lastProgress) {
                  lastProgress = result.progress;
                  onProgress(result.progress, result.message);
                }
              }

              if (result.status === 'success') {
                console.log('[Vina] Docking completed successfully');
                resolve(result);
              }
            } catch (e) {
              // Not JSON, might be debug output
              console.log('[Vina]', line);
            }
          }
        });
      });

      python.stderr.on('data', (data) => {
        const stderr = data.toString();
        // Only log if it's not a DeprecationWarning
        if (!stderr.includes('DeprecationWarning')) {
          console.error('[Vina Error]', stderr);
          stderrOutput += stderr;
        }
      });

      python.on('close', (code) => {
        if (code !== 0) {
          console.error('[Vina] Process exited with code:', code);
          console.error('[Vina] Full stderr output:', stderrOutput);
          console.error('[Vina] Full stdout output:', outputBuffer);
          reject(new Error(`Vina docking failed (exit code ${code}). Check logs above for details.`));
        }
      });

      python.on('error', (err) => {
        console.error('[Vina] Process error:', err);
        reject(err);
      });

      // Send input to Python script
      const input = {
        smiles,
        pdb_content: pdbContent,
        config,
        work_dir: jobWorkDir,
        auto_grid: autoGrid  // Pass auto-grid flag to Python
      };

      python.stdin.write(JSON.stringify(input));
      python.stdin.end();
    });
  }

  /**
   * Cluster docking poses based on RMSD
   */
  clusterPoses(poses, rmsdThreshold = 2.0) {
    const clusters = [];
    const assigned = new Set();

    poses.forEach((pose, idx) => {
      if (assigned.has(idx)) return;

      const cluster = {
        clusterId: clusters.length,
        members: [pose],
        bestScore: pose.score,
        representativePose: pose.poseId
      };

      // Find similar poses
      poses.forEach((otherPose, otherIdx) => {
        if (assigned.has(otherIdx) || idx === otherIdx) return;

        const rmsd = otherPose.rmsd_lb || 0;
        if (rmsd <= rmsdThreshold) {
          cluster.members.push(otherPose);
          assigned.add(otherIdx);
        }
      });

      assigned.add(idx);
      clusters.push({
        clusterId: cluster.clusterId,
        memberCount: cluster.members.length,
        bestScore: cluster.bestScore,
        representativePose: cluster.representativePose
      });
    });

    return clusters;
  }

  /**
   * Enhanced interaction analysis
   * (Placeholder - full implementation requires PLIP or ProLIF)
   */
  analyzeInteractions(pose) {
    // This is a simplified version
    // For production, integrate with PLIP or ProLIF Python tools
    return {
      hBonds: [
        { residue: 'ASP25', atom: 'OD1', distance: 2.8 + Math.random() * 0.5 },
        { residue: 'ILE50', atom: 'O', distance: 3.0 + Math.random() * 0.4 }
      ],
      hydrophobic: [
        { residue: 'VAL32', distance: 3.5 + Math.random() * 0.5 },
        { residue: 'LEU76', distance: 3.8 + Math.random() * 0.6 }
      ],
      piStacking: [
        { residue: 'PHE43', distance: 3.6 + Math.random() * 0.4 }
      ],
      ionic: [
        { residue: 'ARG8', distance: 3.2 + Math.random() * 0.5 }
      ]
    };
  }
}

module.exports = new VinaDocking();
