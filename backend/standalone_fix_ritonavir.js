// Standalone MongoDB fix for Ritonavir
const mongoose = require('mongoose');
require('dotenv').config();

const CORRECT_SMILES = 'CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C';

async function fixRitonavir() {
  try {
    console.log('Connecting to MongoDB...');
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ Connected');

    // Get Ligand model
    const Ligand = require('./models/Ligand');
    
    // Find Ritonavir
    const ligand = await Ligand.findOne({ name: /ritonavir/i });
    
    if (!ligand) {
      console.log('❌ Ritonavir not found in database!');
      console.log('   Please create it first in the app.');
      process.exit(1);
    }

    console.log(`\n📋 Found Ritonavir:`);
    console.log(`   ID: ${ligand._id}`);
    console.log(`   Name: ${ligand.name}`);
    console.log(`   Current SMILES: ${ligand.smiles}`);
    console.log(`   Current length: ${ligand.smiles.length} chars`);

    // Update
    ligand.smiles = CORRECT_SMILES;
    await ligand.save();

    console.log(`\n✅ UPDATED SUCCESSFULLY!`);
    console.log(`   New SMILES: ${CORRECT_SMILES}`);
    console.log(`   New length: ${CORRECT_SMILES.length} chars`);
    console.log(`\n🔬 You can now run docking - expect -9 to -11 kcal/mol`);

    await mongoose.disconnect();
    process.exit(0);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

fixRitonavir();
