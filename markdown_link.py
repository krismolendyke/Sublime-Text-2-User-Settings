import sublime, sublime_plugin
import os

class MarkdownLinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        contents = "[${1:$TM_SELECTED_TEXT}](${2:%s})" % sublime.get_clipboard()
        self.view.run_command("insert_snippet", {"contents": contents})

