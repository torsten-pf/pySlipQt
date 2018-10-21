build_install: clean
	clear; python setup.py build; python setup.py install

release: clean
	python setup.py sdist bdist_wheel

clean:
	rm -Rf build dist pySlipQt.egg-info/
