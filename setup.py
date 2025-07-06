# setup.py

from setuptools import setup, find_packages

setup(
        name="pjg_library",
        version="0.1.0",
        packages=find_packages(),
        py_modules=[
            "SketchBorder",
            "utilityfunctions",
            ],
        install_requires=[
            # Dependencies go here
            ],
)
