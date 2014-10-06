.PHONY: clean dist

clean:
	./setup.py clean

dist:
	./setup.py sdist bdist_wheel

release:
	./setup.py sdist bdist_wheel upload --sign
