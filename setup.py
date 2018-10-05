from distutils.core import setup

setup(
    name='socksproxy',
    version='1.0.0',
    packages=['socksproxy'],
    url='https://github.com/UltrafunkAmsterdam/socksproxy',
    license='MIT',
    author='UltrafunkAmsterdam',
    author_email='info@ultrafunk.nl',
    description='A flexible, asynchronous SOCKS 4/4A/5/5H proxy server written in pure Python',
    entry_points = {
        'console_scripts': ['socksproxy = __main__:main'],
    }
)
