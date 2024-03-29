from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()
    # delete lines starting with # and empty lines
    requirements = [
        r
        for r in requirements
        if not (r.startswith("#") or r.startswith("-e git+") or r.startswith("git+"))
    ]

setup(
    name="data_visualization",
    version="1.1.3",
    packages=find_packages(include=["data_visualization"]),
    url="https://github.com/EPFL-RT-Driverless/data_visualization",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Private :: Do Not Upload",
    ],
    install_requires=requirements,
)
