"""A python testcontainers example.

See:
https://github.com/testcontainers/testcontainers-python
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

def read_requirements(requirement_file):
    with (here / requirement_file).open(mode='r', encoding='utf-8') as input_file:
        return [i.strip() for i in input_file if not i.strip().startswith('#')]

INSTALL_REQUIRES = read_requirements("requirements.txt")
TEST_REQUIRES = read_requirements("requirements_test.txt")

setup(
    name='python-testcontainers-smtp-example',

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    version='1.0.0',

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='Python testcontainers SMTP example',

    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://gitlab.com/ipsedixit-org/python-testcontainers-smtp-example',
    author='ipsedixit',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
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
        'License :: OSI Approved :: Apache Licenze 2.0',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    # This field adds keywords for your project which will appear on the
    # project page.
    keywords='sample, testcontainers, smtp, development',

    packages=find_packages(where='python_testcontainers_smtp_example'),

    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. See
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.9, <4',

    install_requires=INSTALL_REQUIRES,
    extras_require={
        'test': TEST_REQUIRES,
    },

)
