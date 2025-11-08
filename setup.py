"""Setup script for omislisi-accounting."""

from setuptools import setup, find_packages

setup(
    name="omislisi-accounting",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "lxml>=4.9.0",
        "pandas>=2.0.0",
        "python-dateutil>=2.8.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "omislisi-accounting=omislisi_accounting.cli.main:cli",
        ],
    },
)

