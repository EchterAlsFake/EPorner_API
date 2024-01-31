from setuptools import setup, find_packages

setup(
    name="Eporner_API",
    version="1.2",
    packages=find_packages(),
    install_requires=[
        "requests", "bs4", "lxml"
    ],
    entry_points={
        'console_scripts': [
            # If you want to create any executable scripts
        ],
    },
    author="Johannes Habel",
    author_email="EchterAlsFake@proton.me",
    description="A Python API for the Porn Site Eporner.com",
    long_description=open('/home/asuna/PycharmProjects/EPorner_API/README.md').read(),
    long_description_content_type='text/markdown',
    license="LGPLv3",
    url="https://github.com/EchterAlsFake/EPorner_API",
    classifiers=[
        # Classifiers help users find your project on PyPI
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python",
    ],
)
