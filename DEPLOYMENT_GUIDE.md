# ProteinDock - Deployment Guide

## 📱 Building APK for Client Delivery

### Prerequisites
1. **Expo Account** (free): Sign up at https://expo.dev
2. **EAS CLI**: Install globally
   ```bash
   npm install -g eas-cli
   ```

### Step 1: Configure Backend Server
The APK needs a public backend URL. You have 3 options:

#### Option A: Deploy Backend to Cloud (Recommended)
**Using Railway/Render/Heroku:**
1. Push backend code to GitHub
2. Deploy to Railway.app (free tier):
   - Connect GitHub repo
   - Set environment variables (MONGODB_URI, JWT_SECRET, etc.)
   - Get public URL (e.g., `https://your-app.railway.app`)

#### Option B: Use ngrok (Testing Only)
```bash
cd backend
node server.js
# In another terminal:
ngrok http 3000
# Copy the https URL
```

#### Option C: Local Network (Demo Only)
- Use your computer's IP address
- Keep backend running: `cd backend && node server.js`
- Client must be on same WiFi

### Step 2: Update API URL in Frontend
Edit `ProteinDockExpo/src/services/api.ts`:
```typescript
// Replace with your deployed backend URL
const API_URL = 'https://your-backend-url.com/api';
// OR for local demo:
// const API_URL = 'http://YOUR_IP:3000/api';
```

### Step 3: Build APK with EAS

1. **Login to Expo**
   ```bash
   cd ProteinDockExpo
   eas login
   ```

2. **Configure Build**
   ```bash
   eas build:configure
   ```
   - Select "All" when asked which platforms
   - Choose "Production" profile

3. **Build APK**
   ```bash
   eas build -p android --profile preview
   ```
   - Wait 10-20 minutes for build to complete
   - Download APK from the provided link

### Step 4: Deliver to Client

**Download the APK:**
- After build completes, you'll get a download link
- Or visit: https://expo.dev/accounts/[your-account]/projects/proteindockexpo/builds

**Share with Client:**
1. Download APK file (e.g., `proteindock-v1.0.0.apk`)
2. Send via email/cloud storage
3. Provide installation instructions:

---

## 📲 Installation Instructions for Client

### For Android Users:

1. **Enable Unknown Sources**
   - Go to Settings → Security
   - Enable "Install apps from unknown sources" or "Unknown sources"

2. **Install APK**
   - Download the APK file
   - Open it and tap "Install"
   - If warned, tap "Install anyway"

3. **First Launch**
   - Open ProteinDock app
   - Register a new account
   - Start docking!

### System Requirements:
- Android 5.0 or higher
- 100MB free storage
- Internet connection required

---

## 🚀 Backend Deployment (For Production)

### MongoDB Setup
1. Create free MongoDB Atlas account: https://mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string
4. Add to backend `.env`:
   ```
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/proteindock
   ```

### Deploy to Railway (Free Tier)
1. Create account at https://railway.app
2. New Project → Deploy from GitHub
3. Select your backend folder
4. Add environment variables:
   ```
   MONGODB_URI=your_mongodb_uri
   JWT_SECRET=your_random_secret_key_here
   NODE_ENV=production
   PORT=3000
   ```
5. Copy the public URL (e.g., `https://proteindock.up.railway.app`)
6. Update frontend API_URL to this URL

### Alternative: Deploy to Render
1. Create account at https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Build command: `cd backend && npm install`
5. Start command: `node server.js`
6. Add environment variables
7. Deploy

---

## 🔧 Project Structure

```
ProteinDock/
├── backend/              # Node.js + Express API
│   ├── server.js        # Main server file
│   ├── vina_docking.py  # Docking engine
│   ├── routes/          # API endpoints
│   ├── models/          # Database schemas
│   └── package.json
│
├── ProteinDockExpo/     # React Native mobile app
│   ├── src/
│   │   ├── screens/     # UI screens
│   │   ├── services/    # API integration
│   │   └── navigation/
│   ├── app.json         # Expo config
│   └── package.json
│
└── README.md
```

---

## 📝 Environment Variables

### Backend (.env)
```bash
MONGODB_URI=mongodb://localhost:27017/proteindock  # Or MongoDB Atlas URI
JWT_SECRET=your_super_secret_jwt_key_change_this
NODE_ENV=development  # or 'production'
PORT=3000
```

### Frontend (src/services/api.ts)
```typescript
const API_URL = 'http://YOUR_BACKEND_URL/api';
```

---

## 🧪 Testing Before Delivery

1. **Test Backend**
   ```bash
   cd backend
   npm install
   node server.js
   ```
   Visit: http://localhost:3000 (should see "ProteinDock API")

2. **Test Frontend**
   ```bash
   cd ProteinDockExpo
   npm install
   npx expo start
   ```
   Scan QR code with Expo Go app

3. **Test Full Flow**
   - Register account
   - Upload/fetch protein
   - Add ligand
   - Run docking
   - View 3D results

---

## 🎯 Quick APK Build Commands

```bash
# 1. Update API URL
# Edit: ProteinDockExpo/src/services/api.ts

# 2. Build APK
cd ProteinDockExpo
eas login
eas build -p android --profile preview

# 3. Wait for build (~15 minutes)
# 4. Download APK from provided link
# 5. Send to client!
```

---

## 📊 Features Included

✅ Protein fetching from PDB database
✅ Custom protein upload
✅ SMILES-based ligand input
✅ AutoDock Vina integration
✅ Automatic binding site detection
✅ Interactive 3D molecular viewer (WebView)
✅ Molecular interaction analysis (H-bonds, hydrophobic, π-stacking, ionic)
✅ Clustering of binding poses
✅ Auto-cleanup of temporary files (30-minute expiration)
✅ User authentication (JWT)
✅ Job history tracking

---

## 🛠️ Troubleshooting

**APK won't install:**
- Enable "Unknown sources" in Android settings
- Check minimum Android version (5.0+)

**"Network Error" in app:**
- Backend URL is incorrect in `api.ts`
- Backend server is not running
- Firewall blocking connection

**Docking fails:**
- Check backend logs
- Ensure Python dependencies installed
- Verify AutoDock Vina is available

**3D Viewer doesn't load:**
- Check internet connection (loads py3Dmol from CDN)
- Viewer may have expired (30-minute limit)
- Run a new docking job

---

## 📞 Support

For issues:
1. Check backend logs: `cd backend && node server.js`
2. Check frontend console: Expo DevTools
3. Verify environment variables
4. Test API endpoints manually

---

## 🔒 Security Notes

⚠️ **Before Production:**
1. Change `JWT_SECRET` to a strong random value
2. Enable HTTPS on backend
3. Set up proper CORS policies
4. Use MongoDB Atlas (not local MongoDB)
5. Add rate limiting
6. Implement input validation

---

## 📦 What to Send Client

**Minimum Package:**
- ✅ APK file (from EAS build)
- ✅ Installation instructions
- ✅ Backend URL (if you're hosting it)
- ✅ Demo credentials (optional)

**Optional:**
- ✅ User guide
- ✅ Sample proteins/ligands for testing
- ✅ Support contact info

---

**Built with:**
- React Native + Expo
- Node.js + Express
- Python + AutoDock Vina
- MongoDB
- BioPython + py3Dmol
