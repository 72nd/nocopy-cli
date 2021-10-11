import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nocopy-cli",
    version="0.1.0",
    author="72nd",
    author_email="msg@frg72.com",
    description="CLI client application for NocoDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/72nd/nocopy-cli",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points="""
        [console_scripts]
        nocopy=cli.cli:cli
    """,
    install_requires=[
        "click==8.0.1",
        "pyyaml==5.4.1",
        "python-Levenshtein==0.12.1",
        "nocopy==0.1.0",
        "thefuzz==0.19.0",
    ]
)
