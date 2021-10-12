# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(0, os.path.abspath("../../src/pypes_client"))
sys.path.insert(0, os.path.abspath("../../src/pypes_server"))
sys.path.insert(0, os.path.abspath("~/.local/lib/python3.8/site-packages"))


# -- Project information -----------------------------------------------------

project = "Pypes"
copyright = "2021, Silas Wagner"
author = "Silas Wagner"

# The full version, including alpha/beta/rc tags
release = "0.0.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
html_theme = "furo"

background = "#282a36"
background2 = "#232530"
selection = "#44475a"
foreground = "#f8f8f2"
comment = "#6272a4"

cyan = "#8be9fd"
green = "#50fa7b"
orange = "#ffb86c"
pink = "#ff79c6"
purple = "#bd93f9"
red = "#ff5555"
yellow = "#f1fa8c"

admonitions = {
    "caution": (yellow, "spark"),
    "warning": (orange, "warning"),
    "danger": (red, "spark"),
    "attention": (red, "warning"),
    "error": (red, "failure"),
    "hint": (green, "question"),
    "tip": (green, "info"),
    "important": (yellow, "flame"),
    "note": (cyan, "pencil"),
    "seealso": (cyan, "info"),
    "admonition-todo": (purple, "pencil"),
}


html_theme_options = {
    "dark_css_variables": {
        "color-problematic": red,
        "color-foreground-primary": foreground,
        "color-foreground-secondary": comment,
        "color-foreground-muted": comment + "88",
        "color-foreground-border": purple,
        "color-background-primary": background,
        "color-background-secondary": comment,
        "color-background-hover": purple + "ff",
        "color-background-hover--transparent": purple + "88",
        "color-background-border": selection,
        "color-brand-primary": green,
        "color-brand-content": orange,
        "color-link": purple,
        "color-link--hover": pink,
        "color-sidebar-background": background2,
        "color-sidebar-search-background": background,
        "color-sidebar-brand-text": purple,
        "color-sidebar-item-background--hover": "linear-gradient(90deg, {} {}%, {} {}%)".format(
            background2, -20, selection, 120
        ),
        "color-api-background": background2,
        "color-api-background-hover": comment + "88",
        "color-api-overall": foreground,
        "color-api-name": purple,
        "color-api-pre-name": yellow,
        "color-api-paren": comment,
        "color-api-keyword": green,
        "color-api-highlight-on-target": cyan,
    }
}

for kind, (col, icon) in admonitions.items():
    html_theme_options["dark_css_variables"]["color-admonition-title--" + kind] = col
    split = col[1:3], col[3:5], col[5:]
    cols = map(lambda c: int(c, 16), split)
    html_theme_options["dark_css_variables"][
        "color-admonition-title-background--" + kind
    ] = "rgba({},{},{}, 0.1)".format(*cols)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
