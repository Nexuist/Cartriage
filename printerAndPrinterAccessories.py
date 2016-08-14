from enum import Enum

# Helper method to prevent errors
def xstr(s):
    if s is None:
        return "N/A"
    return str(s)

class BaseEnum(Enum):
    @classmethod
    def contains(self, intValue):
        values = map(lambda member: member.value, self)
        if intValue in values:
            return True
        else:
            return False

class SupplyType(BaseEnum):
    consumed = 3
    filled = 4

class SupplyUnit(BaseEnum):
    tenThousandthsOfInches = 3
    micrometers = 4
    characters = 5
    lines = 6
    impressions = 7
    sheets = 8
    dotRows = 9
    hours = 11
    thousandthsOfOunces = 12
    tenthsOfGrams = 13
    hundredsOfFluidOunces = 14
    tenthsOfMillimeters = 15
    feet = 16
    meters = 17
    items = 18
    percent = 19

class ProgressBarColor(Enum):
    danger = range(25) # Red
    warning = range(25, 50) # Yellow
    complete = range(50, 75) # Blue
    success = range(75, 101) # Green

    @classmethod
    def colorForPercentage(self, percent):
        for color in self:
            containedRange = color.value # Referring to the range
            if int(percent) in containedRange:
                return color.name

class PrinterSupply():
    def __init__(self, type, description, unit, maxLevel, currentLevel):
        self.type, self.unit = SupplyType.consumed, SupplyUnit.sheets
        if SupplyType.contains(type):
            self.type = SupplyType(type)
        if SupplyUnit.contains(unit):
            self.unit = SupplyUnit(unit)
        self.description = description
        self.currentLevel = currentLevel
        self.maxLevel = maxLevel
        self.percentLevel = 100 * float(currentLevel) / float(maxLevel)

    def toHTMLProgressBar(self):
        percentLevel = 100 - self.percentLevel if self.type == SupplyType.filled else self.percentLevel # Inverse percentage if supply is filled
        color = ProgressBarColor.colorForPercentage(self.percentLevel)
        colorClass = "progress-bar-" + color
        tooltip = str(self)
        return "<div class = 'progress' style = 'background: #b3adad;' data-toggle = 'tooltip' data-container = 'body' title = '%s'><div class = 'progress-bar %s progress-bar-striped' role = 'progressbar' aria-valuenow = '%s' aria-valuemin = '0' aria-valuemax = '100' style = 'width: %s%%'> %s</div></div>" % (tooltip, colorClass, percentLevel, percentLevel, self.description)

    def __str__(self):
        return "%s - %s%% - %s / %s %s - Type: %s" % (self.description, self.percentLevel, self.currentLevel, self.maxLevel, self.unit.name, self.type.name)

class Printer():
    def __init__(self, ip, online, oids):
        # ip: String -> IP address
        # online: Bool -> Self evident
        # oids: dict<oid: String, value: String> -> OIDs and results
        self.ip = ip
        self.online = online
        self.name = oids[".1.3.6.1.2.1.1.5"][0]
        self.description = oids[".1.3.6.1.2.1.1.1"][0]
        self.serialNumber = oids[".1.3.6.1.2.1.43.5.1.1.17"][0]
        self.uptime = self.uptimeStringFromRawValue(oids[".1.3.6.1.2.1.1.3"][0])
        # Previous method creates self.rawUptimeInSeconds
        self.unit = None
        unit = oids[".1.3.6.1.2.1.43.10.2.1.3"][0]
        if SupplyUnit.contains(unit):
            self.unit = SupplyUnit(unit)
        self.lifeCount = oids[".1.3.6.1.2.1.43.10.2.1.4"][0]
        self.powerOnCount = oids[".1.3.6.1.2.1.43.10.2.1.5"][0]
        self.supplies = []
        # Iterate through prtMarkerSupplies table
        s = lambda oid, index: oids[".1.3.6.1.2.1.43.11.1.1." + oid][index]
        print oids[".1.3.6.1.2.1.43.11.1.1.5"]
        for index, supplyType in enumerate(oids[".1.3.6.1.2.1.43.11.1.1.5"]):
            if supplyType != None:
                description = s("6", index)
                unit = s("7", index)
                maxLevel = s("8", index)
                currentLevel = s("9", index)
                self.supplies.append(PrinterSupply(supplyType, description, unit, maxLevel, currentLevel))

    def uptimeStringFromRawValue(self, rawValue):
        # rawValue: int -> hundredths of seconds since last init
        if not rawValue:
            return None
        if not rawValue.decode("utf-8").isnumeric():
            return None
        rawValue = int(rawValue)
        seconds = rawValue / 100
        self.rawUptimeInSeconds = seconds
        weeks, seconds = divmod(seconds, 7*24*60*60)
        days, seconds = divmod(seconds, 24*60*60)
        return "%d week(s) %d day(s) " % (weeks, days)

    def online(self):
        return self.status == 0

    def toHTMLRow(self):
        row = ""
        rowColor = "danger" if not self.online else ""
        td = lambda content: "<td>%s</td>" % xstr(content)
        tt = lambda content, tooltip: td("%s <span class = 'glyphicon glyphicon-info-sign' data-toggle = 'tooltip' data-container = 'body' title = '%s'></span>") % (xstr(content), xstr(tooltip))
        row += tt(self.ip, "Description: " + xstr(self.description))
        row += tt(self.name, "Serial Number: " + xstr(self.serialNumber))
        row += td(self.uptime)
        row += td(self.lifeCount)
        row += td(self.powerOnCount)
        supplyBars = ""
        for supply in self.supplies:
            supplyBars += supply.toHTMLProgressBar()
        row += td(supplyBars)
        return "<tr class = '%s'>%s</tr>" % (rowColor, row)
