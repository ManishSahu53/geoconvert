from distutils.core import setup

setup(
    name='geoconvert',
    version='0.3.0',
    author='Manish Sahu',
    author_email='manish@indshine.com',
    url="https://gitlab.com/manish.indshine/geoconvert.git",
    description="A small geospatial dataset converter package",
    keywords=['geospatial', 'converter', 'vector'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    requires=[
        'shapely',
        'geopandas',
        'fiona'
    ],
    packages=['geoconvert']
)
