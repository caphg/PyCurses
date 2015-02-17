import json
import time
import requests
import curses


APP_URL = "http://airwiener.appspot.com/service-status/"
NETWORKS_LIST = ["wiener", "kunst"]


def fetch_data():
    res = []
    for network in NETWORKS_LIST:
        resp = requests.get(APP_URL + network).json()
        res.append(resp)
    return res


class MenuDemo:
    DOWN = 1
    UP = -1
    SPACE_KEY = 32
    ESC_KEY = 27

    PREFIX_SELECTED = ''
    PREFIX_DESELECTED = ''

    outputLines = []
    screen = None

    def __init__(self, all_data):
        self.data = all_data
        i = 0

        self.screen = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.border(0)
        self.topLineNum = 0
        self.highlightLineNum = 0
        self.markedLineNums = []
        while True:
            i += 1
            self.getOutputLines(i)
            self.run()
            time.sleep(5)

    def run(self):
        self.displayScreen()

    def markLine(self):
        linenum = self.topLineNum + self.highlightLineNum
        if linenum in self.markedLineNums:
            self.markedLineNums.remove(linenum)
        else:
            self.markedLineNums.append(linenum)

    def getOutputLines(self, i):
        self.outputLines = []
        for batch in self.data[i % len(self.data)]:
            self.outputLines.append("*****NETWORK*****")
            self.outputLines.append("Network Name: %s" % batch.get('networkName'))
            self.outputLines.append("Total users: %s" % batch.get('totalUsers'))
            self.outputLines.append("Total usage: %s kb" % batch.get('totalUsage'))
            self.outputLines.append("*****Nodes*****")
            for node in batch.get('nodeData'):
                self.outputLines.append("Node Name: %s --> " % node.get('name'))
                #self.outputLines.append("")
                self.outputLines.append("Active: %s" % node.get('active'))
                self.outputLines.append("Mac: %s" % node.get('mac'))
                self.outputLines.append("Usage in last day: %s" % node.get('usageInLastDay'))
                self.outputLines.append("Users in last day: %s" % node.get('usersInLastDay'))
        self.nOutputLines = len(self.outputLines)

    def displayScreen(self):
        # clear screen
        self.screen.erase()

        # now paint the rows
        top = self.topLineNum
        bottom = self.topLineNum+curses.LINES
        for (index,line,) in enumerate(self.outputLines[top:bottom]):
            linenum = self.topLineNum + index
            if linenum in self.markedLineNums:
                prefix = self.PREFIX_SELECTED
            else:
                prefix = self.PREFIX_DESELECTED

            # highlight current line
            if index != self.highlightLineNum:
                if line.startswith('Active:'):
                    if 'true' in line.split('Active:')[1]:
                        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_GREEN)
                        self.screen.addstr(line, curses.color_pair(1))
                    else:
                        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_RED)
                        self.screen.addstr(line, curses.color_pair(1))
                else:
                    self.screen.addstr(index, 0, line)
            else:
                self.screen.addstr(index, 0, line, curses.A_BOLD)
        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP
            return
        elif increment == self.DOWN and nextLineNum == curses.LINES and (self.topLineNum+curses.LINES) != self.nOutputLines:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0 or self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (self.topLineNum+self.highlightLineNum+1) != self.nOutputLines and self.highlightLineNum != curses.LINES:
            self.highlightLineNum = nextLineNum

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()


if __name__ == '__main__':
    print 'Initializing...'

    print 'Done.'

    print 'Fetching data...'
    data = fetch_data()
    print 'Done.'

    print 'Making things nice...'
    MenuDemo(data)
    print 'Done.'