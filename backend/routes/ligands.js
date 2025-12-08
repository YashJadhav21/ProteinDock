const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Ligand = require('../models/Ligand');

// Get all user ligands
router.get('/', auth, async (req, res) => {
  try {
    const ligands = await Ligand.find({ userId: req.userId }).sort({ createdAt: -1 });
    res.json(ligands);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Create ligand
router.post('/', auth, async (req, res) => {
  try {
    const { name, smiles, formula, structure, inputFormat, pdbFile } = req.body;

    // Check if ligand with same name and SMILES already exists for this user
    const existingLigand = await Ligand.findOne({ 
      userId: req.userId,
      $or: [
        { name: name, smiles: smiles },
        { name: name, inputFormat: 'smiles', smiles: smiles }
      ]
    });
    
    if (existingLigand) {
      console.log(`[Ligand] Found existing ligand: ${name} (ID: ${existingLigand._id})`);
      return res.status(200).json({
        ...existingLigand.toObject(),
        message: 'Ligand with this name and SMILES already exists',
        isExisting: true
      });
    }

    const ligand = new Ligand({
      name,
      smiles,
      formula,
      structure,
      inputFormat: inputFormat || 'smiles',
      pdbFile,
      userId: req.userId
    });

    await ligand.save();
    console.log(`[Ligand] Created new ligand: ${name} (ID: ${ligand._id})`);
    res.status(201).json({
      ...ligand.toObject(),
      message: 'Ligand created successfully',
      isExisting: false
    });
  } catch (error) {
    console.error(`[Ligand] Error creating ligand:`, error.message);
    res.status(500).json({ message: 'Failed to create ligand', error: error.message });
  }
});

// Get ligand by ID
router.get('/:id', auth, async (req, res) => {
  try {
    const ligand = await Ligand.findById(req.params.id);
    if (!ligand) {
      return res.status(404).json({ message: 'Ligand not found' });
    }
    res.json(ligand);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Search PubChem (simplified)
router.get('/pubchem/search', auth, async (req, res) => {
  try {
    const { query } = req.query;
    // In production, integrate with PubChem API
    res.json({ message: 'PubChem integration coming soon', query });
  } catch (error) {
    res.status(500).json({ message: 'Search failed', error: error.message });
  }
});

// TEMPORARY: Fix Ritonavir SMILES (no auth required for quick fix)
router.post('/fix-ritonavir-temp', async (req, res) => {
  try {
    const CORRECT_SMILES = 'CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C';
    
    const ligand = await Ligand.findOne({ name: /ritonavir/i });
    
    if (!ligand) {
      return res.status(404).json({ message: 'Ritonavir not found in database' });
    }
    
    const oldSmiles = ligand.smiles;
    const oldLength = oldSmiles.length;
    
    console.log(`[Fix] Found Ritonavir ID: ${ligand._id}`);
    console.log(`[Fix] Current SMILES length: ${oldLength}`);
    
    ligand.smiles = CORRECT_SMILES;
    await ligand.save();
    
    console.log(`[Fix] ✅ Updated to correct SMILES (${CORRECT_SMILES.length} chars)`);
    
    res.json({
      success: true,
      message: 'Ritonavir SMILES fixed successfully!',
      oldSmiles: oldSmiles,
      newSmiles: CORRECT_SMILES,
      oldLength: oldLength,
      newLength: CORRECT_SMILES.length
    });
  } catch (error) {
    console.error('[Fix] Error:', error);
    res.status(500).json({ message: 'Failed to fix Ritonavir', error: error.message });
  }
});

// TEMPORARY: Fix Ritonavir SMILES
router.post('/fix-ritonavir', auth, async (req, res) => {
  try {
    const CORRECT_SMILES = 'CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C';
    
    const ligand = await Ligand.findOne({ name: /ritonavir/i });
    
    if (!ligand) {
      return res.status(404).json({ message: 'Ritonavir not found' });
    }
    
    console.log(`[Fix] Current SMILES length: ${ligand.smiles.length}`);
    console.log(`[Fix] Current SMILES: ${ligand.smiles}`);
    
    ligand.smiles = CORRECT_SMILES;
    await ligand.save();
    
    console.log(`[Fix] ✅ Updated to correct SMILES (${CORRECT_SMILES.length} chars)`);
    
    res.json({
      message: 'Ritonavir SMILES fixed successfully',
      oldLength: ligand.smiles.length,
      newLength: CORRECT_SMILES.length,
      ligand: ligand
    });
  } catch (error) {
    console.error('[Fix] Error:', error);
    res.status(500).json({ message: 'Failed to fix Ritonavir', error: error.message });
  }
});

module.exports = router;
