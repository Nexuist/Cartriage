### Introduction

Cartriage is a portmanteau of "cartridge" and "triage." It was originally developed for my school's IT department to monitor cartridge levels and other properties of every printer in the building.

### Operation

Cartriage takes a text file (containing 1 IP address per line) and queries every host in it using SNMP (Simple Networking Management Protocol). In particular, Cartriage collects the following properties:

* Host Up

* Reported Description
	* ex. "RICOH MP C4503 1.24 / RICOH Network Printer C model / RICOH Network Scanner C model / RICOH Network Facsimile C model"

* Reported Name
	* ex. "MP C4503"

* Uptime
	* ex. "8 week(s) 4 day(s)"

* Life Count - Number of pages the printer has printed since it was activated
	* ex. "17463"

* Power Cycle Count - Number of pages the printer has printed since it was last turned on
	* ex. "17460"

* Supplies - Includes toner, staples, photo drums, fusers, etc.
	* ex. "Black Toner - 60.0% - 60 / 100 sheets - Type: consumed"
	* A supply can have a type of "filled" (ex. waste toner) or "consumed" (ex. fuser).
	* The measurement unit used to describe the supply is set by the printer and can range range from "hours" to "sheets" to "lines."


### Arguments

> python main.py input output [-v]

* `input` - Text file containing printer IP addresses, one for each line.
	* ex. "printers.txt"

* `output` - Filename for resulting HTML page.
	* ex. "report.html"

* `-v` - Optional, enables verbose reporting through STDOUT.
