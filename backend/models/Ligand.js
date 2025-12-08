const mongoose = require('mongoose');

const ligandSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  // Input format: SMILES or PDB
  inputFormat: {
    type: String,
    enum: ['smiles', 'pdb'],
    default: 'smiles'
  },
  smiles: {
    type: String,
    required: function() {
      return this.inputFormat === 'smiles';
    },
    trim: true
  },
  pdbFile: {
    type: String,  // PDB file content
    required: function() {
      return this.inputFormat === 'pdb';
    }
  },
  formula: String,
  structure: String, // MOL/SDF format
  // SwissDock-inspired: Molecular properties
  properties: {
    molecularWeight: { type: Number, default: 0 },
    logP: { type: Number, default: 0 },
    hBondDonors: { type: Number, default: 0 },
    hBondAcceptors: { type: Number, default: 0 },
    rotatableBonds: { type: Number, default: 0 },
    tpsa: { type: Number, default: 0 }
  },
  // Preparation status
  prepared: {
    type: Boolean,
    default: false
  },
  // Prepared PDBQT file (cached)
  pdbqtFile: {
    type: String
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Compound index: Prevent duplicate ligands per user (same name + SMILES)
ligandSchema.index({ userId: 1, name: 1, smiles: 1 }, { unique: true, sparse: true });

// Regular index for faster queries
ligandSchema.index({ userId: 1, createdAt: -1 });

module.exports = mongoose.model('Ligand', ligandSchema);
