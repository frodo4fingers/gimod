# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = GIMod
SOURCEDIR     = ./doc
BUILDDIR      = ./doc/_build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

api:
	sphinx-apidoc -fMT --output-dir=doc/gui ./gimod
	sphinx-apidoc -fMT --output-dir=doc/mpl ./gimod
	sphinx-apidoc -fMT --output-dir=doc/core ./gimod

doc: FORCE
	make clean
	make api
	make html

show:
	xdg-open "$(SOURCEDIR)"/_build/html/index.html

.PHONY: help Makefile
.PHONY: FORCE
.FORCE:

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
