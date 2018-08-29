install:
	pip install -r requirements.txt

test:
	pip install -r requirements.txt
	python -m unittest discover . "*_test.py" -v

publish:
	python setup.py sdist bdist_wheel
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*


