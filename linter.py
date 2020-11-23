from SublimeLinter.lint import Linter
from SublimeLinter.lint.linter import PermanentError
import os
import sublime
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import shutil
import logging

logger = logging.getLogger('SublimeLinter.plugin.checkstyle')


def download_file(url, file_name) -> None:
    with urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def jar_filename(version) -> str:
    return 'checkstyle-{}-all.jar'.format(version)


def jar_path(version):
    return os.path.abspath(os.path.join(plugin_dir(),
                                        jar_filename(version)))


def plugin_dir() -> str:
    return os.path.abspath(os.path.join(sublime.cache_path(),
                                        "..", "Package Storage",
                                        CACHE_FOLDER_NAME))


def download_url(version) -> str:
    return DOWNLOAD_BASE_URL +\
        'checkstyle-{}/'.format(version) +\
        jar_filename(version)


def fetch_latest_cs_version() -> str:
    global CURRENT_LATEST_CS_VERSION

    if (CURRENT_LATEST_CS_VERSION is None):
        logger.info('Polling current checkstyle'
                    'version from Maven')
        try:
            with urlopen(VERSIONS_XML_URL) as f:
                v_tree = ET.parse(f)
                v_root = v_tree.getroot()
                CURRENT_LATEST_CS_VERSION = v_root[2][1].text
            logger.info('Latest checkstyle version on Maven is {}'
                        .format(CURRENT_LATEST_CS_VERSION))
        except URLError:
            logger.warning('Latest cs version could not be fetched!')
    return CURRENT_LATEST_CS_VERSION


def cleanup(keep):
    for f in os.listdir(plugin_dir()):
        abs_path = os.path.abspath(os.path.join(plugin_dir(), f))
        if abs_path != keep:
            logger.info('Removing old jar: {}'.format(abs_path))
            os.remove(abs_path)


CURRENT_LATEST_CS_VERSION = None
DOWNLOAD_BASE_URL = 'https://github.com/checkstyle/'\
                    'checkstyle/releases/download/'
VERSIONS_XML_URL = 'https://repo1.maven.org/maven2/'\
                   'com/puppycrawl/tools/checkstyle/'\
                   'maven-metadata.xml'
DEBUG_PANEL_NAME = 'SublimeLinter-checkstyle'
CACHE_FOLDER_NAME = 'SublimeLinter-checkstyle'


class Checkstyle(Linter):
    regex = (r'^\[(?:(?P<warning>WARN)|(?P<error>ERROR))\]\s'
             r'(?P<filename>.*?):(?P<line>\d+):(?:(?P<col>\d+):)?\s'
             r'(?P<message>.*)$')
    multiline = True
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.java',
        'config': 'google_checks.xml',
        'version': 'latest'
    }

    def cmd(self):
        version = self.cs_version()
        checkstyle_jar = None

        if version is not None:
            logger.info('Using Checkstyle {}'.format(version))
            try:
                checkstyle_jar = self.provide_jar(version)
            except (HTTPError, URLError):
                pass  # checkstyle jar is None

        if checkstyle_jar is None or not os.path.isfile(checkstyle_jar):
            # Search existing jar if version not clear or jar not downloaded
            jars = os.listdir(plugin_dir())
            if jars:
                checkstyle_jar = os.path.join(plugin_dir(), jars[0])
                logger.warning('Checkstyle version cannot be '
                               'determined or downloaded. '
                               'Using existing jar {}'.format(checkstyle_jar))

            else:
                logger.error('Checkstyle version cannot be '
                             'determined or downloaded. '
                             'Check version setting and network connection')
                self.notify_failure()
                raise PermanentError()

        # Build command
        command = ['java', '-jar', '{}'.format(checkstyle_jar)]
        checkstyle_config = self.settings.get('config')
        logger.info('Using checkstyle config: {}'.format(checkstyle_config))
        command += ['-c', '{}'.format(checkstyle_config)]
        command += ['${file_on_disk}']
        command = tuple(command)
        return command

    def cs_version(self) -> str:
        """
        Returns the checkstyle version to use

        :returns:   A string representing the checkstyle version
                    or None if it could not be determined
        :rtype:     str
        """
        global CURRENT_LATEST_CS_VERSION
        version = self.settings.get('version')
        if version == 'latest':
            return fetch_latest_cs_version()  # Can be None
        else:
            return version

    def provide_jar(self, version) -> str:
        """
        Checks if the jar is locally available. If not initiates a download.

        :returns:   the path to the jar
        :rtype:     str
        """
        checkstyle_jar = jar_path(version)
        if os.path.isfile(checkstyle_jar):
            logger.info('Using existing jar: ' + checkstyle_jar)
        else:
            logger.info('{} does not exists'.format(checkstyle_jar))
            logger.info("Make sure folder exists")
            os.makedirs(plugin_dir(), exist_ok=True)
            url = download_url(version)
            logger.info("Downloading from {}".format(url))
            download_file(url, checkstyle_jar)
            cleanup(checkstyle_jar)
        return checkstyle_jar
