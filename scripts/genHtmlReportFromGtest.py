#!/usr/bin/env python2

# Copyright (c) 2016, Konstantin Burlachenko (burlachenkok@gmail.com).  All rights reserved.
# Part of gtest_report

import sys, os, re, shutil, os.path, glob
sys.dont_write_bytecode = True
from xml.dom.minidom import *
from traverseCollection import *

# Substitute html-texts
okIconText = '''<img src="gtest_report_ok.png" alt="ok icon" style="width:16px;height:16px;">'''
notOkIconText = '''<img src="gtest_report_notok.png" alt="notok icon" style="width:16px;height:16px;">'''
disableWarningText = '''<img src="gtest_report_disable.png" alt="notok icon" style="width:16px;height:16px;">'''

# Html document template
htmlDocumentText =  '''<!DOCTYPE html>
<html>
<head>
<title>Html report from GTest</title>
<link rel="stylesheet" type="text/css" href="gtest_report.css">
<script src="extraScript.js"></script>

</head>
<body>

<table class="aggregate_report">
{report}
</table>

<br/>

<table class="utests">
{tableHeader}
{rows}
</table>

</body></html>
'''
reportHeader = "<tr><th>Report name</th><th>Total unit tests </th><th>Failed unit tests</th> <th>Execution Time(sec)</th><th>Timestamp</th></tr>\n"

class Empty: pass

def process(outFname, files):
    tableHeader = '''<th>Test name</th>'''

    print "Generate HTML report based on this reports:", files
    print "Output HTML report filename:", outFname

    if (len(files) == 0):
        print "Please provide at least one report xml files..."
        return -2

    ctr = []
    report = ""

    # collect info from reports 
    for f in xrange(0, len(files)):
        ctr.append({})
        xmlFile = parse(files[f])
        fileBaseName = os.path.basename(files[f])

        for node in xmlFile.getElementsByTagName("testcase"):
            extra_content = ""
            for k,v in (node.attributes.items()):
                if k == "name" or k == "status" or k == "time" or k == "classname":
                    continue
                appendMsg = str(k) + ":" + str(v) + "\n"
                extra_content += appendMsg

            #name, time, status
            test = ["", 0.0, None]
            test[0] = str(node.attributes["classname"].value) + "." + str(node.attributes["name"].value)
            test[1] = float(node.attributes["time"].value)
            test[2] = Empty()
            test[2].value = str(node.attributes["status"].value)

            testReportPairId = test[0] + "_file_" + str(f)
            testReportPairId = testReportPairId.replace(".", "_")
            detailsId = testReportPairId + "details"

            if test[2].value == "notrun":
                test[2].value = disableWarningText
                test[2].cssClass = "notrun"
            elif len(node.getElementsByTagName("failure")) == 0:
                test[2].value = okIconText
                test[2].cssClass = "run"
            else:
                test[2].value = notOkIconText
                test[2].cssClass = "failed"

            if (extra_content):     
                extra_content = "<pre>" + extra_content + "</pre>"
                test[2].value += '''<input type="image" src="more_button.png" style="float: right;"  height="30" onclick="ShowDiv('{htmlId}')"></input>'''.format(htmlId = detailsId);
                test[2].value += '''<div id="{htmlId}" style="display:none;">{extra_content}</div>'''.format(htmlId = detailsId, extra_content = extra_content)

            #append 'row'
            ctr[f][test[0]] = test

        totalTime = xmlFile.getElementsByTagName("testsuites")[0].attributes["time"].value
        failures = xmlFile.getElementsByTagName("testsuites")[0].attributes["failures"].value

        timeStamp = ""
        if xmlFile.getElementsByTagName("testsuites")[0].attributes.has_key("timestamp"):
            timeStamp = xmlFile.getElementsByTagName("testsuites")[0].attributes["timestamp"].value

        report += generateElements([(files[f], len(ctr[f]), failures, totalTime, timeStamp)], True)
        tableHeader += '''<th>Execution in sec<br/>%s</th>''' % (fileBaseName)
        tableHeader += '''<th>Status and other info<br/>%s</th>''' % (fileBaseName)
    
    tableHeader = "<tr>" + tableHeader + "</tr>"

    #Create Final ctr
    finalCtr = {}
    for i in xrange(0, len(ctr)):
        for k in ctr[i].keys():
           finalCtr[k] = ["---"] * (len(ctr) * 2 + 1)

    for i in xrange(0, len(ctr)):
        for k in ctr[i].keys():
           finalCtr[k][0] = ctr[i][k][0]       #name
           finalCtr[k][1+(2*i)] = ctr[i][k][1] #time
           finalCtr[k][2+(2*i)] = ctr[i][k][2] #status

    for k in finalCtr.keys():
        maxTimeReport = 0
        minTimeReport = 0
        for i in xrange(0, len(ctr)):
            if (finalCtr[k][1 + 2*i] > finalCtr[k][1 + 2*maxTimeReport]): maxTimeReport = i
            if (finalCtr[k][1 + 2*i] < finalCtr[k][1 + 2*maxTimeReport]): minTimeReport = i       
        if (finalCtr[k][1 + 2*minTimeReport] != finalCtr[k][1 + 2*maxTimeReport]):
            minv = finalCtr[k][1 + 2*minTimeReport]
            maxv = finalCtr[k][1 + 2*maxTimeReport]

            finalCtr[k][1 + 2*minTimeReport] = Empty() 
            try:
                finalCtr[k][1 + 2*minTimeReport].value = str(minv) + "(" + str(minv-maxv) + ")"
            except:
                finalCtr[k][1 + 2*minTimeReport].value = str(minv)
            
            finalCtr[k][1 + 2*minTimeReport].cssClass = "down"

            finalCtr[k][1 + 2*maxTimeReport] = Empty() 
            finalCtr[k][1 + 2*maxTimeReport].value = maxv
            finalCtr[k][1 + 2*maxTimeReport].cssClass = "up"

    htmlDocument = htmlDocumentText.format(rows = generateElements(finalCtr.values(), True), tableHeader = tableHeader, report = reportHeader + report)

    with open(outFname, "wb") as writer:    
        writer.write(htmlDocument)

if __name__ == '__main__':
    if (len(sys.argv) == 1):
        print( "Generate html report from some google test xml reports v1.0.\n")
	sys.exit(2)

    destDir = os.path.dirname(sys.argv[1])

    if not os.path.isdir(destDir): os.makedirs(destDir)

    if (sys.argv[2].find('*') != -1):
        process(sys.argv[1], glob.glob(sys.argv[2]))
    else:
        process(sys.argv[1], sys.argv[2:])

    for f in glob.glob("./html_resources/*.*"):
        shutil.copy(f, os.path.join(destDir, os.path.basename(f)))
