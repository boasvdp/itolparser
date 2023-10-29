import setuptools

from itolparser.version import __version__, __author__, __description__, __email__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="itolparser",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boasvdp/itolparser",
    packages=setuptools.find_packages(),
    install_requires=["colorbrewer", "pandas", "numpy"],
    python_requires=">=3",
    entry_points={
        "console_scripts": [
            "itolparser = itolparser.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
