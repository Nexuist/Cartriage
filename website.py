from printerAndPrinterAccessories import *
import time

class Website():
    def __init__(self, scanned, successfullyScanned, printers, elapsedTime):
        self.scanned = scanned
        self.successfullyScanned = successfullyScanned
        self.printers = printers
        self.elapsedTime = elapsedTime
        self.date = time.strftime("%m/%d/%Y %H:%M:%S")
        self.headers = ["Host", "Name", "Uptime", "Life Count", "Power Cycle Count", "Supplies"]

    def generatePageHTML(self):
        head = "<head><title>Scan Results (%s)</title><link rel=stylesheet href=http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css><script src=https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js></script><script src=http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js></script><script>$(document).ready(function () {$('[data-toggle=tooltip]').tooltip();});</script><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'></head>" % self.date
        navbar = "<nav class='navbar navbar-default'><div class=container-fluid><div class=navbar-header><a class=navbar-brand href=#>%(name)s</a></div><div><ul class='nav navbar-nav navbar-right'><li><a href=#><span class='glyphicon glyphicon-print'></span> %(scanned)s</a></li><li><a href=#><span class='glyphicon glyphicon-ok-circle'></span> %(successfullyScanned)s</a></li><li><a href=#><span class='glyphicon glyphicon-time'></span> %(elapsedTime)s</a></li><li><a href=#><span class='glyphicon glyphicon-calendar'></span> %(date)s</a></li></ul></div></div></nav>" % {\
            "name": "Cartriage v5.0",
            "scanned": self.scanned,
            "successfullyScanned": self.successfullyScanned,
            "elapsedTime": self.elapsedTime,
            "date": self.date}
        table = "<table class='table table-striped table-fluid'><thead><tr>%(headers)s</tr></thead><tbody>%(tableContent)s</tbody></table>" % {\
            "headers": "".join(["<th>%s</th>" % header for header in self.headers]),
            "tableContent": "".join([printer.toHTMLRow() for printer in self.printers])
        }
        body = "<body>%s<div class = 'container-fluid'>%s</div></body>" % (navbar, table)
        page = "<!DOCTYPE html><html lang=en>%s%s</html>" % (head, body)
        return page

    def __str__(self):
        return self.generatePageHTML()
