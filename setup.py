from setuptools import setup

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description=f.read()

setup(
    name="tornado-irc",
    version='0.0.1',
    description="IRC Client for Tornado",
    long_description=long_description,
    author="INADA Naoki",
    author_email="songofacandy@gmail.com",
    requires=["tornado"],
    py_modules=['tornado_irc'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
