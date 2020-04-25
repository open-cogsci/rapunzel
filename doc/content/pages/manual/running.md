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

A code cell contains a chunk of code that should be executed together. You can define code cells in two ways. The short way:

```python
# %%
print('This is a code cell')

# %%
print('This is another code cell')
```

And the long way:

```python
# <codecell>
print('This is a code cell')
# </codecell>

# <codecell>
print('This is another code cell')
# </codecell>
```

You can also define Markdown cells. This is mostly useful if you want to export your file as a Jupyter Notebook.

```python
# <markdowncell>
"""
This is a Markdown cell
"""
# </markdowncell>
```
