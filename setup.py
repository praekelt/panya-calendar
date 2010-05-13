from setuptools import setup, find_packages

setup(
    name='django-calendar',
    version='dev',
    description='Django calendar app.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/django-calendar',
    packages = find_packages(),
    include_package_data=True,
)

