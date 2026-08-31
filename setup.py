from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PySide6', 'database', 'models', 'services', 'ui'],
    'includes': ['sqlite3', 'json', 'datetime', 'dataclasses'],
}

setup(
    name='StudyTracker',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
