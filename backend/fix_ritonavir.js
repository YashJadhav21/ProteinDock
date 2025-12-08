// MongoDB script to fix Ritonavir SMILES
db = db.getSiblingDB('proteindock');

print('Looking for Ritonavir...');
var ligand = db.ligands.findOne({name: /ritonavir/i});

if (!ligand) {
    print('ERROR: Ritonavir not found!');
} else {
    print('Found Ritonavir with ID: ' + ligand._id);
    print('Current SMILES length: ' + ligand.smiles.length);
    
    var correctSMILES = 'CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C';
    
    var result = db.ligands.updateOne(
        {_id: ligand._id},
        {$set: {smiles: correctSMILES}}
    );
    
    if (result.modifiedCount > 0) {
        print('✅ SUCCESS: Updated Ritonavir SMILES');
        print('New SMILES length: ' + correctSMILES.length);
        
        var updated = db.ligands.findOne({_id: ligand._id});
        print('Verified SMILES: ' + updated.smiles.substring(0, 50) + '...');
    } else {
        print('❌ FAILED: Could not update');
    }
}
