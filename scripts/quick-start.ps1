# DevSecOps Project Quick Start Script for Windows
# This script helps set up the development environment and run initial security scans

param(
    [switch]$SkipDocker,
    [switch]$SkipTests,
    [switch]$SkipSecurity
)

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $SuccessColor
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $WarningColor
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $ErrorColor
}

function Test-Python {
    Write-Status "Checking Python installation..."
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
            return $true
        }
    }
    catch {
        Write-Error "Python is required but not installed."
        Write-Host "Please install Python 3.8 or later from https://python.org"
        return $false
    }
}

function Test-Docker {
    Write-Status "Checking Docker installation..."
    try {
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker found: $dockerVersion"
            return $true
        }
    }
    catch {
        Write-Warning "Docker not found. Some features will not be available."
        return $false
    }
}

function Setup-PythonEnvironment {
    Write-Status "Setting up Python virtual environment..."
    
    if (-Not (Test-Path "venv")) {
        python -m venv venv
        Write-Success "Virtual environment created"
    }
    else {
        Write-Status "Virtual environment already exists"
    }
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies
    Write-Status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    Write-Success "Python environment setup complete"
}

function Invoke-SecurityScans {
    if ($SkipSecurity) {
        Write-Warning "Skipping security scans as requested"
        return
    }
    
    Write-Status "Running security scans..."
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Run Bandit security scan
    Write-Status "Running Bandit security scan..."
    try {
        bandit -r src/ -f json -o bandit-report.json
        bandit -r src/ -f txt -o bandit-report.txt
    }
    catch {
        Write-Warning "Bandit scan completed with warnings"
    }
    
    # Run Safety check
    Write-Status "Running Safety dependency check..."
    try {
        safety check --json --output safety-report.json
        safety check --output safety-report.txt
    }
    catch {
        Write-Warning "Safety check completed with warnings"
    }
    
    Write-Success "Security scans completed"
}

function Invoke-Tests {
    if ($SkipTests) {
        Write-Warning "Skipping tests as requested"
        return
    }
    
    Write-Status "Running tests..."
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Run pytest with coverage
    python -m pytest tests/ --cov=src --cov-report=xml --cov-report=html --junitxml=test-results.xml
    
    Write-Success "Tests completed"
}

function Build-DockerImage {
    if ($SkipDocker -or -Not (Test-Docker)) {
        Write-Warning "Skipping Docker image build"
        return
    }
    
    Write-Status "Building Docker image..."
    docker build -t my-devsecops-app:latest -f docker/Dockerfile .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    }
    else {
        Write-Error "Docker image build failed"
    }
}

function New-SecurityReport {
    Write-Status "Generating security report..."
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    python security/generate_security_report.py
    
    Write-Success "Security report generated"
}

function Start-DevEnvironment {
    if ($SkipDocker -or -Not (Test-Docker)) {
        Write-Warning "Skipping development environment setup"
        return
    }
    
    Write-Status "Setting up development environment with Docker..."
    
    # Start development services
    docker-compose -f docker/docker-compose.yml up -d redis postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Development services started"
        Write-Status "Redis available at: localhost:6379"
        Write-Status "PostgreSQL available at: localhost:5432"
    }
    else {
        Write-Error "Failed to start development services"
    }
}

function Show-NextSteps {
    Write-Host ""
    Write-Success "DevSecOps project setup completed!"
    Write-Host ""
    Write-Host "📚 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Review the generated security report: security-reports\security-summary.html"
    Write-Host "2. Set up Jenkins pipeline using the provided Jenkinsfile"
    Write-Host "3. Configure monitoring and alerting"
    Write-Host "4. Review and customize security policies"
    Write-Host ""
    Write-Host "📖 Documentation:" -ForegroundColor Yellow
    Write-Host "- README.md - Project overview and setup instructions"
    Write-Host "- jenkins\jenkins-setup.md - Jenkins configuration guide"
    Write-Host "- security\security-policy.toml - Security policy configuration"
    Write-Host ""
    Write-Host "🔧 Development Commands:" -ForegroundColor Yellow
    Write-Host "- Run application: python src\app.py"
    Write-Host "- Run tests: pytest tests\"
    Write-Host "- Security scan: bandit -r src\"
    Write-Host "- Docker build: docker build -t my-devsecops-app -f docker\Dockerfile ."
    Write-Host ""
}

# Main execution
function Main {
    Write-Host ""
    Write-Host "🚀 DevSecOps Project Quick Start" -ForegroundColor Magenta
    Write-Host "================================" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Status "Starting DevSecOps project setup..."
    Write-Host ""
    
    # Check prerequisites
    $pythonAvailable = Test-Python
    $dockerAvailable = Test-Docker
    
    if (-Not $pythonAvailable) {
        Write-Error "Python is required. Please install Python and try again."
        exit 1
    }
    
    Write-Host ""
    
    # Setup environment
    Setup-PythonEnvironment
    Write-Host ""
    
    # Run tests
    Invoke-Tests
    Write-Host ""
    
    # Run security scans
    Invoke-SecurityScans
    Write-Host ""
    
    # Generate security report
    New-SecurityReport
    Write-Host ""
    
    # Build Docker image
    Build-DockerImage
    Write-Host ""
    
    # Setup development environment
    Start-DevEnvironment
    Write-Host ""
    
    # Show next steps
    Show-NextSteps
}

# Check execution policy
$currentPolicy = Get-ExecutionPolicy
if ($currentPolicy -eq "Restricted") {
    Write-Warning "PowerShell execution policy is restricted."
    Write-Host "Run the following command as Administrator to allow script execution:"
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    Write-Host ""
    Write-Host "Or run this script with:"
    Write-Host "powershell -ExecutionPolicy Bypass -File quick-start.ps1"
    exit 1
}

# Run main function
Main
