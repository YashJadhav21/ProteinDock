# ProteinDock MVP - Molecular Docking Mobile App

## 🎯 Project Overview
Mobile application for molecular docking built with React Native (Expo) and Node.js backend. Designed for pharmacy students to learn and practice protein-ligand docking.

## ✨ Features

### Core Functionality
✅ **User Authentication** - Register/Login with JWT  
✅ **Protein Selection** - Fetch from RCSB PDB database  
✅ **Ligand Design** - SMILES input with validation  
✅ **Molecular Docking** - Real AutoDock Vina OR Simulation mode  
✅ **Results Visualization** - Binding affinity, poses, clusters, interactions  

### SwissDock-Inspired Features
✅ **Advanced Configuration**
- Configurable search space (grid box center & size)
- Adjustable exhaustivity (1-64)
- Multiple docking methods (Vina, Attracting Cavities*)
- Custom number of poses (1-20)

✅ **Enhanced Results**
- Pose clustering by RMSD
- Interaction analysis (H-bonds, hydrophobic, π-stacking, ionic)
- Multiple binding modes identification
- Detailed scoring metrics

✅ **Real-Time Progress**
- Job status tracking
- Progress bar (0-100%)
- Estimated completion time

## 🚀 Tech Stack

### Frontend (Mobile)
- **React Native** via Expo
- **React Native Paper** - Material Design UI
- **React Navigation** - Stack + Bottom Tabs
- **AsyncStorage** - Local data persistence
- **TypeScript** - Type safety

### Backend
- **Node.js** + **Express.js**
- **MongoDB Atlas** - Cloud database
- **JWT Authentication** - Secure token-based auth
- **AutoDock Vina** - Real molecular docking (optional)
- **Python Integration** - For Vina execution

## 📦 Project Structure
```
ProteinDock/
├── backend/                    # Node.js Express API
│   ├── models/                 # MongoDB schemas
│   │   ├── User.js            # User authentication
│   │   ├── Protein.js         # Protein data with chain selection
│   │   ├── Ligand.js          # Ligand data with molecular properties
│   │   └── DockingJob.js      # Job tracking with clustering
│   ├── routes/                # API endpoints
│   │   ├── auth.js            # Login/Register
│   │   ├── proteins.js        # Protein management
│   │   ├── ligands.js         # Ligand creation
│   │   └── docking.js         # Docking submission & results
│   ├── utils/
│   │   └── vinaDocking.js     # AutoDock Vina wrapper
│   ├── vina_docking.py        # Python Vina integration
│   └── server.js              # Express server
│
└── ProteinDockExpo/           # React Native Expo app
    └── src/
        ├── screens/           # All app screens
        │   ├── LoginScreen.tsx
        │   ├── RegisterScreen.tsx
        │   ├── HomeScreen.tsx
        │   ├── ProteinScreen.tsx
        │   ├── LigandScreen.tsx
        │   ├── DockingScreen.tsx
        │   ├── DockingConfigScreen.tsx  # NEW: Advanced config
        │   └── ResultsScreen.tsx        # Enhanced with clustering
        ├── navigation/
        │   └── AppNavigator.tsx
        ├── contexts/
        │   └── AuthContext.tsx
        └── services/
            └── api.ts
```

## 🛠️ Setup Instructions

### Backend Setup
```powershell
cd c:\ProteinDock\backend
npm install
npm run dev  # Starts on http://localhost:3000
```

**MongoDB Atlas Connection**: Already configured in `server.js`

**Optional - AutoDock Vina Installation**:
- See `VINA_SETUP.md` for detailed instructions
- **For Windows users**: Vina Python package has compilation issues
- **Recommended**: Use simulation mode (works great for learning & demos!)
- **Alternative**: Online services like SwissDock for real docking
- If not installed, simulation mode will be used automatically ✅

### Frontend Setup (Expo)
```powershell
cd c:\ProteinDock\ProteinDockExpo
npm install
npx expo start
```

**Test on Your Phone**:
1. Install **Expo Go** from Play Store/App Store
2. Scan QR code from terminal
3. Update `API_BASE_URL` in `src/services/api.ts` to your computer's IP

## 🔐 MongoDB Atlas Credentials
- **Connection String**: `mongodb+srv://yashjadhav2102_db_user:MOuex0vQjsmPo7Zd@cluster0.oma8xns.mongodb.net/`
- **Database**: `proteindock`
- **Collections**: `users`, `proteins`, `ligands`, `dockingjobs`

## 📱 App Screens
1. **Login/Register** - JWT authentication
2. **Home** - Dashboard with statistics
3. **Protein** - Search RCSB PDB, select chains
4. **Ligand** - SMILES input with validation
5. **Docking** - Job history and submission
6. **DockingConfig** - SwissDock-inspired advanced configuration (grid box, exhaustivity, poses)
7. **Results** - Binding affinity, clusters, poses, interactions

## 🧪 Docking Modes

### Simulation Mode (Default)
- ✅ Works immediately, no installation needed
- ✅ Fast results (~5 seconds)
- ✅ Educational purposes
- ⚠️ Simplified scoring (not real binding affinities)

### Real AutoDock Vina Mode
- ✅ **Industry-standard molecular docking**
- ✅ Accurate binding affinity predictions (kcal/mol)
- ✅ Scientifically validated results
- ⚠️ Requires Python packages installation
- ⚠️ Slower (30 sec - 10 min depending on exhaustivity)

**To Enable Real Vina**: Follow `VINA_SETUP.md` instructions

**Auto-Detection**: Backend automatically detects Vina availability and switches modes. No code changes needed!

## 🧬 Testing Workflow
1. **Register** a new account (e.g., `yash@test.com` / `password123`)
2. **Add Protein**: Search for `1HSG` (HIV-1 Protease)
3. **Add Ligand**: SMILES for Aspirin: `CC(=O)Oc1ccccc1C(=O)O`
4. **Configure Docking**:
   - Grid Center: 0, 0, 0 (or specific active site coordinates)
   - Grid Size: 20, 20, 20 Å
   - Exhaustivity: 1 (test) or 8 (production)
   - Poses: 9
5. **View Results**: Clusters, binding scores, interactions

## 📊 Expected Performance
| Exhaustivity | Time    | Accuracy | Use Case           |
|--------------|---------|----------|--------------------|
| 1            | 30 sec  | Low      | Quick testing      |
| 8 (default)  | 5 min   | Good     | Standard docking   |
| 16           | 10 min  | High     | Publication-grade  |
| 32           | 20 min  | Very High| Critical research  |

*Times are approximate and depend on protein/ligand size*

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get JWT token

### Proteins
- `GET /api/proteins` - List user's proteins
- `POST /api/proteins` - Add protein from PDB
- `GET /api/proteins/:id` - Get protein details

### Ligands
- `GET /api/ligands` - List user's ligands
- `POST /api/ligands` - Create ligand from SMILES
- `GET /api/ligands/:id` - Get ligand details

### Docking
- `GET /api/docking/jobs` - List user's docking jobs
- `POST /api/docking/submit` - Submit docking job
- `GET /api/docking/jobs/:id` - Get job status
- `GET /api/docking/vina-status` - Check if AutoDock Vina is available

## 🚨 Troubleshooting

### Backend Issues
- **Port 3000 already in use**: Kill process or change port in `server.js`
- **MongoDB connection failed**: Check Atlas credentials/network access
- **Vina not found**: See `VINA_SETUP.md` or use simulation mode

### Frontend Issues
- **Cannot connect to API**: Update `API_BASE_URL` to your local IP (not localhost)
- **Network request failed**: Ensure backend is running and firewall allows connections
- **Expo Go crash**: Clear cache: `npx expo start -c`

### Docking Issues
- **Job stuck at 0%**: Check backend logs for errors
- **"Vina unavailable" message**: Install Python packages (see `VINA_SETUP.md`)
- **No poses generated**: Check protein/ligand preparation, try different parameters

## 📚 Documentation
- **VINA_SETUP.md** - Complete AutoDock Vina installation guide
- **TECH_STACK_ANALYSIS.md** - Initial technology research
- **DEVELOPMENT_PLAN.md** - Project roadmap

## 🎓 For Students
This MVP is designed for educational purposes:
- **Start with simulation mode** to understand the workflow
- **Upgrade to real Vina** when you need accurate results for reports/research
- **Low exhaustivity (1-2)** for quick testing
- **Standard exhaustivity (8)** for assignments
- **High exhaustivity (16+)** only for important research

## 🔮 Future Enhancements (Not in MVP)
- 3D molecular visualization (Mol*)
- Multiple docking methods (SMINA, LeDock)
- Cloud-based Vina execution
- PLIP integration for detailed interaction analysis
- Pharmacophore modeling
- ADMET predictions

## 👨‍💻 Development Status
✅ **COMPLETED**: Full MVP with dual-mode docking (simulation + real Vina)  
🚀 **READY TO USE**: Simulation mode works immediately  
⚙️ **OPTIONAL**: Install Python packages for real Vina  

---

**Built by students, for students** 🎓💊
