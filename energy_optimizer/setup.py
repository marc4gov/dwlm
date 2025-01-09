from setuptools import setup, find_packages

setup(
    name="energy_optimizer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'torch>=1.9.0',
        'numpy>=1.19.0',
        'pandas>=1.3.0',
        'matplotlib>=3.4.0',
        'scikit-learn>=0.24.0',
    ],
)