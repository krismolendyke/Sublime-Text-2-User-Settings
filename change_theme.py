import sublime, sublime_plugin

class ChangeThemeCommand(sublime_plugin.WindowCommand):
    def quick_panel_callback(self, index):
        if index == -1:
            return

        self.window.run_command("set_user_setting", {
            "file": "Base File.sublime-settings",
            "setting": "color_scheme",
            "value": "Packages/Color Scheme - Default/%s" % (
                ChangeThemeCommand.themes[index]["color_scheme"])
        })

        self.window.run_command("set_user_setting", {
            "file": "Global.sublime-settings",
            "setting": "theme",
            "value": ChangeThemeCommand.themes[index]["theme"]
        })

        print ChangeThemeCommand.themes[index]

    themes = [
        {
            "quick_panel": ["Light",
                            "Color Scheme: Solarized Light",
                            "Theme: Soda Light"],
            "color_scheme": "Solarized (Light).tmTheme",
            "theme": "Soda Light.sublime-theme"
        },
        {
            "quick_panel": ["Dark",
                            "Color Scheme: Monokai",
                            "Theme: Soda Dark"],
            "color_scheme": "Monokai.tmTheme",
            "theme": "Soda Dark.sublime-theme"
        }
    ]

    def run(self):
        self.window.show_quick_panel(
            [x["quick_panel"] for x in ChangeThemeCommand.themes],
            self.quick_panel_callback)
