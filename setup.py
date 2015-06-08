import os
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
        'name': 'WesternX-Notifications.app',
        'identifier': 'com.westernx.uitools.notifications',
        'target_type': 'entrypoint',
        'target': 'uitools.notifications._main:noop',
        'use_compiled_bootstrap': True,
        
        # Bake in the development path if we are in dev mode.
        'python_path': os.environ['PYTHONPATH'].split(':') if '--dev' in os.environ.get('VEE_EXEC_ARGS', '') else [],

        # Place us into the global applications folder if in vee.
        'bundle_path': (
            os.path.join(os.environ['VEE'], 'Applications', 'Notifications.app')
            if 'VEE' in os.environ else
            'build/lib/uitools/notifications/WesternX-Notifications.app'
        ),

        'icon': 'art/notifications.icns',
        'plist_defaults': {
            'LSBackgroundOnly': True, # Don't show up in dock.
            # 'NSUserNotificationAlertStyle': 'alert',
        }
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
