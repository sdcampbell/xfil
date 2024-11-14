from setuptools import setup

setup(
    name="xfil",
    version="0.1.2",
    py_modules=["xfil"],
    install_requires=[
        "requests>=2.32.3",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "xfil=xfil:main",
        ],
    },
    author="Steve Campbell",
    author_email="sdcampbell68@live.com",
    description="xfil is a tool that performs blind XPath exploitation and data exfiltration. This tool is created for penetration testers performing authorized security assessments.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sdcampbell/xfil",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)