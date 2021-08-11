from distutils.core import setup
setup(
    name='dgx',
    packages=['dgx'],
    version='0.1.1',
    license='MIT',
    description='Dealergeek API',
    author='Jeff Aguilar',
    author_email='jaguilar@dealergeek.com',
    url='https://github.com/jaguilar08/dgx',
    download_url='https://github.com/jaguilar08/dgx/archive/refs/tags/0.1.tar.gz',
    keywords=['DEALERGEEK', 'API'],
    install_requires=[
        'werkzeug',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
