# Download AutoDock Vina Binary for Windows
# This script downloads the pre-compiled Vina executable

$vinaUrl = "https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_windows_x86_64.zip"
$zipPath = "C:\ProteinDock\backend\vina_1.2.5.zip"
$extractPath = "C:\ProteinDock\backend\vina_bin"

Write-Host "📥 Downloading AutoDock Vina 1.2.5 for Windows..." -ForegroundColor Cyan

try {
    # Download the zip file
    Invoke-WebRequest -Uri $vinaUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "✅ Download complete!" -ForegroundColor Green
    
    # Extract the zip
    Write-Host "📦 Extracting files..." -ForegroundColor Cyan
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
    
    # Check if vina.exe exists
    $vinaExe = Join-Path $extractPath "vina.exe"
    if (Test-Path $vinaExe) {
        Write-Host "✅ vina.exe found at: $vinaExe" -ForegroundColor Green
        
        # Test execution
        Write-Host "`n🧪 Testing Vina..." -ForegroundColor Cyan
        & $vinaExe --version
        
        Write-Host "`n✅ AutoDock Vina is ready to use!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ vina.exe not found in expected location" -ForegroundColor Yellow
        Write-Host "Contents of $extractPath :" -ForegroundColor Yellow
        Get-ChildItem $extractPath -Recurse
    }
    
    # Clean up zip file
    Remove-Item $zipPath -Force
    Write-Host "`n🧹 Cleaned up temporary files" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n📌 Manual download instructions:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://github.com/ccsb-scripps/AutoDock-Vina/releases" -ForegroundColor Yellow
    Write-Host "2. Download: vina_1.2.5_windows_x86_64.zip" -ForegroundColor Yellow
    Write-Host "3. Extract vina.exe to: C:\ProteinDock\backend\vina_bin\" -ForegroundColor Yellow
}

Write-Host "`n📚 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your backend: cd C:\ProteinDock\backend; npm run dev" -ForegroundColor White
Write-Host "2. Check logs for: ✅ AutoDock Vina is available" -ForegroundColor White
Write-Host "3. Run a docking job from your mobile app!" -ForegroundColor White
