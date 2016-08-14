import logging
import sys
import argparse
import easysnmp
import pprint
import time

# Constants
SOFTWARE_NAME = "Cartriage v4.0"
TABLE_HEADERS = ["Host", "Name", "Uptime", "Life Count", "Power Cycle Count", "Supplies"]
OID_TABLE = \
{
    ".1.3.6.1.2.1.1.5": "Name",
    ".1.3.6.1.2.1.1.1": "Description",
    ".1.3.6.1.2.1.1.3": "Uptime",
    #".1.3.6.1.2.1.1.6": "Location",
    #".1.3.6.1.2.1.43.5.1.1.16": "PrinterName",
    ".1.3.6.1.2.1.43.5.1.1.17": "SerialNumber",
    #".1.3.6.1.2.1.43.5.1.1.18": "CriticalEvents",
    #".1.3.6.1.2.1.43.5.1.1.19": "AllEvents",
    ".1.3.6.1.2.1.43.10.2.1.3": "MarkerUnit",
    ".1.3.6.1.2.1.43.10.2.1.4": "MarkerLifeCount",
    ".1.3.6.1.2.1.43.10.2.1.5": "MarkerPowerOnCount",
    #".1.3.6.1.2.1.43.10.2.1.15": "MarkerStatus",
    #".1.3.6.1.2.1.43.11.1.1.4": "SupplyClass",
    ".1.3.6.1.2.1.43.11.1.1.5": "SupplyType",
    ".1.3.6.1.2.1.43.11.1.1.6": "SupplyDescription",
    ".1.3.6.1.2.1.43.11.1.1.7": "SupplyUnit",
    ".1.3.6.1.2.1.43.11.1.1.8": "SupplyMaxCapacity",
    ".1.3.6.1.2.1.43.11.1.1.9": "SupplyCurrentLevel"
}

# Setup logging
logger = logging.getLogger("Cartriage")
logger.setLevel(logging.INFO)
screenLogger = logging.StreamHandler()
screenLogger.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",  "%H:%M:%S"))
logger.addHandler(screenLogger)

# Convert numeric supply values into strings
def intToSupplyUnit(intValue):
    supplyMap = {
        "3": "tenThousandthsOfInche(s)",
        "4": "micrometer(s)",
        "5": "character(s)",
        "6": "line(s)",
        "7": "impression(s)",
        "8": "sheet(s)",
        "9": "dotRow(s)",
        "11": "hour(s)",
        "12": "thousandthsOfOunce(s)",
        "13": "tenthOfGram(s)",
        "14": "hundredsOfFluidOunce(s)",
        "15": "tenthsOfMillimeter(s)",
        "16": "feet",
        "17": "meter(s)",
        "18": "item(s)",
        "19": "percent"
    }
    if intValue in supplyMap:
        return supplyMap[intValue]
    else:
        return "unknown(s)"

def intToSupplyType(intValue):
    typeMap = {
    "1": "other",
    "3": "consumed",
    "4": "filled"
    }
    if intValue in typeMap:
        return typeMap[intValue]
    else:
        return "unknown"

# HTML helper functions
def td(text):
    return "<td>%s</td>" % text

def td_tooltip(text, tooltip_text):
    return "<td>%s <span class = 'glyphicon glyphicon-info-sign' data-toggle = 'tooltip' data-container = 'body' title = '%s'></span></td>" % (text, tooltip_text)

def progress_bar(progress, color_int, text, tooltip_text):
    '''
        Generate HTML for a progress bar that will get injected into a table row.
        progress -> float (Progress bar value)
        color_int -> int (Number between 1-4 that signifies the color value for this progress bar)
        text -> string (Text that should be visible on progress bar)
        tooltip_text -> string (Text that becomes visible on hover over)

    '''
    color = ""
    if color_int == 4:
        color = "success" # Green
    elif color_int == 3:
        color = "complete" # Blue
    elif color_int == 2:
        color = "warning" # Yellow
    else:
        color = "danger" # Red
    color_class = "progress-bar-" + color
    return "<div class = 'progress' data-toggle = 'tooltip' data-container = 'body' title = '%s'><div class = 'progress-bar %s progress-bar-striped' role = 'progressbar' aria-valuenow = '%s' aria-valuemin = '0' aria-valuemax = '100' style = 'width: %s%%'> %s</div></div>" % (tooltip_text, color_class, progress, progress, text)

def export_row(host, values):
    '''
        Generate HTML for a table row that will get injected into the output file.
        host -> string (IP address)
        values -> dict {oid_english: oid_value}
            oid_english -> string (OID English meaning)
            oid_value -> list (values for OID)
    '''
    v = lambda key: values[key][0]
    color = "danger" if not values["SUCCESSFUL"] else ""
    row = td_tooltip(host, v("Description"))
    row += td_tooltip(v("Name"), "Serial Number: "  + v("SerialNumber"))
    if v("Uptime").decode("utf-8").isnumeric():
        seconds = float(v("Uptime"))
        weeks, seconds = divmod(seconds, 7*24*60*60)
        days, seconds = divmod(seconds, 24*60*60)
        row += td("%d week(s) %d day(s)" % (weeks, days))
    else:
        row += td(v("Uptime"))
    unit = intToSupplyUnit(v("MarkerUnit"))
    row += td(v("MarkerLifeCount") + " " + unit)
    row += td(v("MarkerPowerOnCount") + " " + unit)
    progress_bar_html = ""
    for index, description in enumerate(values["SupplyDescription"]):
        v = lambda key: values[key][index]
        if description != "N/A":
            supplyType = intToSupplyType(v("SupplyType"))
            supplyUnit = intToSupplyUnit(v("SupplyUnit"))
            currentLevel = float(v("SupplyCurrentLevel"))
            maxLevel = float(v("SupplyMaxCapacity"))
            percentLevel = 100 * currentLevel / maxLevel
            tooltip_text = "%s - %s%% - %s / %s %s - Type: %s" % (description, percentLevel, currentLevel, maxLevel, supplyUnit, supplyType)
            color_int = 0
            if percentLevel <= 25:
                color_int = 1
            elif percentLevel <= 50:
                color_int = 2
            elif percentLevel <= 75:
                color_int = 3
            else:
                color_int = 4
            # The higher the percent for filled containers, the higher the urgency is
            if supplyType == "filled":
                color_int = abs(color_int - 4)
            progress_bar_html += progress_bar(percentLevel, color_int, description, tooltip_text)
    row += td(progress_bar_html)
    return "<tr class = '%s'>%s</td>" % (color, row)



def export_html(file, num_printers, num_success, num_secs, host_values):
    '''
        Parse output into HTML and save it into a file.
        file -> writable file object
        num_printers -> int (Hosts scanned)
        num_success -> int (Queries that succeeded)
        num_secs -> string (Elapsed time of scan)
        host_values -> dict {host: values}
            -> values {oid_english: oid_value}
                oid_english -> string (OID English meaning)
                oid_value -> list (values for OID)
    '''
    # Declaration & head & start body
    file.write(
        "<!DOCTYPE html><html lang=en><head><title>Scan Results</title><link rel=stylesheet href=http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css><script src=https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js></script><script src=http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js></script><script>$(document).ready(function () {$('[data-toggle=tooltip]').tooltip();});</script><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'></head><body>")
    stats = {
        "name": SOFTWARE_NAME,
        "num_printers": num_printers,
        "num_success": num_success,
        "num_secs": num_secs
    }
    # Navbar
    file.write("<nav class='navbar navbar-default'><div class=container-fluid><div class=navbar-header><a class=navbar-brand href=#>%(name)s</a></div><div><ul class='nav navbar-nav navbar-right'><li><a href=#><span class='glyphicon glyphicon-print'></span> %(num_printers)s</a></li><li><a href=#><span class='glyphicon glyphicon-ok-circle'></span> %(num_success)s</a></li><li><a href=#><span class='glyphicon glyphicon-time'></span> %(num_secs)s</a></li></ul></div></div></nav>" % stats)
    # Table & table header
    file.write("<div class=container-fluid><table class='table table-striped table-fluid'><thead><tr>")
    for header in TABLE_HEADERS:
        file.write("<th>%s</th>" % header)
    # Close table header
    file.write("</tr></thead><tbody>")
    for host, values in host_values.iteritems():
        file.write(export_row(host, values))
    # End page
    file.write("</tbody></table></div></body></html>")


def queryOIDs(host):
    '''
        Walk all the OIDs in OID_TABLE for the given host.
        host -> string (IP address)
        returns {englishValue: value}
            englishValue -> string (English representation of OID)
            value -> list (available values for OID or "N/A" if not found)
    '''
    host_values = {}
    successful_query = True  # By default
    try:
        snmp_session = easysnmp.Session(
            hostname = host, community = "public", version = 1)
        logger.debug("Connected to host, beginning walk...")
        for oid, englishValue in OID_TABLE.iteritems():
            logger.debug("Current value: %s (%s)" % (englishValue, oid))
            try:
                host_values[englishValue]=map(
                    lambda x: x.value, snmp_session.walk(oid))
                if host_values[englishValue] == []:
                    host_values[englishValue] = ["N/A"]
            except easysnmp.EasySNMPError, e:
                logger.debug("Encountered %s while walking %s (%s): %s" %
                             (e.__class__.__name__, oid, englishValue, e))
                host_values[englishValue] = ["N/A"]
                successful_query = False
    except easysnmp.EasySNMPConnectionError, e:
        logger.debug("Encountered %s while connecting to %s: %s" %
                     (e.__class__.__name__, host, e))
        successful_query = False
        for oid, englishValue in OID_TABLE.iteritems():
            host_values[englishValue] = ["N/A"]
    host_values["SUCCESSFUL"] = successful_query
    return host_values

def run_scan(ip_file):
    '''
        Goes through every line in ip_file and launches a scan on it.
        ip_file -> file object containing list of IP addresses
        returns {host: {englishValue: value}}
            host -> string (IP address)
            Refer to queryOIDs for description of {englishValue: value}.
    '''
    scan_results = {}
    printers_scanned = 0
    printers_successfully_scanned = 0
    for ip in ip_file:
        ip = ip.strip()
        printers_scanned += 1
        logger.info("Querying %s..." % ip)
        host_values = queryOIDs(ip)
        if host_values["SUCCESSFUL"]:
            printers_successfully_scanned += 1
        scan_results[ip] = host_values
    logger.info("Finished scanning %s printer(s) with %s successful attempt(s)" % (
        printers_scanned, printers_successfully_scanned))
    return (printers_scanned, printers_successfully_scanned, scan_results)

def main():
    logger.info("Cartriage v4.0")
    parser = argparse.ArgumentParser(
        description="Retrieves information from printers.")
    parser.add_argument("l", type=open, metavar="printers",
                        help="Text file containing printer IP addresses, one for each line.")
    parser.add_argument("o", metavar="output",
                        help="Filename for resulting HTML page.")
    parser.add_argument("-v", action="store_true", help="Enable verbose mode.")
    try:
        args = parser.parse_args()
        if args.v:
            logger.info("Enabled verbose mode")
            logger.setLevel(logging.DEBUG)
        logger.debug(args)
        start_time = time.time()
        time.clock()
        printers_scanned, printers_successfully_scanned, scan_results = run_scan(args.l)
        elapsed_time = "%02d seconds" % (time.time() - start_time)
        export_html(open(args.o, "w"), printers_scanned, printers_successfully_scanned, elapsed_time, scan_results)
        logger.info("Done! Results available in file: %s" % args.o)
        sys.exit(0)
    except IOError, e:
        logger.error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
