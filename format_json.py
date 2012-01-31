import sublime, sublime_plugin
import json
import decimal

class FormatJsonCommand(sublime_plugin.TextCommand):
    """
    Format a JSON selection using Python's JSON module.  If there is no current
    selection, format the entire file.  The selection can be pretty printed or
    compacted into a single line.
    """
    def quick_panel_callback(self, index):
        if index == -1:
            return
        elif index == 0:
            json_string = json.dumps(self.json_object, indent=4, sort_keys=True)
            self.view.replace(self.edit, self.selection, json_string)
        elif index == 1:
            json_string = json.dumps(self.json_object, separators=(',',':'),
                                     sort_keys=True)
            self.view.replace(self.edit, self.selection, json_string)

    def run(self, edit):
        self.edit = edit
        view = self.view

        for selection in view.sel():
            if selection.empty():
                self.selection = sublime.Region(0, view.size())

            # Only try to format selections that appear to be JSON.
            if view.score_selector(selection.a, "source.json"):
                try:
                    self.json_object = json.loads(view.substr(self.selection),
                                                  parse_float=decimal.Decimal)
                except ValueError as e:
                    sublime.error_message(str(e))
                else:
                    view.window().show_quick_panel(["Pretty Print", "Compact"],
                                                   self.quick_panel_callback)
