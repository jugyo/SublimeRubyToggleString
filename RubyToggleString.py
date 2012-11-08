import subprocess
import sublime, sublime_plugin
import re

# NOTE: It does not support multi line.
def expand_selection_around(view, region, regexp):
    region_of_line = view.line(region)
    text_of_line = view.substr(region_of_line)
    match = find_string_around(text_of_line, regexp, region.begin() - region_of_line.begin())
    if match:
        region_of_string = sublime.Region(region_of_line.begin() + match.start(), region_of_line.begin() + match.end())
        view.sel().add(region_of_string)

def find_string_around(text, regexp, position):
    for m in re.finditer(regexp, text):
        if m.start() <= position <= m.end():
            return m
    return None

class RubyToggleStringCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            expand_selection_around(self.view, region, r'(".*?"|\'.*?\'|%Q{.*?})')

        for region in self.view.sel():
            if region.size() == 0:
                continue
            selected = self.view.substr(region)
            if selected[0] == '"':
                inner = selected[1:-1]
                inner = re.sub(r"[^\\]\'", lambda m: re.sub("'", "\\'", m.group(0)), inner)
                inner = re.sub(r'\\"', '"', inner)
                replace = "'" + inner + "'"
            elif selected[0] == "'":
                inner = selected[1:-1]
                inner = re.sub(r"\\'", "'", inner)
                inner = re.sub(r'\\"', '"', inner)
                replace = '%Q{' + inner + '}'
            elif selected[0] == "%":
                inner = selected[3:-1]
                inner = re.sub(r'[^\\]"', lambda m: re.sub('"', '\\"', m.group(0)), inner)
                inner = re.sub(r"\\'", "'", inner)
                replace = '"' + inner + '"'
            else:
                return
            self.view.replace(edit, region, replace)

class RubyToggleStringAndSymbolCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            expand_selection_around(self.view, region, r'(".*?"|\'.*?\'|:\w+)')

        for region in self.view.sel():
            if region.size() == 0:
                continue
            selected = self.view.substr(region)
            if selected[0] == '"':
                inner = selected[1:-1]
                replace = ":" + inner
            elif selected[0] == "'":
                inner = selected[1:-1]
                replace = ":" + inner
            elif selected[0] == ":":
                inner = selected[1:]
                replace = '"' + inner + '"'
            else:
                return
            self.view.replace(edit, region, replace)
