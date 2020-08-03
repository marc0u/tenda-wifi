import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tendawifi",
    version="0.0.2",
    author="Marco Urriola",
    author_email="marco.urriola@gmail.com",
    description="Python package that allows to manage tenda router AC15.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marc0u/tenda-wifi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
