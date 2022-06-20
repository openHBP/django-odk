def rm_digit(mystr):
    """remove all digit from a string"""
    strnew = ''.join([i for i in mystr if not i.isdigit()])
    return strnew


def convert2camelcase(word):
    """
    convert a string with underscore (package naming convention) to CamelCase
    ex: hello_world => HelloWorld
    """
    return ''.join(x.capitalize() or '_' for x in word.split('_'))