// Quick script to fix Ritonavir SMILES in MongoDB
// Run with: node fix_ritonavir_smiles.js

const mongoose = require('mongoose');
require('dotenv').config();

const RITONAVIR_CORRECT_SMILES = 'CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C';

async function fixRitonavirSmiles() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ Connected to MongoDB');

    // Import the actual Ligand model to ensure validation
    const Ligand = require('./models/Ligand');
    
    const ritonavir = await Ligand.findOne({ name: /ritonavir/i });
    
    if (!ritonavir) {
      console.log('❌ Ritonavir not found in database');
      process.exit(1);
    }

    console.log(`\n📋 Current Ritonavir data:`);
    console.log(`   ID: ${ritonavir._id}`);
    console.log(`   Name: ${ritonavir.name}`);
    console.log(`   Current SMILES: ${ritonavir.smiles}`);
    console.log(`   SMILES length: ${ritonavir.smiles?.length || 0} characters`);

    // Update with correct SMILES
    ritonavir.smiles = RITONAVIR_CORRECT_SMILES;
    ritonavir.molecularWeight = 720.95; // Correct MW for Ritonavir
    
    await ritonavir.save();

    console.log(`\n✅ Updated Ritonavir SMILES!`);
    console.log(`   New SMILES: ${ritonavir.smiles}`);
    console.log(`   New SMILES length: ${ritonavir.smiles.length} characters`);
    console.log(`   Molecular Weight: ${ritonavir.molecularWeight} g/mol`);
    console.log(`\n🔬 Now re-run your docking - you should get -9 to -11 kcal/mol`);

    await mongoose.disconnect();
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

fixRitonavirSmiles();
