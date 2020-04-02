from setuptools import setup, find_packages

setup(
    name='AnalisiCovid19Italia',
    version='1.0',
    packages=find_packages(),
    url='',
    license='LGPLv3',
    author='Andrea Bruno',
    author_email='',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='Analisi dei dati giornalieri forniti dal Dipartimento di Protezione Civile Italiana in merito all\'epidemia di Covid 19',
    install_requires=['pandas', 'numpy', 'git', 'scikit-learn', 'matplotlib']
)
