from setuptools import setup, find_packages

setup(
    name="navigate-connector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "keyring",
        "paramiko"
    ],
    author="Isaac Kerson",
    author_email="ikerson@gsu.edu",
    description="A Python connector for interacting with the Navigate API and SFTP service.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GSU-Analytics/navigate-connector",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
