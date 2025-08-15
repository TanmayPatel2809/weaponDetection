from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name = "weaponDetection",
    version= "1.0",
    author = "Tanmay",
    packages= find_packages(),
    install_requires = requirements,
)