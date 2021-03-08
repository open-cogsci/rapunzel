title: Support for language servers
next_title: Installing packages
next_url: %url:environment%

Support for language servers is experimental
{: .page-notification}


[TOC]


## What is a language server?

A [language server](https://langserver.org/) is a tool that allows a code editor such as Rapunzel to implement features such as autocompletion, calltips, symbol browsing, etc. Different language servers provide these features for different languages. The code editor and the server communicate with each other through the so-called Language Server Protocol (LSP).


## Enabling language-server support

To enable support for language servers in Rapunzel, you need to install:

- The LanguageServer extension
- A language server for each language that you want to use


### LanguageServer extension

The LanguageServer extension provides general support for language servers in Rapunzel.

Anaconda:

```bash
conda config --add channels cogsci --add channels conda-forge
conda install opensesame-extension-language_server
conda install nodejs  # optional: provides npm, see below
```

Ubuntu:

```bash
sudo add-apt-repository ppa:smathot/cogscinl
sudo apt update
sudo apt install python3-opensesame-extension-language-server
```


### CSS

CSS support is provided through the [VSCode CSS Language Server](https://github.com/vscode-langservers/vscode-css-languageserver-bin). This needs to be installed through `npm`.

```bash
npm install -g vscode-css-languageserver-bin
```


### JavaScript/ TypeScript

JavaScript/ TypeScript support is provided through the [TypeScript Language Server](https://github.com/theia-ide/typescript-language-server). This needs to be installed through `npm`.

```bash
npm install -g typescript-language-server typescript
```


### JSON

JSON support is provided through the [VSCODE JSON Language Server](https://www.npmjs.com/package/vscode-json-languageserver). This needs to be installed through `npm`.

```bash
npm install -g vscode-json-languageserver
```


### Python

Python support is provided through the [Python Language Server](https://github.com/palantir/python-language-server).

Anaconda:

```bash
conda config --add channels conda-forge
conda install python-language-server
```

PyPi:

```bash
pip install python-language-server
```

Enabling Python support in the Language replaces the Python support that is built into Rapunzel.


### R

R support is provided through the [R Language Server](https://github.com/REditorSupport/languageserver). This needs to be installed in R from CRAN.

```R
install.packages("languageserver")
```


### YAML

YAML support is provided through the [YAML Language Server](https://github.com/redhat-developer/yaml-language-server). This needs to be installed through `npm`.

```bash
npm install -g yaml-language-server
```
