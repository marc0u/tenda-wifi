import setuptools
import os
import sys

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('python -m twine upload dist/*')
    sys.exit()

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publishtest':
    os.system('python setup.py sdist bdist_wheel')
    os.system('python -m twine upload --repository testpypi dist/*')
    sys.exit()

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'reqtry>=0.0.2,<1.0'
]

setuptools.setup(
    name="tendawifi",
    version="0.2.0",
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
    install_requires=requires,
)
