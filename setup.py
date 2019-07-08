import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geo_garry",
    version="1.0.8",
    author="Sergey Retivykh",
    author_email="s.retivykh@redmadrobot.com",
    description="Geocoding and reverse geocoding, distance calculations. Google Maps implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.redmadrobot.com/Backend/geo_garry.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Geo Service',
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Shapely~=1.5',
        'scipy~=1.1.0',
        'dataclasses==0.6',
    ],
)
