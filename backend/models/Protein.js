const mongoose = require('mongoose');

const proteinSchema = new mongoose.Schema({
  pdbId: {
    type: String,
    required: true,
    uppercase: true,
    index: true,  // Add index for faster queries
    trim: true
  },
  name: {
    type: String,
    required: true
  },
  organism: String,
  resolution: Number,
  structure: {
    type: String, // PDB file content
    required: true
  },
  // SwissDock-inspired: Chain selection
  selectedChains: {
    type: [String],
    default: []
  },
  availableChains: {
    type: [String],
    default: []
  },
  // SwissDock-inspired: Heteroatoms to keep
  heteroatoms: {
    type: [String],
    default: []
  },
  // Protein metadata
  method: {
    type: String,
    default: ''
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Compound index: Same PDB ID can exist for different users or only once globally
// For global uniqueness (recommended for PDB IDs):
proteinSchema.index({ pdbId: 1 }, { unique: true });

module.exports = mongoose.model('Protein', proteinSchema);
