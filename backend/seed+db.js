// seed_database.js - Add 1HSG and Ritonavir to MongoDB with specific IDs

require('dotenv').config();
const mongoose = require('mongoose');
const Protein = require('./models/Protein');
const Ligand = require('./models/Ligand');
const https = require('https');

// Ritonavir SMILES (correct 150-char version)
const RITONAVIR_SMILES = 'CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C';

// Function to download PDB from RCSB
function downloadPDB(pdbId) {
  return new Promise((resolve, reject) => {
    const url = `https://files.rcsb.org/download/${pdbId}.pdb`;
    console.log(`Downloading ${pdbId} from RCSB...`);
    
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log(`✅ Downloaded ${pdbId} (${data.length} bytes)`);
          resolve(data);
        } else {
          reject(new Error(`Failed to download: HTTP ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      reject(err);
    });
  });
}

async function seedDatabase() {
  try {
    console.log('Connecting to MongoDB...');
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ Connected to MongoDB\n');

    // Download full 1HSG PDB structure
    console.log('Downloading 1HSG from RCSB PDB...');
    let pdbStructure;
    try {
      pdbStructure = await downloadPDB('1HSG');
    } catch (error) {
      console.error('❌ Failed to download PDB:', error.message);
      console.log('Please check your internet connection and try again.');
      return;
    }

    // Delete ALL existing proteins and ligands first
    console.log('\nCleaning up existing data...');
    await Protein.deleteMany({});
    await Ligand.deleteMany({});
    console.log('   ✅ Removed all existing proteins and ligands');

    // 1. Add 1HSG Protein with specific ID
    console.log('\nAdding 1HSG HIV-1 Protease...');
    const proteinId = new mongoose.Types.ObjectId('69313695196d1cda93abd42d');
    
    const protein = await Protein.create({
      _id: proteinId,
      pdbId: '1HSG',
      name: '1HSG',
      organism: 'Human Immunodeficiency Virus 1',
      resolution: 2.5,
      structure: pdbStructure,
      selectedChains: ['A', 'B'],
      availableChains: ['A', 'B'],
      heteroatoms: ['MK1'],
      cofactors: [],
      description: 'HIV-1 Protease with bound inhibitor MK1'
    });
    console.log(`✅ Protein added: ${protein.name} (ID: ${protein._id})`);
    console.log(`   Structure size: ${pdbStructure.length} bytes`);

    // 2. Add Ritonavir Ligand with specific ID
    console.log('\nAdding Ritonavir ligand...');
    const ligandId = new mongoose.Types.ObjectId('69319c11e920b87470027cac');
    
    const ligand = await Ligand.create({
      _id: ligandId,
      name: 'Ritonavir',
      smiles: RITONAVIR_SMILES,
      formula: 'C37H48N6O5S2',
      properties: {
        molecularWeight: 720.95,
        logP: 5.6,
        hBondDonors: 4,
        hBondAcceptors: 8,
        rotatableBonds: 15,
        tpsa: 202.26
      },
      prepared: false
    });
    console.log(`✅ Ligand added: ${ligand.name} (ID: ${ligand._id})`);

    console.log('\n' + '='.repeat(70));
    console.log('DATABASE SEEDED SUCCESSFULLY!');
    console.log('='.repeat(70));
    console.log(`\nProtein ID: ${protein._id}`);
    console.log(`Ligand ID:  ${ligand._id}`);
    console.log('\nYou can now run docking with these exact IDs!');
    console.log('='.repeat(70));

  } catch (error) {
    console.error('❌ Error seeding database:', error);
  } finally {
    await mongoose.connection.close();
    console.log('\n✅ Database connection closed');
  }
}

seedDatabase();