PYTHON ?= python

all: guide.pdf

html: guide.html

clean:
	rm *.pdf *.html

%.pdf: %.html
	weasyprint -O all -dv $< $@

%.html: papers
	$(PYTHON) make_paper.py > $@
