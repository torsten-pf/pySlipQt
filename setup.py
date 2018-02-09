from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyslipqt',
      version='1.0.0',
      description='A slipmap widget for PyQt5',
      long_description=readme(),
      url='http://github.com/rzzzwilson/pySlipQt',
      author='Ross Wilson',
      author_email='rzzzwilson@gmail.com',
      license='MIT',
      packages=['pyslipqt'],
      install_requires=['python', 'pyqt5'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3 :: Only'],
      keywords='python pyqt5 slipmap map',
      download_url='https://github.com/rzzzwilson/pySlipQt/releases/tag/1.0.0',
      include_package_data=True,
      zip_safe=False)
