from setuptools import setup

setup(
    name="allocation",
    version="0.1",
    packages=["allocation"],
    scripts=[
        "bin/allocate-from-csv",
    ],
)
