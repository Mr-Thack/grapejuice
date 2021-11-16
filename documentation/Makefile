export PYTHONPATH = ${PWD}

venv:
	virtualenv venv
	bash -c 'source ./venv/bin/activate && pip install -r ./tools/requirements.txt'

dist: venv
	bash -c "source ./venv/bin/activate && BLOG_ENV=dist BLOG_PATH_PREFIX=/grapejuice python3 ./tools/build.py"

serve: venv
	( \
       source ./venv/bin/activate; \
       python3 ./tools/serve.py \
    )

.PHONY: serve dist
