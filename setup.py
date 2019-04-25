import os

from setuptools import setup, find_packages, Extension


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    try:
        return read('README.md')
    except:
        return ''


from setuptools.command.build_ext import build_ext as _build_ext


class BuildExtWithoutPlatformSuffix(_build_ext):

    def get_ext_filename(self, ext_name):
        ext_path = ext_name.split('.')
        ext_suffix = '.so'
        return os.path.join(*ext_path) + ext_suffix


setup(
    name='ratel',
    keywords='ratel',
    version='0.5.1',
    description='Sorted data structure implementation by using skiplist and dict with Python and C',
    long_description=desc(),
    long_description_content_type="text/markdown",
    url='https://github.com/524243642/ratel',
    license='MIT',
    author='Bin Zhang',
    author_email='524243642@qq.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['tests*']),
    test_suite='tests',
    install_requires=[
        'numpy>=1.11.3'
    ],
    ext_modules=[
        Extension(
            'boost_collections.zskiplist._zskiplist',
            extra_compile_args=['-Wall'],
            sources=['boost_collections/zskiplist/t_zset.c']
        ),
    ],
    cmdclass={'build_ext': BuildExtWithoutPlatformSuffix},
)
