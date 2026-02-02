from setuptools import setup
APP = ['mac_ai_cleaner.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'AI清洗工具2.0',
        'CFBundleDisplayName': 'AI清洗工具2.0',
        'CFBundleVersion': '2.0.0',
        'CFBundleIdentifier': 'com.yourcompany.ai-cleaner',
        'NSHumanReadableCopyright': '© 2024 Your Company',
    },
    'packages': ['pandas', 'requests', 'openpyxl'],
    'includes': ['tkinter', 'threading', 'configparser', 're', 'concurrent.futures'],
}
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)