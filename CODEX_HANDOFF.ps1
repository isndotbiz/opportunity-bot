# Opportunity Research Bot Codex Handoff Script
# Generates comprehensive handoff documentation

param(
    [string]$OutputDir = "D:\workspace\projects\opportunity-research-bot\codex_handoff",
    [switch]$IncludeVenv = $false
)

Write-Host "Opportunity Research Bot Codex Handoff Generator" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "D:\workspace\projects\opportunity-research-bot"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$handoffDir = "$OutputDir\$timestamp"

# Create handoff directory
New-Item -ItemType Directory -Path $handoffDir -Force | Out-Null
Write-Host "✓ Created handoff directory: $handoffDir" -ForegroundColor Green

# 1. Project Structure
Write-Host "`nAnalyzing project structure..." -ForegroundColor Cyan
$structure = @"
# Opportunity Research Bot - Project Structure
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Location:** $projectRoot

## Directory Tree

``````
opportunity-research-bot/
"@

Get-ChildItem -Path $projectRoot -Recurse -Depth 2 | ForEach-Object {
    $relativePath = $_.FullName.Replace($projectRoot, '').TrimStart('\')
    $indent = '  ' * ($relativePath.Split('\').Count - 1)
    $prefix = if ($_.PSIsContainer) { '├── ' } else { '│   ' }
    $structure += "`n$indent$prefix$($_.Name)"
}

$structure += @"

``````

## Key Files

### Configuration Files
"@

$configFiles = @('package.json', 'requirements.txt', 'config.json', '.env.example', 'README.md')
foreach ($file in $configFiles) {
    if (Test-Path "$projectRoot\$file") {
        $structure += "`n- **$file** - Found ✓"
    }
}

$structure += "`n`n### Source Code`n"

# List Python files
if (Test-Path "$projectRoot\*.py") {
    Get-ChildItem -Path $projectRoot -Filter "*.py" | ForEach-Object {
        $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
        $structure += "`n- **$($_.Name)** - $lines lines"
    }
}

$structure | Out-File -FilePath "$handoffDir\01_PROJECT_STRUCTURE.md" -Encoding UTF8
Write-Host "✓ Generated 01_PROJECT_STRUCTURE.md" -ForegroundColor Green

# 2. Dependencies
Write-Host "`nExtracting dependencies..." -ForegroundColor Cyan
$depsDoc = @"
# Dependencies Documentation
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

"@

if (Test-Path "$projectRoot\requirements.txt") {
    $depsDoc += @"
## Python Dependencies (requirements.txt)

``````
$(Get-Content "$projectRoot\requirements.txt" -Raw)
``````

## Installation

``````bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
``````

"@
}

if (Test-Path "$projectRoot\package.json") {
    $packageJson = Get-Content "$projectRoot\package.json" -Raw | ConvertFrom-Json
    $depsDoc += @"

## Node.js Dependencies (package.json)

### Dependencies
``````json
$($packageJson.dependencies | ConvertTo-Json -Depth 3)
``````

### DevDependencies
``````json
$($packageJson.devDependencies | ConvertTo-Json -Depth 3)
``````

## Installation

``````bash
npm install
# OR
yarn install
``````

"@
}

$depsDoc | Out-File -FilePath "$handoffDir\02_DEPENDENCIES.md" -Encoding UTF8
Write-Host "✓ Generated 02_DEPENDENCIES.md" -ForegroundColor Green

# 3. Configuration
Write-Host "`nDocumenting configuration..." -ForegroundColor Cyan
$configDoc = @"
# Configuration Guide
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Environment Variables

"@

if (Test-Path "$projectRoot\.env.example") {
    $configDoc += @"
### .env.example

``````
$(Get-Content "$projectRoot\.env.example" -Raw)
``````

### Setup Instructions

1. Copy ``.env.example`` to ``.env``
2. Fill in your API keys and credentials
3. Never commit ``.env`` to version control

"@
} else {
    $configDoc += "`n⚠ No .env.example found - create one if using environment variables`n"
}

if (Test-Path "$projectRoot\config.json") {
    $configDoc += @"

### config.json

``````json
$(Get-Content "$projectRoot\config.json" -Raw)
``````

"@
}

$configDoc | Out-File -FilePath "$handoffDir\03_CONFIGURATION.md" -Encoding UTF8
Write-Host "✓ Generated 03_CONFIGURATION.md" -ForegroundColor Green

# 4. Git History
Write-Host "`nExtracting Git history..." -ForegroundColor Cyan
try {
    Push-Location $projectRoot
    $gitLog = & git log --oneline --graph --decorate -30 2>&1
    $gitStatus = & git status 2>&1
    $gitBranch = & git branch -a 2>&1
    Pop-Location

    $gitDoc = @"
# Git Repository Information
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Current Status

``````
$gitStatus
``````

## Branches

``````
$gitBranch
``````

## Recent Commits (Last 30)

``````
$gitLog
``````

"@

    $gitDoc | Out-File -FilePath "$handoffDir\04_GIT_HISTORY.md" -Encoding UTF8
    Write-Host "✓ Generated 04_GIT_HISTORY.md" -ForegroundColor Green
} catch {
    Write-Host "⚠ Git not initialized" -ForegroundColor Yellow
}

# 5. Usage Guide
Write-Host "`nGenerating usage guide..." -ForegroundColor Cyan
$usageDoc = @"
# Usage Guide
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Quick Start

### 1. Setup Environment

``````bash
# Clone repository (if needed)
cd D:/workspace/projects
git clone [repository-url] opportunity-research-bot
cd opportunity-research-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys
``````

### 2. Run the Bot

``````bash
# Activate virtual environment if not already
.\venv\Scripts\activate

# Run main script
python main.py

# OR with specific parameters
python main.py --query "market research" --depth 3
``````

### 3. Common Commands

``````bash
# Run tests (if exists)
pytest

# Lint code
flake8 .

# Format code
black .

# Type checking
mypy .
``````

## Features

[List key features of the bot based on code analysis]

## API Integration

[Document any APIs being used - OpenAI, Anthropic, web scraping, etc.]

## Output

[Describe what the bot outputs - files, reports, database entries, etc.]

## Troubleshooting

### Virtual Environment Issues

``````bash
# Deactivate current venv
deactivate

# Remove venv
rm -r venv

# Recreate
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
``````

### API Key Errors

- Verify .env file exists
- Check API keys are valid
- Ensure no extra spaces in .env
- Restart terminal after .env changes

### Import Errors

``````bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
``````

"@

$usageDoc | Out-File -FilePath "$handoffDir\05_USAGE_GUIDE.md" -Encoding UTF8
Write-Host "✓ Generated 05_USAGE_GUIDE.md" -ForegroundColor Green

# 6. Development Guide
Write-Host "`nGenerating development guide..." -ForegroundColor Cyan
$devDoc = @"
# Development Guide
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Development Workflow

### 1. Create Feature Branch

``````bash
git checkout -b feature/your-feature-name
``````

### 2. Make Changes

- Edit code
- Add tests
- Update documentation

### 3. Test Locally

``````bash
# Run tests
pytest

# Check code quality
flake8 .
black . --check
``````

### 4. Commit Changes

``````bash
git add .
git commit -m "feat: description of your feature"
``````

### 5. Push and Create PR

``````bash
git push origin feature/your-feature-name
# Create Pull Request on GitHub/GitLab
``````

## Code Style

- Follow PEP 8 for Python
- Use Black for formatting
- Use type hints
- Write docstrings for functions
- Add unit tests for new features

## Testing

``````bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
pytest --cov=.

# Generate coverage report
pytest --cov=. --cov-report=html
``````

## Debugging

``````python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use built-in breakpoint() in Python 3.7+
breakpoint()

# Run with debugger
python -m pdb main.py
``````

## Best Practices

1. **Always use virtual environment**
2. **Keep dependencies up to date**
3. **Write tests for new features**
4. **Document code and APIs**
5. **Use environment variables for secrets**
6. **Never commit .env or credentials**

"@

$devDoc | Out-File -FilePath "$handoffDir\06_DEVELOPMENT.md" -Encoding UTF8
Write-Host "✓ Generated 06_DEVELOPMENT.md" -ForegroundColor Green

# 7. Master Index
Write-Host "`nGenerating master index..." -ForegroundColor Cyan
$indexDoc = @"
# Opportunity Research Bot - Codex Handoff
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Project:** Opportunity Research Bot
**Location:** D:\workspace\projects\opportunity-research-bot

---

## Quick Overview

Opportunity Research Bot is an automated research tool designed to find and analyze business opportunities, market trends, and competitive intelligence.

### Technology Stack

- **Language:** Python
- **Key Libraries:** [Based on requirements.txt]
- **APIs:** [OpenAI/Anthropic/Other - check code]
- **Data Storage:** [Database/Files - check code]

---

## Documentation Files

1. **01_PROJECT_STRUCTURE.md** - Directory layout and file organization
2. **02_DEPENDENCIES.md** - Python packages and installation guide
3. **03_CONFIGURATION.md** - Environment variables and settings
4. **04_GIT_HISTORY.md** - Repository information and recent commits
5. **05_USAGE_GUIDE.md** - How to run and use the bot
6. **06_DEVELOPMENT.md** - Development workflow and best practices

---

## Quick Start for New Developer

### 1. Clone & Setup

``````bash
cd D:/workspace/projects/opportunity-research-bot

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your credentials
``````

### 2. Run

``````bash
python main.py
``````

### 3. Develop

``````bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, test, commit
git add .
git commit -m "feat: my feature"
git push origin feature/my-feature
``````

---

## Project Status

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Git Status:** [Check 04_GIT_HISTORY.md]
**Dependencies:** [Check 02_DEPENDENCIES.md]

---

## Important Files

- **main.py** - Entry point
- **requirements.txt** - Python dependencies
- **.env** - Environment configuration (DO NOT COMMIT)
- **README.md** - Project documentation

---

## Contact & Support

**Project Owner:** [Your Name/Team]
**Repository:** D:\workspace\projects\opportunity-research-bot
**Generated By:** Codex Handoff Script

---

**Next Steps:**

1. Review all 6 documentation files
2. Set up development environment
3. Run initial tests
4. Review recent commits (04_GIT_HISTORY.md)
5. Check configuration (03_CONFIGURATION.md)

---

**Handoff Complete!** 🎉
All documentation generated in: $handoffDir

"@

$indexDoc | Out-File -FilePath "$handoffDir\00_INDEX.md" -Encoding UTF8
Write-Host "✓ Generated 00_INDEX.md" -ForegroundColor Green

# Summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Codex Handoff Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation generated in:" -ForegroundColor White
Write-Host "  $handoffDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Files created:" -ForegroundColor White
Write-Host "  00_INDEX.md - Master overview" -ForegroundColor Yellow
Write-Host "  01_PROJECT_STRUCTURE.md" -ForegroundColor Yellow
Write-Host "  02_DEPENDENCIES.md" -ForegroundColor Yellow
Write-Host "  03_CONFIGURATION.md" -ForegroundColor Yellow
Write-Host "  04_GIT_HISTORY.md" -ForegroundColor Yellow
Write-Host "  05_USAGE_GUIDE.md" -ForegroundColor Yellow
Write-Host "  06_DEVELOPMENT.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Start with: 00_INDEX.md" -ForegroundColor Cyan
Write-Host ""
