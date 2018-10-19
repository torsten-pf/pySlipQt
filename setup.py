from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pySlipQt',
      version='0.1.0',
      description='A slipmap widget for PyQt5',
      long_description=readme(),
      url='http://github.com/rzzzwilson/pySlipQt',
      author='Ross Wilson',
      author_email='rzzzwilson@gmail.com',
      license='MIT',
      packages=['pySlipQt', 'pySlipQt_tilesets'],
      install_requires=['pyqt5', 'python'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3 :: Only'],
      keywords='python pyqt5 slipmap map',
      download_url='https://github.com/rzzzwilson/pySlipQt/releases/tag/0.1.0',
      include_package_data=True,
      zip_safe=False)
