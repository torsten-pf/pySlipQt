"""
A small function to put an error message on the screen with Tkinter.

Used by GUI programs started from a desktop icon.
"""

import textwrap

try:
    from tkinter import *
except ImportError:
    print("You must install 'tkinter'")
    print("Ubuntu: apt-get install python-tk")
    print("Windows: ???")
    sys.exit(1)


def tkinter_error(msg, title=None):
    """Show an error message in a Tkinter dialog.

    msg    text message to display (may contain newlines, etc)
    title  the window title (defaults to 'ERROR')

    The whole point of this is to get *some* output from a python GUI
    program when run from an icon double-click.  We use tkinter since it's
    part of standard python and we may be trying to say something like:

        +-------------------------+
        |  You must install PyQt  |
        +-------------------------+

    Under Linux and OSX we can run the program from the commandline and we would
    see printed output.  Under Windows that's hard to do, hence this code.

    NOTE: For some reason, Ubuntu python doesn't have tkinter installed as
    part of the base install.  Do "sudo apt-get install python-tk".
    """

    ######
    # Define the Application class
    ######

    class Application(Frame):
        def createWidgets(self):
            self.LABEL = Label(self, text=self.text, font=("Courier", 14))
            self.LABEL["fg"] = "black"
            self.LABEL["bg"] = "yellow"
            self.LABEL["justify"] = "left"
            self.LABEL.pack()

        def __init__(self, text, master=None):
            self.text = text
            Frame.__init__(self, master)
            self.pack()
            self.createWidgets()
            self.tkraise()


    # set the title string
    if title is None:
        title = 'ERROR'

    # get the message text
    msg = '\n' + msg.strip() + '\n'

    msg = msg.replace('\r', '')
    msg = msg.replace('\n', '   \n   ')

    app = Application(msg)
    app.master.title(title)
    app.mainloop()


if __name__ == '__main__':
    # just a simple "smoke test" of the error notification
    long_msg = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                'sed do eiusmod tempor incididunt ut labore et dolore magna '
                'aliqua. Ut enim ad minim veniam, quis nostrud exercitation '
                'ullamco laboris nisi ut aliquip ex ea commodo consequat. '
                'Duis aute irure dolor in reprehenderit in voluptate velit '
                'esse cillum dolore eu fugiat nulla pariatur. Excepteur sint '
                'occaecat cupidatat non proident, sunt in culpa qui officia '
                'deserunt mollit anim id est laborum.'
               )

    tkinter_error('A short message with initial TAB:\n\tHello, world!\n\n'
                  'Some Unicode (你好, สวัสดี, こんにちは)\n\n'
                  'A large text paragraph. You must wrap and indent the text yourself:\n'
                      + textwrap.fill(long_msg, initial_indent='    ', subsequent_indent='    '),
                  title='Test Error Message')
