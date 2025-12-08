# DATABASE STRUCTURE & DUPLICATE PREVENTION
## MongoDB Schema Validation & ID Handling
**Date:** December 8, 2025

---

## ✅ FIXES APPLIED

### 1. **Protein Duplicate Prevention**

**Problem:** Multiple copies of same PDB ID could be created

**Solution Applied:**
```javascript
// Database Level: Unique index on pdbId
proteinSchema.index({ pdbId: 1 }, { unique: true });

// Application Level: Check before insert
const existingProtein = await Protein.findOne({ pdbId: pdbId.toUpperCase() });
if (existingProtein) {
  return res.status(200).json({
    protein: existingProtein,
    message: 'Protein with this PDB ID already exists',
    isExisting: true
  });
}
```

**Benefit:** Prevents duplicate PDB entries globally (1HSG should only exist once)

---

### 2. **Ligand Duplicate Prevention**

**Problem:** Users could create multiple identical ligands

**Solution Applied:**
```javascript
// Database Level: Compound unique index per user
ligandSchema.index({ userId: 1, name: 1, smiles: 1 }, { unique: true, sparse: true });

// Application Level: Check before insert
const existingLigand = await Ligand.findOne({ 
  userId: req.userId,
  name: name,
  smiles: smiles
});

if (existingLigand) {
  return res.status(200).json({
    ...existingLigand.toObject(),
    message: 'Ligand with this name and SMILES already exists',
    isExisting: true
  });
}
```

**Benefit:** Prevents duplicate ligands per user (same name + SMILES)

---

### 3. **Enhanced API Responses**

**Problem:** Frontend couldn't tell if entity was existing or newly created

**Solution Applied:**
```javascript
// All create/fetch endpoints now return:
{
  ...entity,
  message: 'Protein already exists in database',
  isExisting: true  // or false
}
```

**Frontend can now:**
- Show "Using existing protein: 1HSG" message
- Ask user "Update existing or create new?"
- Prevent confusion about duplicates

---

### 4. **MongoDB ObjectId Validation**

**Problem:** Invalid IDs caused cryptic errors

**Solution Applied:**
```javascript
const mongoose = require('mongoose');

// Validate ID format before querying
if (!mongoose.Types.ObjectId.isValid(proteinId)) {
  return res.status(400).json({ 
    message: 'Invalid protein ID format',
    proteinId 
  });
}
```

**Benefit:** Clear error messages for invalid IDs

---

### 5. **Enhanced Logging**

**Problem:** Difficult to debug ID mismatches

**Solution Applied:**
```javascript
console.log('[Docking] Looking for protein ID:', proteinId);
console.log('[Docking] Protein found:', protein ? `${protein.pdbId} (${protein._id})` : 'NOT FOUND');
console.log('[Docking] Total proteins in DB:', await Protein.countDocuments());
console.log('[Docking] User proteins:', await Protein.countDocuments({ userId: req.userId }));
```

**Benefit:** Easy debugging of ID issues

---

## 📊 DATABASE SCHEMA OVERVIEW

### Protein Schema
```javascript
{
  _id: ObjectId,                    // MongoDB ID (used in docking)
  pdbId: String (UNIQUE, INDEXED),  // "1HSG", "3CLN", etc.
  name: String,
  structure: String,                // PDB file content
  userId: ObjectId,                 // Creator
  createdAt: Date
}

// Indexes:
// 1. { pdbId: 1 } UNIQUE - Prevents duplicates
// 2. { pdbId: 1 } INDEX - Fast lookups
```

### Ligand Schema
```javascript
{
  _id: ObjectId,                    // MongoDB ID (used in docking)
  name: String,
  smiles: String,
  inputFormat: 'smiles' | 'pdb',
  pdbFile: String (optional),
  userId: ObjectId,                 // Owner
  createdAt: Date
}

// Indexes:
// 1. { userId: 1, name: 1, smiles: 1 } UNIQUE - Prevent user duplicates
// 2. { userId: 1, createdAt: -1 } INDEX - Fast user queries
```

### DockingJob Schema
```javascript
{
  _id: ObjectId,
  userId: ObjectId,
  proteinId: ObjectId,  // ← References Protein._id
  ligandId: ObjectId,   // ← References Ligand._id
  status: 'pending' | 'running' | 'completed' | 'failed',
  results: { ... },
  createdAt: Date
}
```

---

## 🔄 COMPLETE WORKFLOW

### Protein Flow:
```
1. User enters PDB ID: "1HSG"
   
2. Frontend calls: POST /api/proteins/fetch/1HSG
   
3. Backend checks:
   ✓ Does Protein with pdbId="1HSG" exist?
   
4a. IF EXISTS:
    - Return existing protein
    - Response: { ...protein, isExisting: true }
    - Frontend shows: "Using existing protein: 1HSG"
    
4b. IF NOT EXISTS:
    - Fetch from RCSB PDB
    - Save to database
    - Response: { ...protein, isExisting: false }
    - Frontend shows: "Protein loaded: 1HSG"
    
5. Frontend stores protein._id in AsyncStorage
   {
     _id: "673ab123...",
     pdbId: "1HSG",
     name: "HIV-1 Protease"
   }
```

### Ligand Flow:
```
1. User enters:
   - Name: "Aspirin"
   - SMILES: "CC(=O)Oc1ccccc1C(=O)O"
   
2. Frontend calls: POST /api/ligands
   Body: { name, smiles }
   
3. Backend checks:
   ✓ Does Ligand with userId + name + smiles exist?
   
4a. IF EXISTS:
    - Return existing ligand
    - Response: { ...ligand, isExisting: true }
    - Frontend shows: "Ligand already exists. Use existing?"
    
4b. IF NOT EXISTS:
    - Create new ligand
    - Response: { ...ligand, isExisting: false }
    - Frontend shows: "Ligand created: Aspirin"
    
5. Frontend stores ligand._id in AsyncStorage
   {
     _id: "673ab456...",
     name: "Aspirin",
     smiles: "CC(=O)Oc1ccccc1C(=O)O"
   }
```

### Docking Flow:
```
1. Frontend sends:
   POST /api/docking/submit
   {
     proteinId: "673ab123...",  // ← From AsyncStorage
     ligandId: "673ab456...",   // ← From AsyncStorage
     parameters: { ... }
   }
   
2. Backend validates:
   ✓ Is proteinId valid ObjectId? → Yes
   ✓ Does Protein exist? → Query: Protein.findById(proteinId)
   ✓ Is ligandId valid ObjectId? → Yes
   ✓ Does Ligand exist? → Query: Ligand.findById(ligandId)
   
3. Backend creates job:
   DockingJob.create({
     userId,
     proteinId,  // ← References Protein._id
     ligandId,   // ← References Ligand._id
     ...
   })
   
4. Backend processes docking:
   - Fetch protein.structure (PDB content)
   - Fetch ligand.smiles
   - Run AutoDock Vina
   - Save results
```

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: "Protein or ligand not found"

**Cause:** IDs in AsyncStorage don't match database

**Debug:**
```javascript
// Check AsyncStorage
const protein = await AsyncStorage.getItem('selectedProtein');
const ligand = await AsyncStorage.getItem('selectedLigand');
console.log('Stored protein:', JSON.parse(protein));
console.log('Stored ligand:', JSON.parse(ligand));

// Verify _id exists
console.log('Protein ID:', JSON.parse(protein)._id);
console.log('Ligand ID:', JSON.parse(ligand)._id);
```

**Solution:**
```javascript
// Ensure _id is stored correctly
const proteinData = await api.fetchProtein(pdbId, token);
await AsyncStorage.setItem('selectedProtein', JSON.stringify(proteinData));
// proteinData MUST contain _id field

// When submitting docking:
const storedProtein = JSON.parse(await AsyncStorage.getItem('selectedProtein'));
const proteinId = storedProtein._id;  // Use _id, not pdbId
```

---

### Issue 2: Duplicate proteins created

**Cause:** Unique index not applied yet

**Solution:**
```bash
# Drop existing Protein collection (ONLY in development!)
mongo
> use proteindock
> db.proteins.drop()
> exit

# Restart backend - indexes will be created
npm start
```

**Verification:**
```javascript
// Check indexes
db.proteins.getIndexes()
// Should show: { pdbId: 1 } with unique: true
```

---

### Issue 3: Can't create ligand with same name

**Cause:** User wants to create "Aspirin" with different SMILES

**Solution:** Ligand uniqueness is based on name + SMILES
```javascript
// These are DIFFERENT ligands (different SMILES):
{ name: "Aspirin", smiles: "CC(=O)Oc1ccccc1C(=O)O" }  // Aspirin
{ name: "Aspirin", smiles: "CCCCC" }                   // Different molecule, same name = ALLOWED

// These are SAME ligand (duplicate):
{ name: "Aspirin", smiles: "CC(=O)Oc1ccccc1C(=O)O" }  // Original
{ name: "Aspirin", smiles: "CC(=O)Oc1ccccc1C(=O)O" }  // Duplicate = REJECTED
```

---

## ✅ VERIFICATION CHECKLIST

### Test Duplicate Prevention:

**Test 1: Protein Duplicates**
```bash
# 1. Fetch 1HSG first time
curl -X POST http://localhost:3000/api/proteins/fetch/1HSG \
  -H "Authorization: Bearer $TOKEN"
# Response: { ..., isExisting: false }

# 2. Fetch 1HSG second time
curl -X POST http://localhost:3000/api/proteins/fetch/1HSG \
  -H "Authorization: Bearer $TOKEN"
# Response: { ..., isExisting: true, message: "Protein already exists" }

# 3. Verify only one 1HSG exists
mongo proteindock
> db.proteins.countDocuments({ pdbId: "1HSG" })
1  // ✓ Should be 1, not 2
```

**Test 2: Ligand Duplicates**
```bash
# 1. Create Aspirin first time
curl -X POST http://localhost:3000/api/ligands \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Aspirin","smiles":"CC(=O)Oc1ccccc1C(=O)O"}'
# Response: { ..., isExisting: false }

# 2. Create Aspirin second time (same user)
curl -X POST http://localhost:3000/api/ligands \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Aspirin","smiles":"CC(=O)Oc1ccccc1C(=O)O"}'
# Response: { ..., isExisting: true, message: "Ligand already exists" }
```

**Test 3: Docking with Valid IDs**
```bash
# Get protein and ligand IDs first
PROTEIN_ID=$(mongo proteindock --quiet --eval 'db.proteins.findOne({pdbId:"1HSG"})._id.str')
LIGAND_ID=$(mongo proteindock --quiet --eval 'db.ligands.findOne({name:"Aspirin"})._id.str')

# Submit docking job
curl -X POST http://localhost:3000/api/docking/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"proteinId\":\"$PROTEIN_ID\",\"ligandId\":\"$LIGAND_ID\"}"
# Response: { status: "pending", ... } ✓
```

---

## 📝 API RESPONSE FORMAT

### All protein/ligand endpoints return:
```javascript
{
  _id: "673ab123...",        // MongoDB ObjectId
  pdbId: "1HSG",             // For proteins
  name: "HIV-1 Protease",
  structure: "ATOM ...",
  userId: "673ab999...",
  createdAt: "2025-12-08...",
  
  // NEW fields:
  message: "Protein already exists in database",
  isExisting: true           // true = found existing, false = newly created
}
```

### Frontend should:
```typescript
const response = await api.fetchProtein(pdbId, token);

if (response.isExisting) {
  // Show: "✓ Using existing protein: 1HSG"
  Alert.alert('Info', response.message);
} else {
  // Show: "✓ Protein loaded: 1HSG"
  Alert.alert('Success', 'Protein fetched successfully');
}

// Always store the full response (includes _id)
await AsyncStorage.setItem('selectedProtein', JSON.stringify(response));
```

---

## 🔧 MIGRATION GUIDE

### If you have existing data:

**Option 1: Fresh Start (Development)**
```bash
# Drop collections and restart
mongo proteindock
> db.proteins.drop()
> db.ligands.drop()
> db.dockingjobs.drop()
> exit

# Restart backend
cd backend
npm start
```

**Option 2: Keep Data (Production)**
```bash
# Create indexes manually
mongo proteindock
> db.proteins.createIndex({ pdbId: 1 }, { unique: true })
> db.ligands.createIndex({ userId: 1, name: 1, smiles: 1 }, { unique: true, sparse: true })
> exit

# Remove duplicates first:
> db.proteins.aggregate([
  { $group: { _id: "$pdbId", count: { $sum: 1 }, ids: { $push: "$_id" } } },
  { $match: { count: { $gt: 1 } } }
])
# Manually delete duplicate IDs using db.proteins.deleteOne({ _id: ... })
```

---

## ✅ SUMMARY

### Changes Made:

1. ✅ **Protein Schema:** Added unique index on `pdbId`
2. ✅ **Ligand Schema:** Added compound unique index on `userId + name + smiles`
3. ✅ **Protein Route:** Check for duplicates before insert, return `isExisting` flag
4. ✅ **Ligand Route:** Check for duplicates before insert, return `isExisting` flag
5. ✅ **Docking Route:** Enhanced ID validation and error messages
6. ✅ **Logging:** Added comprehensive logging for debugging

### Frontend Impact: **NONE**

The frontend continues to work as-is. The API now returns additional fields:
- `isExisting`: true/false
- `message`: Human-readable status

Frontend can optionally use these to show better messages to users.

### Database Impact:

- New unique indexes prevent duplicates
- Existing duplicates must be cleaned up manually
- Fresh databases will enforce uniqueness automatically

---

**Files Modified:**
- `backend/models/Protein.js` - Added unique index
- `backend/models/Ligand.js` - Added compound unique index
- `backend/routes/proteins.js` - Duplicate checking + enhanced responses
- `backend/routes/ligands.js` - Duplicate checking + enhanced responses
- `backend/routes/docking.js` - Enhanced ID validation + error messages
