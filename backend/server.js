require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const authRoutes = require('./routes/auth');
const proteinRoutes = require('./routes/proteins');
const ligandRoutes = require('./routes/ligands');
const dockingRoutes = require('./routes/docking');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Root route
app.get('/', (req, res) => {
  res.json({ 
    status: 'ok',
    message: 'ProteinDock API Server',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      auth: '/api/auth',
      proteins: '/api/proteins',
      ligands: '/api/ligands',
      docking: '/api/docking',
      vinaStatus: '/api/docking/vina-status'
    },
    documentation: 'https://github.com/YashJadhav21/ProteinDock'
  });
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/proteins', proteinRoutes);
app.use('/api/ligands', ligandRoutes);
app.use('/api/docking', dockingRoutes);

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'ProteinDock API is running' });
});

// MongoDB Connection
const mongoUri = process.env.MONGODB_URI;

if (!mongoUri) {
  console.error('❌ ERROR: MONGODB_URI environment variable is not set!');
  console.error('📝 Please set MONGODB_URI in Railway environment variables');
  console.error('💡 Get MongoDB URI from: https://mongodb.com/cloud/atlas');
  process.exit(1);
}

mongoose.connect(mongoUri)
  .then(() => {
    console.log('✅ Connected to MongoDB');
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
      console.log(`🚀 Server running on http://localhost:${PORT}`);
      
      // Start cleanup scheduler for expired 3D viewers
      setupViewerCleanup();
    });
  })
  .catch((err) => {
    console.error('❌ MongoDB connection error:', err);
  });

// Cleanup scheduler for expired 3D viewers
function setupViewerCleanup() {
  const fs = require('fs');
  const path = require('path');
  const DockingJob = require('./models/DockingJob');
  
  // Run cleanup every 10 minutes
  setInterval(async () => {
    try {
      const now = new Date();
      
      // Find jobs with expired viewers
      const jobsWithExpiredViewers = await DockingJob.find({
        'results.viewer.expiresAt': { $lt: now },
        'results.viewer.htmlPath': { $exists: true }
      });
      
      let cleanedCount = 0;
      
      for (const job of jobsWithExpiredViewers) {
        try {
          const htmlPath = job.results.viewer.htmlPath;
          
          // Delete the HTML file
          if (fs.existsSync(htmlPath)) {
            fs.unlinkSync(htmlPath);
            cleanedCount++;
          }
          
          // Clear viewer data from database (keep job record)
          job.results.viewer = {};
          await job.save();
          
        } catch (err) {
          console.error('[Cleanup] Error cleaning viewer:', err.message);
        }
      }
      
      if (cleanedCount > 0) {
        console.log(`[Cleanup] Deleted ${cleanedCount} expired viewer(s)`);
      }
      
    } catch (error) {
      console.error('[Cleanup] Scheduled cleanup error:', error.message);
    }
  }, 10 * 60 * 1000); // Every 10 minutes
  
  console.log('🧹 Viewer cleanup scheduler started (runs every 10 minutes)');
}

module.exports = app;
