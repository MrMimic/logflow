import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LogFlow_Atos_Marc_Platini", # Replace with your own username
    version="0.0.4",
    author="Marc Platini",
    author_email="marc.platini@gmail.com",
    description="LogFlow aims at finding the correlations between the entries of logs files. It is split into 3 parts: a logparser, a relation learner and a tree building to show the correlations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: GPU",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
	"Topic :: Scientific/Engineering :: Artificial Intelligence",
	"Topic :: System",
	"Topic :: System :: Monitoring",
	"Topic :: System :: Systems Administration",
	"Topic :: Text Processing",
	"Topic :: Utilities"
    ],
    python_requires='==3.6.9',
    install_requires=["numpy>=1.18.5","cython>=0.29.19","typing>=3.7.4.1","loguru>=0.5.0","h5py>=2.10.0","tqdm>=4.46.1","torch>=1.5.0","torchvision>=0.6.0","word2vec>=0.11.1"]
)
