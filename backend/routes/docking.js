const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const DockingJob = require('../models/DockingJob');
const Protein = require('../models/Protein');
const Ligand = require('../models/Ligand');
const vinaDocking = require('../utils/vinaDocking');

// Check if Vina is available
let vinaAvailable = false;
let vinaStatus = null;

// Check Vina availability on startup
(async () => {
  try {
    vinaStatus = await vinaDocking.checkVinaAvailability();
    vinaAvailable = vinaStatus.available;
    if (vinaAvailable) {
      console.log('✅ AutoDock Vina is available');
    } else {
      console.log('⚠️  AutoDock Vina not available - using simulation mode');
      if (vinaStatus.missing) {
        console.log('   Missing packages:', vinaStatus.missing.join(', '));
        console.log('   Install with:', vinaStatus.installCommand);
      }
    }
  } catch (error) {
    console.log('⚠️  Could not check Vina availability:', error.message);
  }
})();

// Get Vina status endpoint
router.get('/vina-status', (req, res) => {
  res.json({
    available: vinaAvailable,
    status: vinaStatus
  });
});

// Submit docking job
router.post('/submit', auth, async (req, res) => {
  try {
    console.log('[Docking] Received docking request:', JSON.stringify(req.body, null, 2));
    const { proteinId, ligandId, parameters } = req.body;

    // Validate input IDs
    if (!proteinId || !ligandId) {
      return res.status(400).json({ 
        message: 'Both proteinId and ligandId are required',
        details: { proteinId, ligandId }
      });
    }

    // Validate MongoDB ObjectId format
    const mongoose = require('mongoose');
    if (!mongoose.Types.ObjectId.isValid(proteinId)) {
      return res.status(400).json({ 
        message: 'Invalid protein ID format',
        proteinId 
      });
    }
    if (!mongoose.Types.ObjectId.isValid(ligandId)) {
      return res.status(400).json({ 
        message: 'Invalid ligand ID format',
        ligandId 
      });
    }

    // Log the IDs being searched for
    console.log('[Docking] Looking for protein ID:', proteinId);
    console.log('[Docking] Looking for ligand ID:', ligandId);

    // Verify protein and ligand exist
    const protein = await Protein.findById(proteinId);
    const ligand = await Ligand.findById(ligandId);

    console.log('[Docking] Protein found:', protein ? `${protein.pdbId} (${protein._id})` : 'NOT FOUND');
    console.log('[Docking] Ligand found:', ligand ? `${ligand.name} (${ligand._id})` : 'NOT FOUND');

    if (!protein || !ligand) {
      console.log('[Docking] ❌ Protein or ligand not found');
      console.log('[Docking] Total proteins in DB:', await Protein.countDocuments());
      console.log('[Docking] Total ligands in DB:', await Ligand.countDocuments());
      console.log('[Docking] User proteins:', await Protein.countDocuments({ userId: req.userId }));
      console.log('[Docking] User ligands:', await Ligand.countDocuments({ userId: req.userId }));
      
      // List available IDs for debugging
      const availableProteins = await Protein.find({}, '_id pdbId name').limit(5);
      const availableLigands = await Ligand.find({}, '_id name').limit(5);
      console.log('[Docking] Sample protein IDs:', availableProteins.map(p => `${p._id} (${p.pdbId})`));
      console.log('[Docking] Sample ligand IDs:', availableLigands.map(l => `${l._id} (${l.name})`));
      
      return res.status(404).json({ 
        message: 'Protein or ligand not found in database',
        details: {
          proteinFound: !!protein,
          ligandFound: !!ligand,
          requestedProteinId: proteinId,
          requestedLigandId: ligandId,
          hint: !protein ? 'Protein may have been deleted or does not exist' : 'Ligand may have been deleted or does not exist'
        }
      });
    }

    console.log('[Docking] ✅ Found protein:', protein.pdbId, 'and ligand:', ligand.name);

    // SwissDock-inspired: Extract parameters with defaults
    const dockingParams = {
      gridCenter: parameters?.gridCenter || { x: 0, y: 0, z: 0 },
      gridSize: parameters?.gridSize || { x: 20, y: 20, z: 20 },
      method: parameters?.method || 'vina',
      exhaustivity: parameters?.exhaustivity || 16,  // Increased default for better accuracy
      numPoses: parameters?.numPoses || 9,
    };

    console.log('[Docking] Using parameters:', dockingParams);

    // Calculate estimated time (30 sec per exhaustivity level)
    const estimatedTime = Math.ceil((dockingParams.exhaustivity * dockingParams.numPoses * 30) / 60);

    // Create docking job with enhanced parameters
    const job = new DockingJob({
      userId: req.userId,
      proteinId,
      ligandId,
      status: 'pending',
      parameters: dockingParams,
      estimatedTime,
      progress: 0
    });

    await job.save();
    console.log('[Docking] Job created with ID:', job._id);

    // Process docking asynchronously
    processDockingJob(job, protein, ligand, dockingParams).catch(err => {
      console.error('[Docking] Async processing error:', err);
    });

    res.status(201).json(job);
  } catch (error) {
    console.error('[Docking] Submit error:', error);
    res.status(500).json({ message: 'Failed to submit job', error: error.message });
  }
});

// Async function to process docking job
async function processDockingJob(job, protein, ligand, dockingParams) {
  try {
    console.log('[Docking] Processing job:', job._id);
    job.status = 'running';
    job.progress = 10;
    await job.save();

    let results;

    // Use real Vina if available, otherwise simulate
    if (vinaAvailable && dockingParams.method === 'vina') {
      console.log('[Docking] Running REAL AutoDock Vina');
      
      results = await vinaDocking.runDocking({
        smiles: ligand.smiles,
        pdbContent: protein.structure,
        config: dockingParams,
        jobId: job._id.toString(),
        autoGrid: true  // Enable automatic grid detection
      }, async (progress, message) => {
        // Progress callback - use atomic update instead of save()
        try {
          await DockingJob.findByIdAndUpdate(job._id, { progress });
          console.log(`[Docking] Progress: ${progress}% - ${message}`);
        } catch (err) {
          console.error('Progress update error:', err.message);
        }
      });

      // Process Vina results with enhanced information
      const poses = results.poses.map((pose, idx) => ({
        poseId: pose.poseId,
        clusterId: Math.floor(idx / 3), // Simple clustering
        score: pose.score,
        vinaScore: pose.score,
        rmsd: pose.rmsd_lb || 0,
        pdbFile: pose.pdbFile || '',  // Individual pose PDB file
        coordinates: `POSE_${pose.poseId}`,
        interactions: pose.interactions || vinaDocking.analyzeInteractions(pose)
      }));

      // Create clusters
      const clusters = vinaDocking.clusterPoses(poses, 2.0);

      job.status = 'completed';
      job.progress = 100;
      job.results = {
        bindingAffinity: results.best_affinity,
        gridDetection: results.grid_detection || {},
        files: {
          complexPdb: results.complex_pdb || '',
          bestPosePdb: results.best_pose_pdb || '',
          bestPosePdbqt: results.pose_files && results.pose_files[0] || '',
          allPosesPdbqt: results.output_file || ''
        },
        // Interactive viewer (temporary, auto-expires)
        viewer: results.viewer || {},
        // Store top-level interaction analysis
        interactions: results.interactions || {
          hBonds: [],
          hydrophobic: [],
          piStacking: [],
          ionic: [],
          summary: {}
        },
        poses: poses.sort((a, b) => a.score - b.score),
        clusters,
        bestPose: {
          poseId: poses[0].poseId,
          score: poses[0].score,
          bindingAffinity: results.best_affinity
        },
        method: 'vina-real'
      };
      job.completedAt = new Date();
      await job.save();

      console.log('[Docking] Real Vina completed:', job._id, 'Best affinity:', results.best_affinity);
      if (results.grid_detection) {
        console.log('[Docking] Grid detection method:', results.grid_detection.method);
      }

    } else {
      // SIMULATION MODE
      console.log('[Docking] Running SIMULATED docking (Vina not available or method not vina)');
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      job.progress = 50;
      await job.save();

      await new Promise(resolve => setTimeout(resolve, 2000));
      job.progress = 75;
      await job.save();

      // SwissDock-inspired: Generate clustered poses with interactions
      const baseScore = -6.5 - Math.random() * 3; // Between -6.5 and -9.5 kcal/mol
      const numPoses = dockingParams.numPoses;
      const poses = [];
      const clusters = [];

      // Generate 3 clusters with different binding modes
      for (let clusterId = 0; clusterId < 3; clusterId++) {
        const clusterBaseScore = baseScore + (clusterId * 1.5);
        const posesInCluster = Math.ceil(numPoses / 3);
        
        for (let i = 0; i < posesInCluster && poses.length < numPoses; i++) {
          const poseId = poses.length + 1;
          poses.push({
            poseId,
            clusterId,
            score: clusterBaseScore + (Math.random() * 0.8),
            vinaScore: clusterBaseScore + (Math.random() * 0.5),
            rmsd: Math.random() * 2.5,
            coordinates: `SIMULATED_POSE_${poseId}`,
            interactions: {
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
            }
          });
        }

        clusters.push({
          clusterId,
          memberCount: posesInCluster,
          bestScore: clusterBaseScore,
          representativePose: clusterId * posesInCluster + 1
        });
      }

      // Sort poses by score (lower is better)
      poses.sort((a, b) => a.score - b.score);

      job.status = 'completed';
      job.progress = 100;
      job.results = {
        bindingAffinity: poses[0].score,
        poses,
        clusters,
        bestPose: {
          poseId: poses[0].poseId,
          score: poses[0].score,
          bindingAffinity: poses[0].score
        },
        method: 'simulated'
      };
      job.completedAt = new Date();
      await job.save();

      console.log('[Docking] Simulation completed:', job._id, 'Best score:', poses[0].score);
    }

  } catch (error) {
    console.error('[Docking] Job failed:', error);
    job.status = 'failed';
    job.error = error.message;
    await job.save();
  }
}

// Get job status
router.get('/job/:id', auth, async (req, res) => {
  try {
    const job = await DockingJob.findById(req.params.id)
      .populate('proteinId')
      .populate('ligandId');

    if (!job) {
      return res.status(404).json({ message: 'Job not found' });
    }

    res.json(job);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get all user jobs
router.get('/jobs', auth, async (req, res) => {
  try {
    const jobs = await DockingJob.find({ userId: req.userId })
      .populate('proteinId')
      .populate('ligandId')
      .sort({ createdAt: -1 });

    res.json(jobs);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Serve interactive 3D viewer
router.get('/viewer/:viewerId', async (req, res) => {
  try {
    const { viewerId } = req.params;
    const fs = require('fs');
    const path = require('path');
    
    // Find job with this viewer ID
    const job = await DockingJob.findOne({ 'results.viewer.viewerId': viewerId });
    
    if (!job || !job.results.viewer) {
      return res.status(404).send('<h1>Viewer Not Found</h1><p>This visualization may have expired or does not exist.</p>');
    }
    
    // Check if viewer has expired
    const now = new Date();
    const expiresAt = new Date(job.results.viewer.expiresAt);
    
    if (now > expiresAt) {
      return res.status(410).send('<h1>Viewer Expired</h1><p>This visualization has expired and been removed.</p>');
    }
    
    // Serve the HTML file
    const htmlPath = job.results.viewer.htmlPath;
    
    if (!fs.existsSync(htmlPath)) {
      return res.status(404).send('<h1>Viewer File Not Found</h1><p>The visualization file is missing.</p>');
    }
    
    res.sendFile(path.resolve(htmlPath));
    
  } catch (error) {
    console.error('[Viewer] Error serving viewer:', error);
    res.status(500).send('<h1>Server Error</h1><p>Failed to load visualization.</p>');
  }
});

module.exports = router;
