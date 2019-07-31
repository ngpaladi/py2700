import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py2700",
    version="0.0.8",
    author="ngpaladi",
    author_email="py2700@noahpaladino.com",
    description="A Python package to interface with a Keithley 2700 multimeter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ngpaladi/py2700",
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