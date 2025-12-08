#!/bin/bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node dependencies and start server
cd backend
npm install
node server.js
