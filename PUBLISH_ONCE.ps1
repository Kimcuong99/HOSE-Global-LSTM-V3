$ErrorActionPreference = "Stop"
$Project = "C:\HOSE_GLOBAL_LSTM_V3"
$RepoName = "HOSE-Global-LSTM-V3"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " HOSE GLOBAL LSTM V3 - ONE-CLICK PUBLISHER"
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Project)) { throw "Khong tim thay thu muc $Project" }
Set-Location $Project

$required = @("app.py","requirements.txt",".gitignore","data\simulation\processed\hose_model_ready.csv")
foreach ($f in $required) {
    if (-not (Test-Path $f)) { throw "Thieu file bat buoc: $f" }
}

$ignore = Get-Content ".gitignore" -Raw
if ($ignore -notmatch '(?m)^!models/simulation/global_lstm_final\.keras\s*$') {
    Add-Content ".gitignore" "`n!models/simulation/global_lstm_final.keras"
}

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host "Chua co GitHub CLI. Dang thu cai bang winget..." -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host "Hay cai GitHub CLI tai https://cli.github.com/ roi chay lai file nay." -ForegroundColor Red
        Start-Process "https://cli.github.com/"
        Read-Host "Nhan Enter de ket thuc"
        exit 1
    }
    winget install --id GitHub.cli --exact --source winget --accept-package-agreements --accept-source-agreements
    Write-Host "Hay dong cua so nay, mo lai va chay PUBLISH_ONCE.bat mot lan nua." -ForegroundColor Yellow
    Read-Host "Nhan Enter de ket thuc"
    exit 0
}

git --version
gh --version

gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Can dang nhap GitHub. Trinh duyet se mo de xac thuc." -ForegroundColor Yellow
    gh auth login --web --git-protocol https
    if ($LASTEXITCODE -ne 0) { throw "Dang nhap GitHub chua thanh cong." }
}

$login = gh api user --jq .login
if (-not $login) { throw "Khong doc duoc GitHub username." }
$displayName = gh api user --jq '.name // .login'
$publicEmail = gh api user --jq '.email // empty'
if (-not $publicEmail) { $publicEmail = "$login@users.noreply.github.com" }
git config user.name "$displayName"
git config user.email "$publicEmail"

if (-not (Test-Path ".git")) { git init }
git branch -M main
git add -A

Write-Host ""
Write-Host "Cac file se duoc dua len repository PUBLIC:" -ForegroundColor Cyan
git status --short
Write-Host ""
Write-Host "Repository PUBLIC se cong khai source code va du lieu duoc git add." -ForegroundColor Yellow
$confirm = Read-Host "Nhap PUBLISH de tiep tuc"
if ($confirm -cne "PUBLISH") {
    Write-Host "Da huy. Khong co du lieu nao duoc push len GitHub."
    Read-Host "Nhan Enter de dong"
    exit 0
}

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Publish HOSE Global LSTM V3 prototype"
    if ($LASTEXITCODE -ne 0) { throw "Git commit that bai." }
}

$null = gh repo view "$login/$RepoName" --json name 2>$null
if ($LASTEXITCODE -eq 0) {
    $remote = git remote get-url origin 2>$null
    if (-not $remote) { git remote add origin "https://github.com/$login/$RepoName.git" }
    git push -u origin main
} else {
    gh repo create $RepoName --public --source . --remote origin --push --description "HOSE Global LSTM - Equity Analytics and Decision Support Prototype"
}
if ($LASTEXITCODE -ne 0) { throw "Push len GitHub that bai. Kiem tra thong bao o tren." }

$repoUrl = "https://github.com/$login/$RepoName"
Write-Host ""
Write-Host "Da dua source code len GitHub: $repoUrl" -ForegroundColor Green
Start-Process "https://share.streamlit.io/"
Write-Host ""
Write-Host "TREN STREAMLIT CLOUD:" -ForegroundColor Yellow
Write-Host "1. Dang nhap bang GitHub va Authorize Streamlit."
Write-Host "2. Chon Create app > Use existing repository."
Write-Host "3. Repository: $login/$RepoName"
Write-Host "4. Branch: main"
Write-Host "5. Main file path: app.py"
Write-Host "6. Custom subdomain: hose-global-lstm-v3 (neu con trong)."
Write-Host "7. Nhan Deploy."
Write-Host "Sau khi deploy, Streamlit se cap URL streamlit.app cho ban." -ForegroundColor Green
Read-Host "Nhan Enter de dong"
