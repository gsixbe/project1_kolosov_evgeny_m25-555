install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	for %%f in (dist\*.whl) do python -m pip install "%%f"
lint:
	poetry run ruff check .

