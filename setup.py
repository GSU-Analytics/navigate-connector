from setuptools import setup, find_packages

# Read README with explicit UTF-8 encoding
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except:
    # Fallback if there's still an issue
    long_description = "A Python connector for interacting with the Navigate API and SFTP service."

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
    long_description=long_description,
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