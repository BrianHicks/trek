.PHONY: clean dist

clean:
	./setup.py clean

develop:
	pip install -r requirements.txt
	./setup.py develop

dist:
	./setup.py sdist bdist_wheel

release:
	./setup.py sdist bdist_wheel upload --sign
