export PYTHONPATH = ${PWD}

venv:
	virtualenv venv
	bash -c 'source ./venv/bin/activate && pip install -r ./tools/requirements.txt'

dist: venv
	( \
       source ./venv/bin/activate; \
       BLOG_ENV=dist python ./tools/build.py \
    )

serve: venv
	( \
       source ./venv/bin/activate; \
       python ./tools/serve.py \
    )

.PHONY: serve dist
