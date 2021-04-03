from setuptools import setup, find_packages
from shutil import copyfile
import os, platform


def get_long_description():
    return ""
    # this_directory = os.path.abspath(os.path.dirname(__file__))
    # with open(os.path.join(this_directory, 'docs/README.md')) as f:
    #     long_description = f.read()
    #     return long_description


def copy_docs():
    return
    # docs_dir = "pythonMuse/docs"
    # if not os.path.exists(docs_dir):
    #     os.makedirs(docs_dir)
    #
    # copyfile("docs/Header.png", docs_dir + "/Header.png")
    # copyfile("docs/README.md", docs_dir + "/README.md")


copy_docs()
long_description = get_long_description()

setup(
    name="pythonMuse",
    version="1.0.0",
    description="A Python library for connecting and communicate with MUSE headbands. "
                "Uses Bleak as the underlying Bluetooth interface.",
    keywords="muse lsl eeg ble neuroscience matlab UDP",
    url="https://github.com/bardiabarabadi/PythonMuse",
    author="Bardia Barabadi",
    author_email="bardiabarabadi@uvic.ca",
    license="MIT",
    entry_points={},
    packages=['pythonMuse'],
    package_data={},
    include_package_data=True,
    zip_safe=False,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "bitstring",
        "numpy",
        "seaborn",
        "pexpect",
        "bleak",
        "pygments",
        "pyserial",
        "esptool",
        "nest_asyncio",
        "scipy"
    ]
    ,
    classifiers=[
        # How mature is this project?  Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        "Topic :: Software Development",
        # Specify the Python versions you support here.  In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python",
    ],
)
