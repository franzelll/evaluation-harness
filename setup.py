#!/usr/bin/env python3
"""
Setup script für die Evaluation Harness
"""

from setuptools import setup, find_packages
from pathlib import Path

# README lesen
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Version aus __init__.py lesen (falls vorhanden)
version = "1.0.0"

# Requirements aus requirements.txt lesen
def read_requirements():
    requirements_file = this_directory / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Entferne Kommentare und optionale Pakete
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    requirements.append(line)
            return requirements
    return []

setup(
    name="evaluation-harness",
    version=version,
    author="Evaluation Harness Team",
    author_email="team@evaluation-harness.org",
    description="Eine professionelle Evaluation-Pipeline für Text-Vereinfachung",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/evaluation-harness",
    project_urls={
        "Bug Tracker": "https://github.com/your-org/evaluation-harness/issues",
        "Documentation": "https://github.com/your-org/evaluation-harness#readme",
        "Source Code": "https://github.com/your-org/evaluation-harness",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gpu": [
            "torch>=2.0.0+cu118",
            "accelerate>=0.20.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "torch>=2.0.0+cu118",
            "accelerate>=0.20.0",
            "bitsandbytes>=0.41.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "evaluate=evaluate:main",
            "eval-harness=evaluate:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    data_files=[
        ("configs", [
            "configs/default.yaml",
            "configs/models/base_phi4.yaml",
            "configs/models/finetuned_klexikon.yaml",
            "configs/tasks/simplify_de.yaml",
        ]),
        ("data", [
            "data/test.jsonl",
            "data/dev.jsonl",
        ]),
    ],
    keywords=[
        "evaluation", "nlp", "text-simplification", "metrics", "statistics",
        "machine-learning", "transformer", "german", "readability"
    ],
    zip_safe=False,
)
