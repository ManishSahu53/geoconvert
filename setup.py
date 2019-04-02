import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geoConvert",
    version="0.1.0",
    author="Manish Sahu",
    author_email="manish@indshine.com",
    description="A small geospatial dataset converter package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/manish.indshine/geoconvert.git",
    install_requires=[
          'geopandas',
          'fiona',
          'shapely'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
