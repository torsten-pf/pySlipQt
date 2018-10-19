build_install: clean
	clear; python setup.py build; python setup.py install

clean:
	rm -Rf build dist pySlipQt.egg-info/
