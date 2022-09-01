from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="data_visualization",
    version="0.2.0",
    packages=find_packages(include=["data_visualization"]),
    url="https://github.com/EPFL-RT-Driverless/data_visualization",
    license="MIT",
    classifiers=[
        # "Development Status :: 1 - Planning",
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Private :: Do Not Upload",
    ],
    requires=requirements,
)
