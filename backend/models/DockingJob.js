const mongoose = require('mongoose');

const dockingJobSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  proteinId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Protein',
    required: true
  },
  ligandId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Ligand',
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'running', 'completed', 'failed'],
    default: 'pending'
  },
  // SwissDock-inspired: Docking parameters
  parameters: {
    // Search space definition (grid box)
    gridCenter: {
      x: { type: Number, default: 0 },
      y: { type: Number, default: 0 },
      z: { type: Number, default: 0 }
    },
    gridSize: {
      x: { type: Number, default: 20 },
      y: { type: Number, default: 20 },
      z: { type: Number, default: 20 }
    },
    // Docking method
    method: {
      type: String,
      enum: ['vina', 'attracting-cavities'],
      default: 'vina'
    },
    // Exhaustivity parameter (1-64)
    exhaustivity: {
      type: Number,
      default: 8
    },
    // Number of poses to generate
    numPoses: {
      type: Number,
      default: 9
    }
  },
  // SwissDock-inspired: Enhanced results with clustering
  results: {
    bindingAffinity: Number,
    // Grid detection information
    gridDetection: {
      method: String,
      confidence: String,
      center: {
        x: Number,
        y: Number,
        z: Number
      },
      size: {
        x: Number,
        y: Number,
        z: Number
      }
    },
    // Generated files
    files: {
      complexPdb: String,              // Protein-ligand complex
      bestPosePdb: String,             // Best scoring pose (PDB)
      bestPosePdbqt: String,           // Best scoring pose (PDBQT)
      allPosesPdbqt: String            // All poses in one file
    },
    // Interactive 3D viewer information (auto-expires, not stored)
    viewer: {
      viewerId: String,                // Unique viewer ID
      htmlPath: String,                // Temporary HTML path
      expiresAt: Date,                 // Auto-cleanup timestamp
      urlPath: String                  // API endpoint to access viewer
    },
    // Interaction analysis results
    interactions: {
      hBonds: [{
        residue: String,
        proteinAtom: String,
        ligandAtom: String,
        distance: Number
      }],
      hydrophobic: [{
        residue: String,
        proteinAtom: String,
        ligandAtom: String,
        distance: Number
      }],
      piStacking: [{
        residue: String,
        proteinAtom: String,
        ligandAtom: String,
        distance: Number
      }],
      ionic: [{
        residue: String,
        proteinAtom: String,
        ligandAtom: String,
        distance: Number
      }],
      summary: {
        totalInteractions: Number,
        hBondCount: Number,
        hydrophobicCount: Number,
        piStackingCount: Number,
        ionicCount: Number,
        interactingResidues: [String]
      }
    },
    poses: [{
      poseId: Number,
      clusterId: Number,
      score: Number,
      rmsd: Number,
      pdbFile: String,            // Individual pose PDB file
      coordinates: String,
      interactions: {
        hBonds: [{ residue: String, proteinAtom: String, ligandAtom: String, distance: Number }],
        hydrophobic: [{ residue: String, proteinAtom: String, ligandAtom: String, distance: Number }],
        piStacking: [{ residue: String, proteinAtom: String, ligandAtom: String, distance: Number }],
        ionic: [{ residue: String, proteinAtom: String, ligandAtom: String, distance: Number }]
      }
    }],
    clusters: [{
      clusterId: Number,
      memberCount: Number,
      bestScore: Number,
      representativePose: Number
    }]
  },
  // Progress tracking
  progress: {
    type: Number,
    default: 0
  },
  estimatedTime: {
    type: Number,
    default: 0
  },
  error: String,
  createdAt: {
    type: Date,
    default: Date.now
  },
  completedAt: Date
});

module.exports = mongoose.model('DockingJob', dockingJobSchema);
