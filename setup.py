from setuptools import setup, find_packages

setup(
    name="PyKit",
    packages=find_packages(),
    install_requires=[],
    entry_points={'console_scripts': [
        'pykit-tests = pykit.tests.run_on_cocoa:main']},
)
