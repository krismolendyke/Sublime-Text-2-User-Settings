import sublime, sublime_plugin
import os
import functools
import Growl
import re

class ExecAndGrowlCommand(sublime_plugin.WindowCommand,
                          __import__("exec").ProcessListener):
    """
    Execute a command and Growl when finished.  This command depends on Growl.
    You will need the following from http://growl.info:

    - The Growl binary itself
    - The Growl SDK

    After installing Growl, open up the SDK disk image and follow the
    instructions here to install the Python bindings:

    http://growl.info/documentation/developer/python-support.php

    Be aware of which version of python the bindings are being installed to.
    Sublime Text 2 currently runs in 2.6 so if you do not install the bindings
    module to that version they will not be available.
    """

    def run(self, cmd=[], file_regex="", line_regex="", working_dir="",
            encoding="utf-8", env={}, show_output=False, quiet=False,
            kill=False,
            # Catches "path" and "shell"
            **kwargs):

        # Growl configuration and registration.
        self.growlIcon = Growl.Image.imageWithIconForCurrentApplication()
        self.growlNotification = "st2"
        self.growlNotifier = Growl.GrowlNotifier(
            applicationName = "Sublime Text 2",
            applicationIcon = self.growlIcon,
            notifications = [self.growlNotification]
        )
        self.growlNotifier.register()

        self.errorDetails = ""
        self.cmdString = " ".join(cmd)

        if kill:
            if self.proc:
                self.proc.kill()
                self.proc = None
                self.append_data(None, "[Cancelled]")
            return

        if not hasattr(self, 'output_view'):
            # Try not to call get_output_panel until the regexes are assigned
            self.output_view = self.window.get_output_panel("exec")

        # Default the to the current files directory if no working directory was given
        if (working_dir == "" and self.window.active_view()
                        and self.window.active_view().file_name() != ""):
            working_dir = os.path.dirname(self.window.active_view().file_name())

        self.output_view.settings().set("result_file_regex", file_regex)
        self.output_view.settings().set("result_line_regex", line_regex)
        self.output_view.settings().set("result_base_dir", working_dir)

        # Call get_output_panel a second time after assigning the above
        # settings, so that it'll be picked up as a result buffer
        self.window.get_output_panel("exec")

        self.encoding = encoding
        self.quiet = quiet

        self.proc = None
        if not self.quiet:
            print "Running " + " ".join(cmd)
            self.growl(cmd[0], description=" ".join(cmd[1:]))

        if show_output:
            self.window.run_command("show_panel", {"panel": "output.exec"})

        merged_env = env.copy()
        if self.window.active_view():
            user_env = self.window.active_view().settings().get('build_env')
            if user_env:
                merged_env.update(user_env)

        # Change to the working dir, rather than spawning the process with it,
        # so that emitted working dir relative path names make sense
        if working_dir != "":
            os.chdir(working_dir)

        err_type = OSError
        if os.name == "nt":
            err_type = WindowsError

        try:
            # Forward kwargs to AsyncProcess
            self.proc = __import__("exec").AsyncProcess(cmd, merged_env, self,
                                                        **kwargs)
        except err_type as e:
            self.append_data(None, str(e) + "\n")
            if not self.quiet:
                self.append_data(None, "[Finished]")

    def is_enabled(self, kill=False):
        if kill:
            return hasattr(self, "proc") and self.proc and self.proc.poll()
        else:
            return True

    def append_data(self, proc, data):
        if proc != self.proc:
            # a second call to exec has been made before the first one
            # finished, ignore it instead of intermingling the output.
            if proc:
                proc.kill()
            return

        try:
            str = data.decode(self.encoding)
        except:
            str = "[Decode error - output not " + self.encoding + "]"
            proc = None

        # Normalize newlines, Sublime Text always uses a single \n separator
        # in memory.
        str = str.replace('\r\n', '\n').replace('\r', '\n')

        # Simple error detail collection to throw into Growl notification
        if re.search('ERROR', str):
            self.errorDetails += str
        elif re.search('^fail:', str):
            self.errorDetails += str

        selection_was_at_end = (len(self.output_view.sel()) == 1
            and self.output_view.sel()[0]
                == sublime.Region(self.output_view.size()))
        self.output_view.set_read_only(False)
        edit = self.output_view.begin_edit()
        self.output_view.insert(edit, self.output_view.size(), str)
        if selection_was_at_end:
            self.output_view.show(self.output_view.size())
        self.output_view.end_edit(edit)
        self.output_view.set_read_only(True)

    def growl(self, title="Finished", description="Execution complete.",
              sticky=False):
        self.growlNotifier.notify(self.growlNotification, title, description,
                                  sticky = sticky)

    def finish(self, proc):
        if not self.quiet:
            self.append_data(proc, "[Finished]")
        if proc != self.proc:
            return

        returncode = proc.proc.poll()
        if returncode == None or returncode == 0:
            self.growl("Success", self.cmdString)
        else:
            if len(self.errorDetails) > 0:
                errorDetails = self.errorDetails
            else:
                errorDetails = "%s returned %d" % (self.cmdString, returncode)

            self.growl("Error", errorDetails, sticky = True)

    def on_data(self, proc, data):
        sublime.set_timeout(functools.partial(self.append_data, proc, data), 0)

    def on_finished(self, proc):
        sublime.set_timeout(functools.partial(self.finish, proc), 0)
