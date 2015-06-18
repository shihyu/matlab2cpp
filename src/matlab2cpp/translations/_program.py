import re

def add_indenting(text):

    lines = text.split("\n")

    indent = 0
    for i in xrange(len(lines)):
        line = lines[i]

        # Fix indentation and linesplit
        if line in ("}", "} ;") or line[:4] == "} //":
            indent -= 1
            line = "  "*indent + line

        elif line == "{":
            line = "  "*indent + line
            indent += 1
        else:
            line = "  "*indent + line
        lines[i] = line

    text = "\n".join(lines)

    return text


def number_fix(text):

    # Cosmetic fix
    for p0,p1,p2 in set(re.findall(r"(([ ,(])(-?\d+)-1)", text)):
        val = int(p2)-1
        val = p1+str(val)
        text = val.join(text.split(p0))

    for p0,p1,p2 in \
            set(re.findall(r"(([+\- ])(\d+)-1)", text)):
        if p1=="-":     val = int(p2)+1
        else:           val = int(p2)-1
        if val:         val = p1+str(val)
        else:           val = ""
        text = val.join(text.split(p0))

    text = re.sub(r"\+-", r"-", text)
    return text

def strip(text):

    start = 0
    while text[start] in "\n ":
        start += 1
    end = 0
    while text[end-1] in "\n ":
        end -= 1
    if end:
        text = text[start:end]
    else:
        text = text[start:]

    return text


def Program(tree):

    text = "\n\n".join(map(str, tree[:]))
    text = add_indenting(text)
    text = number_fix(text)
    text = re.sub(r"\n *(\n *)+", r"\n\n", text)
    text = strip(text)

    return text


Includes = "", "\n", ""
Include = "%(value)s"

def Library(node):

    if not node:
        return ""

    text = "\n\n".join(map(str, node[:]))

    """#ifndef MCONVERT_H
#define MCONVERT_H
#include <armadillo>

namespace m2cpp
{
""" + text + """
}

#endif
"""
    text = add_indenting(text)
    return text

Snippet = "%(value)s"
