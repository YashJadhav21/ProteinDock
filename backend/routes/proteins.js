const express = require('express');
const router = express.Router();
const axios = require('axios');
const auth = require('../middleware/auth');
const Protein = require('../models/Protein');

// Search RCSB PDB
router.get('/search', auth, async (req, res) => {
  try {
    const { query } = req.query;
    
    // Simple search - in production, use RCSB API
    const proteins = await Protein.find({
      $or: [
        { pdbId: new RegExp(query, 'i') },
        { name: new RegExp(query, 'i') }
      ]
    }).limit(20);

    res.json(proteins);
  } catch (error) {
    res.status(500).json({ message: 'Search failed', error: error.message });
  }
});

// Get protein by ID
router.get('/:id', auth, async (req, res) => {
  try {
    const protein = await Protein.findById(req.params.id);
    if (!protein) {
      return res.status(404).json({ message: 'Protein not found' });
    }
    res.json(protein);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Upload custom protein
router.post('/upload', auth, async (req, res) => {
  try {
    const { pdbId, name, organism, structure } = req.body;

    // Check if protein with same PDB ID already exists
    const existingProtein = await Protein.findOne({ pdbId: pdbId.toUpperCase() });
    
    if (existingProtein) {
      return res.status(200).json({
        protein: existingProtein,
        message: 'Protein with this PDB ID already exists',
        isExisting: true
      });
    }

    const protein = new Protein({
      pdbId: pdbId.toUpperCase(),
      name,
      organism,
      structure,
      userId: req.userId
    });

    await protein.save();
    res.status(201).json({ protein, isExisting: false });
  } catch (error) {
    res.status(500).json({ message: 'Upload failed', error: error.message });
  }
});

// Fetch from RCSB PDB
router.post('/fetch/:pdbId', auth, async (req, res) => {
  try {
    const { pdbId } = req.params;
    const pdbIdUpper = pdbId.toUpperCase();
    
    // Check if already in database
    let protein = await Protein.findOne({ pdbId: pdbIdUpper });
    if (protein) {
      console.log(`[Protein] Found existing protein: ${pdbIdUpper} (ID: ${protein._id})`);
      return res.json({
        ...protein.toObject(),
        message: 'Protein already exists in database',
        isExisting: true
      });
    }

    // Fetch from RCSB
    console.log(`[Protein] Fetching ${pdbIdUpper} from RCSB PDB...`);
    const response = await axios.get(`https://files.rcsb.org/download/${pdbIdUpper}.pdb`);
    
    protein = new Protein({
      pdbId: pdbIdUpper,
      name: pdbIdUpper,
      structure: response.data,
      userId: req.userId
    });

    await protein.save();
    console.log(`[Protein] Created new protein: ${pdbIdUpper} (ID: ${protein._id})`);
    res.status(201).json({
      ...protein.toObject(),
      message: 'Protein fetched and saved successfully',
      isExisting: false
    });
  } catch (error) {
    console.error(`[Protein] Error fetching ${pdbId}:`, error.message);
    res.status(500).json({ message: 'Failed to fetch protein', error: error.message });
  }
});

// Get grid box suggestion for a protein
router.post('/grid-suggestion/:proteinId', auth, async (req, res) => {
  try {
    const { proteinId } = req.params;
    const protein = await Protein.findById(proteinId);
    
    if (!protein) {
      return res.status(404).json({ message: 'Protein not found' });
    }

    // Call Python script to detect binding site
    const { spawn } = require('child_process');
    const fs = require('fs');
    const path = require('path');
    
    // Write protein structure to temp file
    const tempDir = path.join(__dirname, '../docking_temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    const tempPdbFile = path.join(tempDir, `temp_${proteinId}.pdb`);
    fs.writeFileSync(tempPdbFile, protein.structure);
    
    // Run Python script to detect grid
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../detect_grid.py'),
      tempPdbFile
    ]);
    
    let output = '';
    let errorOutput = '';
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      // Clean up temp file
      try {
        fs.unlinkSync(tempPdbFile);
      } catch (err) {
        console.error('Failed to delete temp file:', err);
      }
      
      if (code !== 0) {
        console.error('[Grid Detection] Error:', errorOutput);
        // Return default grid centered at origin
        return res.json({
          gridCenter: { x: 0, y: 0, z: 0 },
          gridSize: { x: 25, y: 25, z: 25 },
          method: 'default',
          message: 'Using default grid (could not detect binding site)'
        });
      }
      
      try {
        const result = JSON.parse(output);
        res.json({
          gridCenter: result.center,
          gridSize: result.size,
          method: result.method,
          message: result.message
        });
      } catch (err) {
        console.error('[Grid Detection] Parse error:', err);
        res.json({
          gridCenter: { x: 0, y: 0, z: 0 },
          gridSize: { x: 25, y: 25, z: 25 },
          method: 'default',
          message: 'Using default grid'
        });
      }
    });
  } catch (error) {
    console.error('[Grid Suggestion] Error:', error);
    res.status(500).json({ message: 'Failed to get grid suggestion', error: error.message });
  }
});

module.exports = router;
