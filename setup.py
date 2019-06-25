import re
from io import open

from setuptools import find_packages, setup

# Get the long description from the relevant file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

with open('geoconvert/VERSION') as version_file:
    __version__=version_file.read().strip()

setup(name='geoconvert',
        version=__version__,
        description="A micro geospatial dataset converter package",
        long_description=long_description,
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        ],
        keywords='GIS, converter, geospatial',
        author="Manish Sahu",
        author_email='manish.sahu.civ13@iitbhu.ac.in',
        url='https://github.com/ManishSahu53/geoconvert.git',
        license='MIT',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        include_package_data=True,
        zip_safe=False,
        install_requires=open('requirements.txt').read().splitlines(),
        extras_require={
            'dev': [
                'numpy',
                'argparse',
                'tqdm'
            ],
        },
)

# MD to  RST
# pandoc --from=markdown --to=rst --output=README.rst README.md