from setuptools import setup, find_packages

setup(
    name='uitools',
    version='0.1-dev',
    description='Collection of general tools and utilities for working with and testing Qt tools.',
    url='https://github.com/westernx/uitools',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    
    author='Mike Boers',
    author_email='uitools@mikeboers.com',
    license='BSD-3',
    
    metatools_apps=[{
        'name': 'notifications',
        'identifier': 'com.westernx.uitools.notifications',
        'target_type': 'entrypoint',
        'target': 'uitools.notifications._main:main_bundle',
        'use_compiled_bootstrap': True,
        'python_path': [
            '/home/mboers/dev/uitools',
            '/home/mboers/dev/metatools',
        ],
        'bundle_path': 'build/lib/uitools/notifications/Python Notifications.app',
    }],

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
