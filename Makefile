.PHONY: all md pdf check clean

all: md pdf check

md:
	python3 scripts/publish.py md

pdf:
	python3 scripts/publish.py pdf

check:
	python3 -m py_compile scripts/publish.py scripts/render_atlas_lite_guide.py scripts/render_atlas_lite_intro.py
	python3 scripts/publish.py verify
	git diff --check

clean:
	rm -rf _build
