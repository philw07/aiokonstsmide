from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="aiokonstsmide",
    version="0.1.0",
    description="Library to communicate with Konstsmide Bluetooth powered string lights",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="philw07",
    author_email="phil.w07@gmail.com",
    url="https://github.com/philw07/aiokonstsmide",
    license="MIT",
    license_file="LICENSE",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.10",
    keywords="konstsmide bluetooth string light ble",
)
