.PHONY: all design design-check md pdf check clean

all: design md pdf check

design:
	python3 scripts/design_system.py generate

design-check:
	python3 scripts/design_system.py verify

md:
	python3 scripts/publish.py md

pdf: design-check
	python3 scripts/publish.py pdf

check: design-check
	python3 -m py_compile scripts/design_system.py scripts/publish.py scripts/render_atlas_lite_guide.py scripts/render_atlas_lite_intro.py
	python3 scripts/publish.py verify
	git diff --check

clean:
	rm -rf _build
