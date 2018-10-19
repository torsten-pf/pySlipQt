build_install:
	rm -Rf build
	clear; python setup.py build; python setup.py install
