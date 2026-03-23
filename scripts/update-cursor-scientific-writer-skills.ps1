# Update Cursor Scientific Writer skills from K-Dense-AI/claude-scientific-writer
# Copies skills/ from the repo to ~/.cursor/skills/ (writing-focused: papers, grants, posters, clinical reports, etc.)

$RepoUrl = "https://github.com/K-Dense-AI/claude-scientific-writer.git"
$CloneDir = Join-Path $env:TEMP "claude-scientific-writer"
$SkillsSource = Join-Path $CloneDir "skills"
$CursorSkills = Join-Path $env:USERPROFILE ".cursor\skills"

Write-Host "Updating Claude Scientific Writer skills for Cursor..." -ForegroundColor Cyan

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
    Write-Host "ERROR: skills folder not found." -ForegroundColor Red
    exit 1
}

$count = 0
Get-ChildItem $SkillsSource -Directory | ForEach-Object {
    Copy-Item $_.FullName -Destination (Join-Path $CursorSkills $_.Name) -Recurse -Force
    $count++
}
Write-Host "Copied $count Scientific Writer skills to $CursorSkills" -ForegroundColor Green
Write-Host "Restart Cursor (or reload window) to pick up changes." -ForegroundColor Cyan
