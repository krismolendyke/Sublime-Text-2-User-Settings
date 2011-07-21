import sublime, sublime_plugin

class ToggleQuotesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    for region in self.view.sel():
      scope = self.view.scope_name(region.begin())

      if scope.find('string.quoted.') > -1:
        start = end = region.begin()

        if scope.find('string.quoted.double') > -1:
          l = '"'

        else:
          l = '\''

        if self.view.substr(start) ==  l:
          scope = self.view.scope_name(start - 1)

          if scope.find('string.quoted.') > -1:
            start = end = start - 1

        while start >= 0:
          c = self.view.substr(start)

          if c == l and not self.is_escaped(start):
            break

          else:
            start -= 1

        end = start + 1

        while (end - start) <= self.view.size():
          c = self.view.substr(end)

          if c == l and not self.is_escaped(end):
            break

          else:
            end += 1

        if start >= 0 and end <= self.view.size():
          if l == '\'':
            r = '"'

          else:
            r = '\''

          self.view.replace(edit, sublime.Region(start, start + 1), r)
          self.view.replace(edit, sublime.Region(end, end + 1), r)

          while start < (end - 1):
            start += 1

            c = self.view.substr(start)

            if c == r and not self.is_escaped(start):
              self.view.insert(edit, start, '\\')
              end += 1

            elif c == l and self.is_escaped(start):
              self.view.replace(edit, sublime.Region(start - 1, start), '')
              end -= 1

    # fix for cursor moving outside string, thanks to adzenith
    rs = self.view.sel()
    scope = self.view.scope_name(rs[0].begin())

    if scope.find('string.quoted') == -1:
      p = rs[0].begin() - 1
      region = sublime.Region(p, p)

      rs.clear()
      rs.add(region)

  def is_escaped(self, point):
    point -= 1
    i = 0

    while self.view.substr(point) == '\\':
      i += 1
      point -= 1

    return i % 2 == 1
