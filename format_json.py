import sublime, sublime_plugin
import json

class FormatJsonCommand(sublime_plugin.TextCommand):
    """
    Format a JSON selection using Python's JSON module.  If there is no current
    selection, format the entire file.
    """
    def run(self, edit):
        view = self.view
        for selection in view.sel():
            if selection.empty(): selection = sublime.Region(0, view.size())

            # Only try to format selections that appear to be JSON.
            if view.score_selector(selection.a, "source.json"):
                try:
                    json_object = json.loads(view.substr(selection))
                except ValueError as e:
                    sublime.error_message(str(e))
                else:
                    json_string = json.dumps(json_object, indent=4)
                    view.replace(edit, selection, json_string)
