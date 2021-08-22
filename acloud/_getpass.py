#!/usr/bin/python3

"""

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import os
import sys
import time

if os.name == "nt":
    import msvcrt
    from msvcrt import getch as _win_getch
else:
    import tty
    import termios


class GetPass(object):
    def _unix_getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _getuser(self, prompt="Username : "):
        """Prompt for Username """
        if sys.version_info[:2] >= (3, 0):
            sys.stdout.write("{}".format(prompt))
            sys.stdout.flush()
            username = input()
        else:
            sys.stdout.write("{}".format(prompt))
            sys.stdout.flush()
            username = raw_input()
        return username

    def _getpass(self, prompt="Password : "):
        """Prompt for password and replace each character by asterik (*)"""
        sys.stdout.write("{}".format(prompt))
        sys.stdout.flush()
        pw = ""
        while True:
            c = _win_getch() if os.name == "nt" else self._unix_getch()
            if os.name == "nt":
                if ord(c) == 13:
                    break
                if ord(c) == 3:
                    raise KeyboardInterrupt
                if ord(c) == 8:
                    if len(pw) > 0:
                        pw = pw[:-1]
                        s = "*" * len(pw)
                        sys.stdout.write("\033[2K\033[1G")
                        sys.stdout.flush()
                        sys.stdout.write("\r\r\r{}{}".format(prompt, s))
                        sys.stdout.flush()
                    else:
                        pass
                else:
                    if ord(c) == 27:
                        pass
                    elif ord(c) == 224:
                        c = _win_getch()
                        pass
                    else:
                        if sys.version_info[:2] >= (3, 0):
                            pw = pw + c.decode("utf-8")
                        else:
                            pw = pw + c
                        sys.stdout.write("*")
                        sys.stdout.flush()
            else:
                if ord(c) == 13:
                    break
                if ord(c) == 3:
                    raise KeyboardInterrupt
                if ord(c) == 127:
                    if len(pw) > 0:
                        pw = pw[:-1]
                        s = "*" * len(pw)
                        sys.stdout.write("\033[2K\033[1G")
                        sys.stdout.flush()
                        sys.stdout.write("\r\r\r{}{}".format(prompt, s))
                        sys.stdout.flush()
                    else:
                        pass
                else:
                    if ord(c) == 27:
                        pass
                    elif ord(c) == 91 or ord(c) == 27:
                        c = self._unix_getch()
                        pass
                    else:
                        pw = pw + c
                        sys.stdout.write("*")
                        sys.stdout.flush()

        return pw
