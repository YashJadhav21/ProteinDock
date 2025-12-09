# MGLTools Setup for Production

This directory will contain MGLTools AutoDockTools utilities needed for receptor preparation.

## What Gets Installed

During the build process (`render-build.sh`), the following will be downloaded and set up:

- **MGLTools AutoDockTools** - Specifically the `prepare_receptor4.py` script and dependencies
- **Location**: `backend/mgltools/MGLToolsPckgs/AutoDockTools/Utilities24/`

## How It Works

### Local Development (Windows)
- Uses your installed MGLTools at: `C:\Program Files (x86)\MGLTools-1.5.7\`
- No download needed

### Production (Linux/Render)
- Downloads MGLTools Linux version during build
- Extracts only the needed Python scripts (no GUI)
- Sets up in `backend/mgltools/` directory

## Build Process

The `render-build.sh` script automatically:
1. Downloads MGLTools tarball from Scripps
2. Extracts the MGLToolsPckgs directory
3. Cleans up temporary files
4. Makes scripts available for `vina_docking.py`

## Manual Setup (if needed)

If automatic download fails, you can manually download MGLTools:

```bash
cd backend
wget http://mgltools.scripps.edu/downloads/downloads/tars/releases/REL1.5.7/mgltools_x86_64Linux2_1.5.7.tar.gz
tar -xzf mgltools_x86_64Linux2_1.5.7.tar.gz
mkdir -p mgltools
mv mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs mgltools/
```

## Verify Installation

Check if `prepare_receptor4.py` exists:
```bash
ls backend/mgltools/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py
```

## Why MGLTools?

MGLTools' `prepare_receptor4.py` is the **gold standard** for receptor preparation:
- Adds hydrogens correctly
- Computes Gasteiger charges
- Sets proper atom types for AutoDock
- Handles edge cases (metals, non-standard residues, etc.)

Alternative approaches (Meeko, OpenBabel) lack some of these capabilities.
