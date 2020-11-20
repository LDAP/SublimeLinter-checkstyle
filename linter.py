from SublimeLinter.lint import Linter
import os
import sublime
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError
import shutil


def download_file(url, file_name):
    with urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


class CheckstyleLinter(Linter):
    name = 'SublimeLinter-checkstyle'
    regex = (r'^\[(?:(?P<warning>WARN)|(?P<error>ERROR))\]\s'
             r'(?P<filename>.*):(?P<line>\d+):(?P<col>\d+):\s(?P<message>.*)$')
    multiline = True
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.java',
        'config': 'google_checks.xml',
        'version': 'latest',
        'debug': False
    }
    debug = False
    checkstyle_jar = None

    def cmd(self):
        settings = self.settings
        self.debug = settings.get('debug')

        try:
            version = self.checkstyle_version()
            self.print_debug_panel('Using Checkstyle {}'.format(version))

            # Get checkstyle jar
            self.checkstyle_jar = self.checkstyle_jar_path(version)
            if os.path.isfile(self.checkstyle_jar):
                self.print_debug_panel('Using: ' + self.checkstyle_jar)
            else:
                self.print_debug_panel('{} does not exists'.format(
                    self.checkstyle_jar))
                url = self.download_url(version)
                self.print_debug_panel("Make sure folder exists")
                os.makedirs(self.plugin_dir(), exist_ok=True)
                self.print_debug_panel("Downloading from {}".format(url))
                download_file(url, self.checkstyle_jar)
                self.cleanup()

        except URLError:
            # Search existing jar if maven does not respond
            jars = os.listdir(self.plugin_dir())
            if jars:
                self.checkstyle_jar = os.path.join(self.plugin_dir(), jars[0])

        # Build command
        command = ['java', '-jar', '{}'.format(self.checkstyle_jar)]
        checkstyle_config = settings.get('config')
        self.print_debug_panel('Using config: {}'
                               .format(checkstyle_config))
        command += ['-c', '{}'.format(checkstyle_config)]
        command += ['${file_on_disk}']
        command = tuple(command)
        self.print_debug_panel('Executing {}'.format(command))
        return command

    def plugin_dir(self) -> str:
        return os.path.abspath(os.path.join(sublime.cache_path(),
                                            "..", "Package Storage",
                                            self.name))

    def download_base_url(self) -> str:
        return 'https://github.com/checkstyle/checkstyle/releases/download/'

    def download_url(self, version) -> str:
        return self.download_base_url() +\
            'checkstyle-{}/'.format(version) +\
            self.jar_filename(version)

    def checkstyle_version(self) -> str:
        settings = self.settings
        version = settings.get('version')
        if version == 'latest':
            self.print_debug_panel('Polling current checkstyle'
                                   'version from Maven')
            xml_url = 'https://repo1.maven.org/maven2/'\
                'com/puppycrawl/tools/checkstyle/'\
                'maven-metadata.xml'
            with urlopen(xml_url) as f:
                v_tree = ET.parse(f)
                v_root = v_tree.getroot()
                return v_root[2][1].text
        else:
            return version

    def jar_filename(self, version):
        return 'checkstyle-{}-all.jar'.format(version)

    def print_debug_panel(self, msg):
        if self.debug is False:
            return
        window = sublime.active_window()
        debug_panel = window.find_output_panel(self.name)
        if debug_panel is None:
            debug_panel = window.create_output_panel(self.name)
        debug_panel.run_command("append", {"characters": '{}\n'.format(msg)})

    def checkstyle_jar_path(self, version):
        return os.path.abspath(os.path.join(self.plugin_dir(),
                                            self.jar_filename(version)))

    def cleanup(self):
        for f in os.listdir(self.plugin_dir()):
            self.print_debug_panel(f)
            abs_path = os.path.abspath(os.path.join(self.plugin_dir(), f))
            if abs_path != self.checkstyle_jar:
                self.print_debug_panel('Removing old jar: {}'.format(abs_path))
                os.remove(abs_path)
