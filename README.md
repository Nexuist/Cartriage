### Introduction

Cartriage is a portmanteau of "cartridge" and "triage." It was originally developed for my school's IT department to monitor cartridge levels and other properties of every printer in the building.

### Operation

Cartriage takes a text file (containing 1 IP address per line) and queries every host in it using SNMP (Simple Networking Management Protocol). In particular, Cartriage collects the following properties:

* Host Up

* Description - Reported by the printer.
	* ex. "RICOH MP C4503 1.24 / RICOH Network Printer C model / RICOH Network Scanner C model / RICOH Network Facsimile C model"

* Name - This can usually be set by the owner in the printer's web interface.
	* ex. "MP C4503"

* Serial Number

* Uptime
	* ex. "8 week(s) 4 day(s)"

* Life Count - Number of pages the printer has printed since it was activated
	* ex. "17463"

* Power Cycle Count - Number of pages the printer has printed since it was last turned on
	* ex. "17460"

* Supplies - Includes toner, staples, photo drums, fusers, etc.
	* ex. "Black Toner - 60.0% - 60 / 100 sheets - Type: consumed"
	* A supply can have a type of "filled" (ex. waste toner) or "consumed" (ex. fuser).
	* The measurement unit used to describe the supply is set by the printer and can range from "hours" to "sheets" to "lines." See `SupplyUnit` in `printerAndPrinterAccessories.py` for more.

The results are then dumped into an HTML file and prettified for human consumption. An example report is available [here](here).

> **NOTE:** Your results may vary. Most of these values are reported by the printer. Therefore, it's entirely possible that some of them will make no sense. It's all up to the manufacturer.

### Arguments

> python main.py input output [-v]

* `input` - Text file containing printer IP addresses, one for each line.
	* ex. "printers.txt"

* `output` - Filename for resulting HTML page.
	* ex. "report.html"

* `-v` - Optional, enables verbose reporting through STDOUT.

### License
