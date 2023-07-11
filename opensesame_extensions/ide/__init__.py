"""Rapunzel is a set of extensions that turns OpenSesame into a modern code
editor.
"""
__version__ = '1.0.0'
# The name of the package to check for updates on conda and pip
packages = ['rapunzel']


def rapunzel():
    """This is the entry point for rapunzel"""
    import sys
    sys.argv.append(u'--mode=ide')
    from libqtopensesame import __main__
    __main__.opensesame()


# checking if __name__ is __main__ is required to let multiprocessing correctly
# work on Windows (or any other platform that is not able to use os.fork)
if __name__ == "__main__":
    rapunzel()
