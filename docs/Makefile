# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

echo:
	echo '(dolist (f (file-expand-wildcards "./$(SOURCEDIR)/org/*.org")) (message "exporting %s" f) (lm-with-file f (org-rst-export-to-rst)))'

org:
	(cd "$(SOURCEDIR)/org" && emacsclient --eval '(dolist (f (file-expand-wildcards "./*.org")) (message "%s exporting %s" (pwd) f) (lm-with-file f (org-rst-export-to-rst)))')

rst:
	sphinx-apidoc -f -o source ../src


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
