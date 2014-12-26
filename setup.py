import setuptools

setuptools.setup(
    name="wapu",
    version="0.1.0",
    url="http://github.com/pperez/wapu",

    author="Patricio Pérez",
    author_email="patricio.perez@ceinf.cl",
    maintainer="Patricio Pérez",
    maintainer_email="patricio.perez@ceinf.cl",

    description="Colección de wrappers para apps UTEM",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
