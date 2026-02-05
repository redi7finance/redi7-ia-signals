# Script para subir cambios a GitHub
cd "c:\Users\Geiser\OneDrive\Documentos\REDI7 IA SEÑALES\redi7-ia-signals"

# Verificar cambios
Write-Host "Archivos modificados:" -ForegroundColor Yellow
git status --short

# Agregar archivo
Write-Host "`nAgregando auth.py..." -ForegroundColor Green
git add auth.py

# Commit
Write-Host "Haciendo commit..." -ForegroundColor Green
git commit -m "Fix: Agregar buffered=True a todos los cursores MySQL para evitar InternalError"

# Push
Write-Host "Subiendo a GitHub..." -ForegroundColor Green
git push origin main

Write-Host "`n✅ Cambios subidos exitosamente!" -ForegroundColor Green
Write-Host "Streamlit Cloud redesplegará automáticamente en ~2 minutos" -ForegroundColor Cyan
