import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyApraisal",
    version="0.1.1",
    author="Zack Dai",
    author_email="zdai@brocku.ca",
    description="A package to scrape data from the easy appraisal",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/ZackAnalysis/easyApraisal",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*.json", "*.xlsx"]},
    install_requires=['pandas','openpyxl','selenium','requests']
)