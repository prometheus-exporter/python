from setuptools import find_packages, setup

setup(
    name="prometheus-exporter",
    version="1.0.0",
    description="prometheus exporter",
    url="https://github.com/prometheus-exporter/python",
    long_description="",
    long_description_content_type="text/markdown",
    author="heaven-chp",
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
)
