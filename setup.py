import setuptools
import json

with open('package_info.json') as f:
  package_info = json.load(f)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=package_info["name"],
    version=package_info["version"],
    author=package_info["author"],
    author_email="py2700@noahpaladino.com",
    description="A Python package to interface with a Keithley 2700 multimeter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=package_info["url"],
    packages=setuptools.find_packages(),
    install_requires=[
        'PyVISA',
        'PyVISA-py',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)