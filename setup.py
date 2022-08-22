from setuptools import setup

setup(
    name='twofi',
    version='0.1.0',    
    description='Rofi menu for twitch.tv',
    url='https://github.com/Pecarvajal246/twofi',
    author='Pedro Carvajal',
    author_email='pacarvajal246@gmail.com',
    packages=['twofi'],
    install_requires=['twitchAPI', 'pyxdg'],
    entry_points = {
            'console_scripts': ['twofi=twofi.twofi:main'],
        },
    classifiers=[
        'Operating System :: POSIX :: Linux',        
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.10',
    ],
)
