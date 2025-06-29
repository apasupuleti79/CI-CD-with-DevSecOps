#!/bin/bash

# DevSecOps Project Quick Start Script
# This script helps set up the development environment and run initial security scans

set -e

echo "🚀 DevSecOps Project Quick Start"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not installed."
        exit 1
    fi
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker found: $DOCKER_VERSION"
    else
        print_warning "Docker not found. Some features will not be available."
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup complete"
}

# Run security scans
run_security_scans() {
    print_status "Running security scans..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run Bandit security scan
    print_status "Running Bandit security scan..."
    bandit -r src/ -f json -o bandit-report.json || true
    bandit -r src/ -f txt -o bandit-report.txt || true
    
    # Run Safety check
    print_status "Running Safety dependency check..."
    safety check --json --output safety-report.json || true
    safety check --output safety-report.txt || true
    
    print_success "Security scans completed"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run pytest with coverage
    python -m pytest tests/ --cov=src --cov-report=xml --cov-report=html --junitxml=test-results.xml
    
    print_success "Tests completed"
}

# Build Docker image
build_docker_image() {
    if command -v docker &> /dev/null; then
        print_status "Building Docker image..."
        docker build -t my-devsecops-app:latest -f docker/Dockerfile .
        print_success "Docker image built successfully"
    else
        print_warning "Docker not available, skipping image build"
    fi
}

# Generate security report
generate_security_report() {
    print_status "Generating security report..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    python security/generate_security_report.py
    
    print_success "Security report generated"
}

# Setup development environment
setup_dev_environment() {
    if command -v docker &> /dev/null; then
        print_status "Setting up development environment with Docker..."
        
        # Start development services
        docker-compose -f docker/docker-compose.yml up -d redis postgres
        
        print_success "Development services started"
        print_status "Redis available at: localhost:6379"
        print_status "PostgreSQL available at: localhost:5432"
    else
        print_warning "Docker not available, skipping development environment setup"
    fi
}

# Main execution
main() {
    echo
    print_status "Starting DevSecOps project setup..."
    echo
    
    # Check prerequisites
    check_python
    check_docker
    echo
    
    # Setup environment
    setup_python_env
    echo
    
    # Run tests
    run_tests
    echo
    
    # Run security scans
    run_security_scans
    echo
    
    # Generate security report
    generate_security_report
    echo
    
    # Build Docker image
    build_docker_image
    echo
    
    # Setup development environment
    setup_dev_environment
    echo
    
    print_success "DevSecOps project setup completed!"
    echo
    echo "📚 Next Steps:"
    echo "1. Review the generated security report: security-reports/security-summary.html"
    echo "2. Set up Jenkins pipeline using the provided Jenkinsfile"
    echo "3. Configure monitoring and alerting"
    echo "4. Review and customize security policies"
    echo
    echo "📖 Documentation:"
    echo "- README.md - Project overview and setup instructions"
    echo "- jenkins/jenkins-setup.md - Jenkins configuration guide"
    echo "- security/security-policy.toml - Security policy configuration"
    echo
    echo "🔧 Development Commands:"
    echo "- Run application: python src/app.py"
    echo "- Run tests: pytest tests/"
    echo "- Security scan: bandit -r src/"
    echo "- Docker build: docker build -t my-devsecops-app -f docker/Dockerfile ."
    echo
}

# Run main function
main "$@"
