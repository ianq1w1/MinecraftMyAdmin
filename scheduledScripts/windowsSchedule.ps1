# Configurações
$KEY = "VPS/KEY/PATH"
$VPS = "VPS_ADDRESS"
$SNAPSHOT_DIR = "LOCAL/COMPRESSED/DB"
$DB_DIR = "LOCAL/UNCOMPRESSED/DB"

New-Item -ItemType Directory -Force -Path $SNAPSHOT_DIR

# Limpa snapshots antigos locais antes de baixar
Write-Host "Limpando snapshots antigos..."
Remove-Item -Force "$SNAPSHOT_DIR\*.tar.gz" -ErrorAction SilentlyContinue

# Puxa só o snapshot mais recente da VPS
Write-Host "Buscando snapshot da VPS..."
scp -i $KEY "${VPS}:/VPS/SNAPSHOTS/PATH/*.tar.gz" $SNAPSHOT_DIR

# Pega o arquivo
$latest = Get-ChildItem $SNAPSHOT_DIR -Filter "*.tar.gz" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Limpa o db antigo completamente
Write-Host "Limpando db antigo..."
Remove-Item -Recurse -Force $DB_DIR -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $DB_DIR

# Extrai
Write-Host "Descompactando $($latest.Name)..."
tar -xzf $latest.FullName -C $DB_DIR

Write-Host "executando arquivo python do ETL"
#python LOCAL/ETL/PYTHONFILE.PY

Write-Host "Concluído!"