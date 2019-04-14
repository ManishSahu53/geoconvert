from distutils.core import setup
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='geoconvert',
    version='0.2.0',
    author='Manish Sahu',
    author_email='manish@indshine.com',
    url="https://gitlab.com/manish.indshine/geoconvert.git",
    description="A small geospatial dataset converter package",
    long_description=long_description,
    keywords=['geospatial', 'converter', 'vector'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    packages=['geoconvert']
)
