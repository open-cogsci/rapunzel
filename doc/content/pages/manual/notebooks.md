title: Notebooks
next_title: language-server
next_url: %url:language-server%


[TOC]


## What is a notebook?

Notebooks allow you to mix code, output (including figures), and text in a single document, and are often used for data analysis and other forms of numerical computing. Notebooks are generally edited in a browser, using the [JupyterLab or Jupyter Notebook](http://jupyterlab.io/) browser apps, or in [R Markdown](https://rmarkdown.rstudio.com/), which is part of R Studio.

The downside of this workflow is that these apps do not (yet) support all of the features of a modern code editor. In addition, many people prefer to work with plain-text code. Therefore, Rapunzel provides most of the functionality of a traditional notebook while still preserving the flexibility of a regular plain-text code editor.


## Defining code, markdown, and output cells



A code cell contains a chunk of code that should be executed together. A Markdown cell contains comments, and are mostly useful when [exporting your code as a notebook](%url:notebooks%). You can define code cells in three different ways. These ways are mutually exclusive, so within one document stick to one way of defining your cells.


### Only code cells

```python
# %%
print('This is a code cell')

# %%
print('This is another code cell')
```


### Mixing Markdown, code, and output cells

A multiline string (indicated by `"""` or `'''`) is treated as a Markdown cell. Everything in between Markdown cells is treated as a code cell. If you've enabled 'Capture output' (Menu → Run -> Capture output), then the output from running code cells is automatically insert in output cells, which are comment blocks preceded by a `# % output` line.


```python
print('This is a code cell')

# % output
# This is a code cell
# 
"""
This is a Markdown cell
"""

print('This is another code cell')

# % output
# This is another code cell
# 
```

## Capturing image output

There are two ways to capture image output. The first way, called 'Capture images as code annotations' in the preferences, puts the images as annotations next to the code that generated them:

%--
figure:
  source: image-capture.png
  id: FigImageCapture
  caption: Image annotations.
--%

The second way, called 'Capture images and text as code annotations and comments' in the preferences, puts the images as annotations next to the output that was captured while executing code cells:

%--
figure:
  source: output-capture.png
  id: FigOutputCapture
  caption: Image annotations combined with output capture.
--%


## Importing and exporting

You can import from, and export to Jupyter Notebook (`.ipynb`) format. Comment, code, and output cells are all preserved, including images, which are imported as image annotations.

You can export to `.docx`, `.pdf`, and `.html` format.
