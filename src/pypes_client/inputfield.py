import curses


class InputField:
    def __init__(self, width, height, y, x):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.win = curses.newwin(height, width, y, x)
        self.pad = curses.newpad(height - 2, 512)
        # self.win.border()
        # self.win.refresh()
        self.pad.move(0, 0)
        self.current_x = 0
        self.current_row = 0
        self.current_input = ""

    def add_char(self, char):
        self.pad.addch(char)
        y, x = self.pad.getyx()
        self.current_row += 1
        if self.current_row >= self.width - 2:
            self.current_x += 1
        self.current_input += chr(char)

    def flush_input(self):
        msg = self.current_input
        self.pad.erase()
        self.pad.move(0, 0)
        self.current_input = ""
        self.current_row = self.current_x = 0
        return msg

    def backspace(self):
        y, x = self.pad.getyx()
        if x < 1:
            return
        self.pad.move(y, x - 1)
        self.pad.addch(" ")
        self.pad.move(y, x - 1)
        self.current_input = self.current_input[:-1]

    def refresh(self):
        self.win.box()
        self.win.noutrefresh()
        self.pad.refresh(0, self.current_x, self.y + 1, 1, self.y + 2, self.width - 2)
