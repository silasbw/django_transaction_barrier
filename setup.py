try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


with open('README.rst') as file:
    long_description = file.read()

setup(
  author='Silas Boyd-Wickizer',
  author_email='silas@godaddy.com',
  classifiers=(
    'Development Status :: 5 - Production/Stable',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
  ),
  description='Transaction barriers for Django and Celery.',
  download_url='https://github.com/godaddy/django_transaction_barrier/tarball/0.3',
  include_package_data=True,
  install_requires=('Django>=1.4.0,<1.8.0','celery>=3.0.0,<4.0.0'),
  keywords=('django', 'transaction', 'celery', 'atomic'),
  license=open('LICENSE.txt').read(),
  long_description=long_description,
  name='django-transaction-barrier',
  packages=('django_transaction_barrier', 'django_transaction_barrier.migrations'),
  url='https://github.com/godaddy/django_transaction_barrier',
  version='0.3',
  zip_safe=True,
)
