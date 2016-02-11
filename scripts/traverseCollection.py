#!/usr/bin/env python2

# Copyright (c) 2016, Konstantin Burlachenko (burlachenkok@gmail.com).  All rights reserved.
# Part of gtest_report

import sys
sys.dont_write_bytecode = True

def extractCssClass(ctr):
    # Special process of css enable case
    cssClass=""
    if hasattr(ctr, "cssClass"):
        cssClass = ctr.cssClass
        del ctr.cssClass
        fields = {field: value for field, value in ctr.__dict__.items() if not callable(getattr(ctr, field))}
        if len(fields.values()) != 1: raise Exception("Problems cssClass field can be applied only for class with two fields")
        ctr = fields.values()[0];

    return (cssClass, ctr)

def genRows(ctr, cssClass, expandTypeIsRow):
    res = ""
#   res += '''<table border=1 class="container">'''
    for i in ctr:
        cssClass, i = extractCssClass(i)
        if (cssClass != ""):
            res += "<tr class=\"%s\">\n" % (cssClass,)
        else:
            res += "<tr>\n"
        
        res += generateElements(i, not expandTypeIsRow)
        res += "\n</tr>\n"
#   res += '''</table>'''
    return res

def genColumns(ctr, cssClass, expandTypeIsRow):
    res = ""
    for i in ctr:
        cssClass, i = extractCssClass(i)
        if (cssClass != ""):
            res += "<td class=\"%s\">" % (cssClass,)
        else:        
            res += "<td>"
        res += generateElements(i, not expandTypeIsRow)
        res += "</td>"
    return res

def genIterative(ctr, cssClass, expandTypeIsRow):
    if expandTypeIsRow == 1:
        return genRows(ctr, cssClass, expandTypeIsRow)
    else:
        return genColumns(ctr, cssClass, expandTypeIsRow)

def generateElements(ctr, expandTypeIsRow):
    xRes = ""
    cssClass = ""
    cssClass, ctr = extractCssClass(ctr)

    if (type(ctr) == list or type(ctr) == tuple):
        xRes = genIterative(ctr, "", expandTypeIsRow)
    elif (type(ctr) == dict):
        xRes = genIterative( map(None, ctr.keys(), ctr.values()), cssClass, expandTypeIsRow)
    elif hasattr(ctr, "__dict__"):
         fields = {field: value for field, value in ctr.__dict__.items() if not callable(getattr(ctr, field))}
         xRes = genIterative(map(None, fields.keys(), fields.values()), cssClass, expandTypeIsRow)
    else:
        if not expandTypeIsRow:
            xRes = "<td>" + str(ctr) + "</td>"
        else:
            xRes = str(ctr)

    return xRes

def generateHtmlDocument(ctr):
   htmlDocumentText =  '''<!DOCTYPE html>
<html>
<head> <title>Html report from gtest</title> </head>
<body>
{ctr}
</body></html>'''
   return htmlDocumentText.format(ctr=generateElements(ctr, True))

if __name__ == '__main__':
    class A: pass;
    a=A()   
    a.values = [1,2,3,4, None];
    a.cssClass = "wow"
    print generateHtmlDocument(a)
