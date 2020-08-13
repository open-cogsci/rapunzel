title: Running code
next_title: Debugging
next_url: %url:debugging%


There are two main ways to run code:

`F5` runs a project or file
`F9` runs a selection, the current cell, or the current line.

Rapunzel uses an intuitive logic to run code as you would expect it to, as explained below. Code is executed in the currently active console, unless otherwise specified in a project file.


[TOC]


%--
video:
 source: youtube
 id: VidRapunzel
 videoid: UYKIIsyex1g
 width: 640
 height: 360
 caption: |
  Running code with Rapunzel
--%


## Running a project or file (`F5`)

- If a project file exists for the currently active file, then this project file controls how the project is executed (see below).
- Otherwise, the currently active file is executed.


## Running a selection, cell, or line (`F9`)

- If any code is selected, then this selection is executed.
- Otherwise, if the cursor is inside a code cell (explained below), then this code cell is executed.
- Otherwise, the currently active line of code is executed.


## Defining a project file

A project file is a file called `.rapunzel.yaml` in the root of your project folder. It is mostly useful if you're working on a large project, and you want to quickly compile or run it, regardless of which file is currently active. There is at least a `run` key, which specifies the code that should be executed. Optionally, there is a `kernel` key, in which case a new console is opened with this kernel; if no kernel is specified, the currently active console is used.

Example:

```yaml
kernel: python
run: |
    %cd ~/git/OpenSesame
    !python opensesame --mode=ide -d
```


## Defining code and Markdown cells

A code cell contains a chunk of code that should be executed together. A Markdown cell contains comments, and are mostly useful when [exporting your code to a Jupyter Notebook](%url:notebooks%). You can define code cells in three different ways. These ways are mutually exclusive, so within one document stick to one way of defining your cells.


### Only code cells

```python
# %%
print('This is a code cell')

# %%
print('This is another code cell')
```


### Mixing code cells and Markdown cells

*Version note: New in Rapunzel 0.4.9*

A multiline string (indicated by `"""` or `'''`) is treated as a Markdown cell. Everything in between Markdown cells is treated as a code cell.


```python
print('This is a code cell')

"""
This is a Markdown cell
"""

print('This is another code cell')
```


### Mixing code cells and Markdown cells (alternative)


A slightly more verbose way to define code and Markdown cells uses explicit tags, like so:

```python
# <codecell>
print('This is a code cell')
# </codecell>

# <markdowncell>
"""
This is a Markdown cell
"""
# </markdowncell>

# <codecell>
print('This is another code cell')
# </codecell>
```
