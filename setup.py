import setuptools

setuptools.setup(
    name='lokii',
    packages=['lokii'],
    version='0.0.1',
    description='CSV dataset generator',
    author='Package Author',
    author_email='you@youremail.com',
    url='http://path-to-my-packagename',
    py_modules=['lokii'],
    install_requires=[
        'faker',
        'slugify'
    ],
    license='MIT License',
    zip_safe=False,
    keywords='boilerplate package',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
    ])
