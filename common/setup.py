# common/setup.py
from setuptools import setup, find_packages

setup(
    name="common",
    version="0.1.0",
    packages=find_packages(),  # picks up common/ and any subpackages
)
