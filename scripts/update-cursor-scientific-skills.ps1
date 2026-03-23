# Update Cursor Scientific Skills from K-Dense-AI/claude-scientific-skills
# Run from project root or any directory. Refreshes repo and copies to ~/.cursor/skills/

$RepoUrl = "https://github.com/K-Dense-AI/claude-scientific-skills.git"
$CloneDir = Join-Path $env:TEMP "claude-scientific-skills"
$SkillsSource = Join-Path $CloneDir "scientific-skills"
$CursorSkills = Join-Path $env:USERPROFILE ".cursor\skills"

Write-Host "Updating Claude Scientific Skills for Cursor..." -ForegroundColor Cyan

# Clone or pull
if (Test-Path $CloneDir) {
    Write-Host "Pulling latest from repository..." -ForegroundColor Yellow
    Push-Location $CloneDir
    git pull --depth 1 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { git fetch --depth 1; git reset --hard origin/main }
    Pop-Location
}
else {
    Write-Host "Cloning repository..." -ForegroundColor Yellow
    git clone --depth 1 $RepoUrl $CloneDir
}

if (-not (Test-Path $SkillsSource)) {
    Write-Host "ERROR: scientific-skills folder not found." -ForegroundColor Red
    exit 1
}

# Copy each skill folder into Cursor skills (overwrite)
$count = 0
Get-ChildItem $SkillsSource -Directory | ForEach-Object {
    $dest = Join-Path $CursorSkills $_.Name
    Copy-Item $_.FullName -Destination $dest -Recurse -Force
    $count++
}
Write-Host "Copied $count skills to $CursorSkills" -ForegroundColor Green
Write-Host "Restart Cursor (or reload window) to pick up changes." -ForegroundColor Cyan
