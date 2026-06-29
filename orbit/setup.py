from setuptools import setup, find_packages

setup(
    name="orbit-cli",
    version="0.1.0",
    packages=find_packages(),
    package_data={"orbit": ["skills/*.md"]},
    entry_points={"console_scripts": ["orbit=orbit.cli:main"]},
    python_requires=">=3.10",
    install_requires=["pyyaml"],
    description="Second Brain Agent Orchestrator CLI",
    author="Gaurav Agarwal",
    url="https://github.com/GauravAgarwalGarg/autonomy-loops",
)
