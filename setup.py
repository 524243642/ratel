from setuptools import setup, find_packages

with open("README.md", "r") as h:
    README = h.read()

setup(
    name='ratel',
    version='0.2.17',
    description='Sorted data structure implementation by using skiplist and dict with Python',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/524243642/ratel',
    license='MIT',
    author='Bin Zhang',
    author_email='524243642@qq.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7'
    ],
    packages=find_packages(exclude=['tests*']),
    test_suite='tests',
    install_requires=[
        'numpy>=1.11.3'
    ]
)
