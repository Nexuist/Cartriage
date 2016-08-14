### Introduction

Cartriage is a portmanteau of "cartridge" and "triage." It was originally developed for my school's IT department to monitor cartridge levels and other properties of every printer in the building.

#### [View a demo  report!](http://htmlpreview.github.io/?https://github.com/Nexuist/Cartriage/blob/master/example.html)

### Operation

Cartriage takes a text file (containing 1 IP address per line) and queries every host in it using SNMP (Simple Networking Management Protocol). In particular, Cartriage collects the following properties:

* Host Online - Whether the printer could be reached or not.

* Description - Reported by the printer.
	* ex. `RICOH MP C4503 1.24 / RICOH Network Printer C model / RICOH Network Scanner C model / RICOH Network Facsimile C model`

* Name - This can usually be set by the owner in the printer's web interface.
	* ex. `MP C4503`

* Serial Number

* Uptime - Amount of time since the printer was last restarted.
	* ex. `8 week(s) 4 day(s)`

* Life Count - Number of pages the printer has printed since it was activated.
	* ex. `17463`

* Power Cycle Count - Number of pages the printer has printed since it was last turned on.
	* ex. `17460`

* Supplies - Includes toner, staples, photo drums, fusers, etc.
	* ex. `Black Toner - 60.0% - 60 / 100 sheets - Type: consumed`
	* A printer can (and usually does) contain multiple supplies.
	* A supply can have a type of "filled" (ex. waste toner) or "consumed" (ex. fuser).
	* The measurement unit used to describe the supply is set by the printer and can range from "hours" to "sheets" to "lines." See [SupplyUnit in printerAndPrinterAccessories.py](https://github.com/Nexuist/Cartriage/blob/master/src/printerAndPrinterAccessories.py#L22-L38) for more.

The results are then dumped into an HTML file and prettified for human consumption. An link to an example page is available in the introduction.

> **NOTE:** Your results may vary. Most of these values are reported by the printer. Therefore, it's entirely possible that some of them will make no sense. It's all up to the manufacturer.

### Dependencies

* pySNMP - Used to communicate with the printers using SNMP.
	* Install using `pip install pysnmp`

* Python 2.7+
	* Comes preinstalled on most Linux and OS X versions
	* https://www.python.org/downloads/

### Arguments

> python [-h] [-v] printers output

* `printers` - Text file containing printer IP addresses, one for each line.
	* ex. "printers.txt"

* `output` - Filename for resulting HTML page.
	* ex. "report.html"

* `-v` - Optional, enables verbose reporting through STDOUT.

* `-h` - Display help message.

### License

```
MIT License

Copyright (c) 2016 Andi Andreas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
