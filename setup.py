from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as fh:
    long_description = fh.read()
setup(
    name='django-multi-tenancy',
    version='0.1.3',
    keywords=['python', 'django','mult-tenant'],
    description='Django multi tenant implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT Licence', 
    url='https://github.com/AnsGoo/djangoMultiTenant',
    author='ansgoo',
    author_email='haiven_123@163.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
        'django>=3.2.0',
        'pycryptodome>=3.10.1',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: MacOS X',
     ]
)
