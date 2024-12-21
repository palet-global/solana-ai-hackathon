from version import palet_api_version
from setuptools import find_packages, setup

def get_requirements(path: str):
    return [l.strip() for l in open(path)]

setup(
    name="palet-api",
    version=palet_api_version,
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)