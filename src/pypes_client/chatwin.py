import curses


class ChatWin:
    def __init__(self, width, height, name_col_width=20):
        self.width = width
        self.height = height
        self.name_col = name_col_width
        self.msg_width = width - name_col_width - 5
        self.win = curses.newwin(height, width, 0, 0)
        self.pad = curses.newpad(1000, width - 2)
        self.win.box()
        self.win.refresh()
        self.current_y = 0
        self.current_line = 0
        self.pad.move(0, 0)

    def text_wrap(self, text, max_width):
        lines = []
        for para in text.split("\n"):
            current_line = ""
            for word in para.strip().split():
                if len(current_line) + len(word) >= max_width:
                    lines.append(current_line.strip())
                    current_line = ""
                current_line += word + " "
            lines.append(current_line.strip())
        return lines

    def add_entry(self, sender, message, color):
        y, x = self.pad.getyx()
        lines = self.text_wrap(message, self.msg_width)
        formatted = "{:>{width}}│ {}".format(
            sender[: self.name_col], lines[0], width=self.name_col
        )
        self.pad.addstr(formatted)
        self.pad.chgat(y, 0, self.name_col, curses.color_pair(color))
        self.pad.move(y + 1, 0)
        for i, line in enumerate(lines[1:]):
            formatted = "{:>{width}}│ {}".format(" ", line, width=self.name_col)
            self.pad.move(y + 1 + i, 0)
            self.pad.addstr(formatted)

        self.current_line += len(lines)
        if self.current_line >= self.height - 2:
            self.current_y += 1
        self.refresh

    def add_banner(self, text):
        y, _ = self.pad.getyx()
        margin = 10
        banner_width = self.width - 2 * margin - 2
        lines = ["┌" + "─" * banner_width + "┐"]
        for line in self.text_wrap(text, banner_width):
            lines.append("│{txt:^{width}}│".format(txt=line, width=banner_width))
            # lines.append("{txt}".format(txt=line, width=banner_width))
        lines.append("└" + "─" * banner_width + "┘")
        lines.append("\n")
        for i, line in enumerate(lines):
            self.pad.move(y + i + 1, 0)
            self.pad.addstr(line, curses.A_BOLD)
        self.current_line += len(lines)
        if self.current_line >= self.height - 2:
            self.current_y += 1
        self.refresh

    def refresh(self):
        self.win.box()
        self.win.noutrefresh()
        self.pad.refresh(self.current_y, 0, 1, 3, self.height - 3, self.width - 2)
