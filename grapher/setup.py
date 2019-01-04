from setuptools import setup, find_packages

VERSION = '0.0.1'

# @see https://github.com/pypa/sampleproject/blob/master/setup.py
setup(
    name='grapher',
    version=VERSION,
    author='Maciej Brencz',
    author_email='maciej.brencz@gmail.com',
    license='MIT',
    packages=find_packages(),
    extras_require={
        'dev': [
            'coverage==4.5.2',
            'pylint>=1.9.2, <=2.1.1',  # 2.x branch is for Python 3
            'pytest==4.0.0',
        ]
    },
    install_requires=[
        'data-flow-graph==0.4',  # for generating dot files (graphviz) that are visualized as a graph
        'mwclient==0.9.3',
        'redisgraph==1.5',
        'requests==2.21.0',
    ],
    entry_points={
        'console_scripts': [
            'index_football_wiki=grapher.scripts.index_football_wiki:index',
        ],
    }
)
