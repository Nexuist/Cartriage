import logging
import sys
import argparse
import pprint
import time
import socket
import random
from website import Website
from pysnmp.hlapi import *
from printerAndPrinterAccessories import *


logger = logging.getLogger("Cartriage")
logger.setLevel(logging.INFO)
screenLogger = logging.StreamHandler()
screenLogger.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",  "%H:%M:%S"))
logger.addHandler(screenLogger)

def query(ip):
    # ip: String -> IP address to query
    finalResults = {}
    values = \
    {
        ".1.3.6.1.2.1.1.5": "Name",
        ".1.3.6.1.2.1.1.1": "Description",
        ".1.3.6.1.2.1.1.3": "Uptime",
        ".1.3.6.1.2.1.43.5.1.1.17": "SerialNumber",
        ".1.3.6.1.2.1.43.10.2.1.3": "MarkerUnit",
        ".1.3.6.1.2.1.43.10.2.1.4": "MarkerLifeCount",
        ".1.3.6.1.2.1.43.10.2.1.5": "MarkerPowerOnCount",
        ".1.3.6.1.2.1.43.11.1.1.5": "SupplyType",
        ".1.3.6.1.2.1.43.11.1.1.6": "SupplyDescription",
        ".1.3.6.1.2.1.43.11.1.1.7": "SupplyUnit",
        ".1.3.6.1.2.1.43.11.1.1.8": "SupplyMaxCapacity",
        ".1.3.6.1.2.1.43.11.1.1.9": "SupplyCurrentLevel"
    }
    success = True # By default
    target = UdpTransportTarget((ip, 161), retries = 0, timeout = 5) # Don't retry if fail
    community = CommunityData("public", mpModel = 0) # mpModel -> SNMP version
    for oid in values.keys():
        children = []
        oidObject = ObjectType(ObjectIdentity(oid))
        iterator = nextCmd(SnmpEngine(), community, target, ContextData(), oidObject)
        for errorIndicator, errorStatus, errorIndex, bindings in iterator:
            if errorIndicator or errorStatus or errorIndex:
                children.append(None)
                success = False
            else:
                result = bindings[0] # We will only ever want the first entry
                resultOID = str(result[0].getOid())
                comparisonOID = resultOID[:len(oid)] # Trim result OID to the same length as the original OID for comparison
                # Remove periods from stringd and compare
                if oid.replace(".", "") != comparisonOID.replace(".", ""):
                    # No longer listing children of the OID
                    # Quit the loop
                    break
                resultValue = str(result[1])
                if resultValue == "":
                    resultValue = None
                children.append(resultValue)
        finalResults[oid] = children if len(children) > 0 else [None]
    return Printer(ip, success, finalResults)

def runScan(ipFile):
    printers = []
    numScanned = 0
    numSuccessfullyScanned = 0
    for ip in ipFile:
        ip = ip.strip()
        valid = True
        try:
            socket.inet_aton(ip)
        except socket.error:
            valid = False
        if valid:
            numScanned += 1
            printer = query(ip)
            numSuccessfullyScanned += 1 if printer.online else 0
            printers.append(printer)
    return (numScanned, numSuccessfullyScanned, printers)

def main():
        logger.info("Cartriage v5.0")
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
            startTime = time.time()
            time.clock()
            scanned, successfullyScanned, printers = runScan(args.l)
            elapsedTime = "%d seconds" % (time.time() - startTime)
            site = Website(scanned, successfullyScanned, printers, elapsedTime)
            with open(args.o, "w") as output:
                output.write(str(site))
            logger.info("Done! Results available in file: %s" % args.o)
            sys.exit(0)
        except IOError, e:
            logger.error(str(e))
            sys.exit(1)


if __name__ == "__main__":
    main()
