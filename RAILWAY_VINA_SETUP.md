# Railway Deployment with AutoDock Vina - Setup Guide

## 🚂 Step-by-Step Railway Deployment

### 1. Set Environment Variables in Railway

Go to your Railway project → **Variables** tab and add:

```bash
MONGODB_URI=mongodb+srv://yashjadhav2102_db_user:MOuex0vQjsmPo7Zd@cluster0.oma8xns.mongodb.net/proteindock
JWT_SECRET=change_this_to_a_random_secure_key_1234567890
NODE_ENV=production
PORT=3000
```

**Important:** Change `JWT_SECRET` to a secure random string!

### 2. Deployment will automatically:
- ✅ Install Python 3.11
- ✅ Install Node.js 20
- ✅ Download AutoDock Vina (Linux version)
- ✅ Install BioPython, NumPy, OpenBabel
- ✅ Install Node dependencies
- ✅ Start the server

### 3. Monitor Deployment Logs

Watch for these messages:
```
✅ AutoDock Vina downloaded successfully
✅ All dependencies installed
✅ Connected to MongoDB
✅ AutoDock Vina is available
🚀 Server running on http://localhost:8080
```

### 4. Get Your Public URL

After deployment:
1. Go to **Settings** → **Networking**
2. Click **Generate Domain**
3. Copy the URL (e.g., `proteindock-production.up.railway.app`)

### 5. Update Frontend API URL

Edit `ProteinDockExpo/src/services/api.ts`:
```typescript
const API_URL = 'https://your-railway-url.up.railway.app/api';
```

Then commit and push:
```bash
cd ProteinDockExpo
git add src/services/api.ts
git commit -m "Update API URL to Railway deployment"
cd ..
git push origin main
```

### 6. Test Backend

Visit in browser:
```
https://your-railway-url.up.railway.app/api/health
```

Should return:
```json
{
  "status": "ok",
  "message": "ProteinDock API is running"
}
```

Test Vina availability:
```
https://your-railway-url.up.railway.app/api/docking/vina-status
```

Should return:
```json
{
  "available": true,
  "status": {
    "available": true,
    "vina_path": "/app/backend/vina_bin/vina",
    "python_packages": ["BioPython", "NumPy"],
    "message": "AutoDock Vina is ready"
  }
}
```

---

## 🎯 Build APK with Production Backend

Now that backend is deployed with Vina:

1. **Update API URL** (see step 5 above)
2. **Build APK**:
   ```bash
   cd ProteinDockExpo
   eas login
   eas build -p android --profile preview
   ```
3. **Wait 15-20 minutes** for build
4. **Download APK** from provided link
5. **Test docking** - should now use real AutoDock Vina!

---

## 🔍 Verify Real Vina is Working

After installing the APK:

1. Register/login
2. Add protein (e.g., fetch `1hsg`)
3. Add ligand with SMILES
4. Run docking
5. Check results - should see:
   - "Real Vina completed" in logs
   - Accurate binding affinities
   - Interaction analysis
   - 3D molecular viewer

The results will be scientifically accurate using AutoDock Vina!

---

## 🐛 Troubleshooting

**"Vina not available" in Railway logs:**
- Check if `install.sh` ran successfully
- Verify Python packages installed
- Check Railway build logs for errors

**Deployment fails:**
- Verify environment variables are set
- Check MongoDB URI is correct (include `/proteindock` at end)
- Review Railway deployment logs

**Frontend can't connect:**
- Verify API_URL matches Railway domain
- Check CORS is enabled (already configured)
- Ensure Railway service is running

---

## 📊 What's Different from Simulation Mode

**Simulation Mode** (no Vina):
- Fast (2-3 seconds)
- Random binding affinities
- Fake interactions
- Good for testing UI

**Real Vina Mode** (with Vina):
- Slower (30-60 seconds per job)
- Scientifically accurate binding affinities
- Real molecular interactions detected
- Production-ready results

---

## ✅ Final Checklist

Before sending APK to client:

- [ ] Railway deployment successful
- [ ] Environment variables set (MONGODB_URI, JWT_SECRET)
- [ ] AutoDock Vina available (check /api/docking/vina-status)
- [ ] Frontend API_URL updated to Railway domain
- [ ] APK built with EAS
- [ ] Tested complete docking workflow
- [ ] 3D viewer working
- [ ] Interactions showing correctly

---

**Your deployment is now production-ready with real AutoDock Vina! 🎉**
