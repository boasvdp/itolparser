import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='itolparser',
     version='0.1.3',
     scripts=['itolparser'] ,
     author="Boas van der Putten",
     author_email="boas.vanderputten@amsterdamumc.nl",
     description="Small script to produce iTOL colorstrip metadata files from a table",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/boasvdp/itolparser",
     packages=setuptools.find_packages(),
     install_requires=['colorbrewer', 'pandas', 'numpy'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
