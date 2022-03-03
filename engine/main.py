# ibus-byrninpikak - byrninpikak IME
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2022 Harsiharsi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus
from gi.repository import GLib
from gi.repository import GObject

import os
import sys
import getopt
import gettext
import locale

from engine import EngineByrninpikak

#_ = lambda a: gettext.dgettext('ibus-tmpl', a)

class IMApp:
    def __init__(self, exec_by_ibus):
        engine_name = "byrninpikak-python" if exec_by_ibus else "byrninpikak-python (debug)"
        self.__component = \
                IBus.Component.new("org.freedesktop.IBus.Byrninpikak",
                                   "Byrninpikak Input Method",
                                   "0.0.0",
                                   "Apache",
                                   "Harsiharsi",
                                   "",
                                   "/usr/bin/exec",
                                   "ibus-byrninpikak")
        engine = IBus.EngineDesc.new("byrninpikak-python",
                                     engine_name,
                                     "byrninpikak",
                                     "ja",
                                     "Apache",
                                     "Harsiharsi",
                                     "",
                                     "us")
        self.__component.add_engine(engine)
        self.__mainloop = GLib.MainLoop()
        self.__bus = IBus.Bus()
        self.__bus.connect("disconnected", self.__bus_disconnected_cb)
        self.__factory = IBus.Factory.new(self.__bus.get_connection())
        self.__factory.add_engine("byrninpikak-python",
                GObject.type_from_name("EngineByrninpikak"))
        if exec_by_ibus:
            self.__bus.request_name("org.freedesktop.IBus.Byrninpikak", 0)
        else:
            self.__bus.register_component(self.__component)
            self.__bus.set_global_engine_async(
                    "byrninpikak-python", -1, None, None, None)

    def run(self):
        self.__mainloop.run()

    def __bus_disconnected_cb(self, bus):
        self.__mainloop.quit()


def launch_engine(exec_by_ibus):
    IBus.init()
    IMApp(exec_by_ibus).run()

def print_help(v = 0):
    print(_("Hello"));
    print("-i, --ibus             executed by IBus.")
    print("-h, --help             show this message.")
    print("-d, --daemonize        daemonize ibus")
    sys.exit(v)

def main():
    try:
        locale.setlocale(locale.LC_ALL, "")
    except:
        pass

    exec_by_ibus = False
    daemonize = False

    shortopt = "ihd"
    longopt = ["ibus", "help", "daemonize"]

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
    except getopt.GetoptError as err:
        print_help(1)

    for o, a in opts:
        if o in ("-h", "--help"):
            print_help(sys.stdout)
        elif o in ("-d", "--daemonize"):
            daemonize = True
        elif o in ("-i", "--ibus"):
            exec_by_ibus = True
        else:
            sys.stderr.write("Unknown argument: %s\n" % o)
            print_help(1)

    if daemonize:
        if os.fork():
            sys.exit()

    launch_engine(exec_by_ibus)

if __name__ == "__main__":
    main()
