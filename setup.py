from setuptools import find_packages, setup


with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='best',
    version='2.0.1',
    description='Bayesian estimation supersedes the t-test',
    author='Andrew Straw and Laszlo Treszkai',
    author_email='laszlo.treszkai@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/treszkai/best',
    package_dir={'': 'best'},
    packages=find_packages(where='src'),
    classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.5',
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib>=3.0.0',
        'pymc3<4.0',
    ],
)
