from setuptools import setup, find_packages

setup(
    name="devsecops-demo-app",
    version="1.0.0",
    description="A DevSecOps demonstration application",
    author="DevSecOps Team",
    author_email="team@company.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.3.0",
        "Werkzeug>=2.3.0",
        "requests>=2.31.0",
        "gunicorn>=21.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "isort>=5.12.0",
        ],
        "security": [
            "bandit>=1.7.0",
            "safety>=2.3.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
