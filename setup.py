import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gt-examcard-parser",
    version="0.0.2",
    author="Martin Bührer",
    author_email="info@gyrotools.com",
    description="Parser for Philips ExamCards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gyrotools/gt-examcard-parser",
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    python_requires='>=3.6.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
