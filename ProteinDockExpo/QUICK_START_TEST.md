# 🚀 QUICK START - Test Your Updates Now!

## ✅ What's Been Fixed (ProteinDockExpo)

### 1. **Ritonavir SMILES** - Fixed in database ✓
### 2. **Data Persistence** - Clean object storage ✓
### 3. **PDB Upload** - Protein & Ligand support ✓
### 4. **Auto-Grid Detection** - Automatic binding site detection ✓
### 5. **Screen Refresh** - Auto-reload on navigation ✓

---

## 🧪 TEST NOW (5 minutes)

### Step 1: Start Backend (if not running)
```powershell
cd C:\ProteinDock\backend
node server.js
```

**Look for:**
```
✅ AutoDock Vina is available
✅ Connected to MongoDB
🚀 Server running on http://localhost:3000
```

---

### Step 2: Start Frontend (already running)
```powershell
cd C:\ProteinDock\ProteinDockExpo
npx expo start --clear
```

Scan QR code in Expo Go app

---

### Step 3: Test Complete Workflow

#### A. Login/Register
```
1. Open app in Expo Go
2. Login or Register
```

#### B. Select Protein
```
1. Tap "Protein" tab
2. Enter PDB ID: 1HSG
3. Tap "Fetch Protein"
   ✅ Should show: "✓ Protein Loaded: 1HSG"
   ✅ May show alert: "Using existing protein: 1HSG"
4. Tap "Continue to Ligand Design"
```

#### C. Create Ligand
```
1. Ensure "SMILES" mode is selected (toggle button)
2. Enter name: Ritonavir
3. Enter SMILES: (paste the correct one from database)
   Or use: CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C
4. Tap "Create Ligand"
   ✅ Should show: "✓ Ligand Created: Ritonavir"
   ✅ May show alert: "Using existing ligand: Ritonavir"
5. Tap "Continue to Docking"
```

#### D. Configure Docking (AUTO-GRID!)
```
1. Should see both protein and ligand displayed
2. Tap "Configure & Run Docking"
3. ✅ WATCH FOR AUTO-GRID DETECTION:
   - Should show "Detecting optimal grid box..."
   - Loading spinner appears
   - Grid values auto-populate:
     • Center X: ~13.1
     • Center Y: ~22.5
     • Center Z: ~5.6
     • Size X: ~25
     • Size Y: ~20
     • Size Z: ~19
   - Message: "Grid detected from co-crystallized ligand"
4. Review settings (or keep defaults)
5. Tap "Start Docking Job"
```

#### E. View Results
```
1. Should navigate to Results screen
2. Watch job progress (polling every 3 seconds)
3. ✅ Should complete without errors
4. ✅ Check binding affinity: -9 to -11 kcal/mol
```

---

## 🔍 WHAT TO VERIFY

### ✅ Data Persistence:
- Go to "Run Docking" screen
- Navigate away (to Home)
- Navigate back to "Run Docking"
- ✅ Protein and ligand should still be there

### ✅ Auto-Grid Detection:
- In DockingConfigScreen
- Grid should NOT be (0, 0, 0) anymore
- Should show detected values from protein structure
- Message should indicate detection method

### ✅ Manual Refresh:
- Tap refresh button (↻) next to "Define Search Space"
- Should re-detect grid
- Values may update

### ✅ No Errors:
- Check backend console (node terminal)
- Check frontend console (Expo app)
- Should not see kekulization errors
- Should not see "Invalid SMILES" errors

---

## 📊 EXPECTED OUTPUT

### Backend Console:
```
[Docking] Received docking request: { proteinId: "...", ligandId: "..." }
[Docking] Protein found: 1HSG
[Docking] Ligand found: Ritonavir
[Vina] Starting docking job: ...
[Docking] Progress: 15% - Preparing ligand...
[Docking] Progress: 30% - Preparing receptor...
[Docking] Progress: 50% - Running AutoDock Vina...
[Vina] Vina finished successfully
[Docking] Job completed successfully
```

### Frontend Console (Expo):
```
[Grid Auto-Detect] {
  gridCenter: { x: 13.1, y: 22.5, z: 5.6 },
  gridSize: { x: 25, y: 20, z: 19 },
  method: 'ligand-based',
  message: 'Grid detected from co-crystallized ligand (45 atoms)'
}
[DockingConfig] Starting docking with config: { ... }
[DockingConfig] Job submitted: <jobId>
```

---

## 🐛 TROUBLESHOOTING

### Problem: Grid still shows (0, 0, 0)
**Solution:**
1. Check backend console for errors
2. Verify `detect_grid.py` exists in backend folder
3. Check Python and BioPython are installed
4. Tap refresh button (↻) to retry

### Problem: "Using existing protein" but different data
**Solution:**
1. Clear app storage (or uninstall/reinstall)
2. Re-fetch protein fresh

### Problem: Docking fails with kekulization error
**Solution:**
1. Run `node fix_ritonavir_smiles.js` again
2. Verify Ritonavir in database has 106 character SMILES
3. Delete old ligand and recreate

### Problem: Data missing on Run Docking screen
**Solution:**
1. Use refresh button (↻) in header
2. Navigate back to Protein/Ligand screens
3. Re-select items
4. Check AsyncStorage has clean objects

---

## 📝 FILES TO CHECK

### If grid detection not working:
```
✓ backend/detect_grid.py (should exist)
✓ backend/routes/proteins.js (has grid-suggestion endpoint)
✓ ProteinDockExpo/src/services/api.ts (has getGridSuggestion)
✓ ProteinDockExpo/src/screens/DockingConfigScreen.tsx (has detectGrid)
```

### If data persistence issues:
```
✓ ProteinDockExpo/src/screens/ProteinScreen.tsx (clean extraction)
✓ ProteinDockExpo/src/screens/LigandScreen.tsx (clean extraction)
✓ ProteinDockExpo/src/screens/DockingScreen.tsx (useFocusEffect)
```

---

## 🎯 SUCCESS CRITERIA

You'll know everything works when:

1. ✅ Grid auto-populates with non-zero values
2. ✅ Grid message shows detection method
3. ✅ Docking completes without errors
4. ✅ Binding affinity is -9 to -11 kcal/mol for Ritonavir
5. ✅ Data persists when navigating between screens
6. ✅ Refresh button updates grid values
7. ✅ No kekulization errors in console
8. ✅ Alerts show for duplicate proteins/ligands

---

## 🎉 YOU'RE DONE!

**All fixes are applied to ProteinDockExpo.**

Test the workflow above and verify:
- Auto-grid detection works
- Data persists correctly
- Ritonavir docking succeeds
- Results show good binding affinity

**Happy Testing! 🚀**
