import sublime, sublime_plugin
import re
import datetime

class AddTimeStampCommand(sublime_plugin.TextCommand):
    def run(self, edit, contents):
        format = re.search(r"\$\$(.*?)\$\$", contents).groups()[0]
        result = datetime.datetime.now().strftime(format)
        contents = re.sub(r"\$\$.*?\$\$", result, contents)
        self.view.run_command('insert_snippet', {'contents': contents})
