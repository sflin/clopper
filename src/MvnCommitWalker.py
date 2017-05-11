import datetime

import untangle
import os
from GitRepoHandler import GitRepoHandler


class MvnCommitWalker():
    """ This is the backend implementation that assumes that we are tracking the performance of a
     Git/Java/mvn project between commits.
    """

    def __init__(self, config_file):
        self.config = self.parse_config(config_file)

    def parse_config(self, config_file):
        return Configuration(config_file)

    def generate_version_list(self, start = None, end = None, step = None, **kwargs):
        
        cwd = os.getcwd()
        repo = GitRepoHandler(self.config.project.dir)

        # we somewhat awkwardly have two completely different ways to iterate here -
        # over dates and over Git versions / commits
        if kwargs['mode'] == 'commit-mode':
            if not start:
                start = self.config.project.start
            if not end:
                end = self.config.project.end
            versions = repo.find_commits_between(start, end, kwargs['skip-noncode'])
        elif kwargs['mode'] == 'time-mode':
            if not start:
                start = self.config.project.start
            if not end:
                end = self.config.project.end
            versions = MvnCommitWalker.dates_between(start, end)
        else:
            raise RuntimeError("Mode not yet implemented.")
        if step:
            versions = versions[0::step]
        os.chdir(cwd)
        return versions

    @staticmethod
    def dates_between(start, end):
        """ Helper method that lists all the dates between a start and end date.
        The start and end date are always included.

        :param start:
        :param end:
        :return:
        """

        dates = []
        date = datetime.datetime.strptime(start, "%Y/%m/%d")
        date_end = datetime.datetime.strptime(end, "%Y/%m/%d")
        while date < date_end:
            dates.append(date.strftime("%Y/%m/%d"))
            date += datetime.timedelta(days=1)
        dates.append(date_end.strftime("%Y/%m/%d"))
        return dates


class Configuration:
    """Wrapper for the XML-based config files used by the mvn version walker backend.
    """

    def __init__(self, config_path):
        """ Construct a new configuration wrapper from a well-formed XML config document.
        :param configPath: Path to the XML config file
        :return: Parsed configuration
        """

        self.config = untangle.parse(config_path).historian

        # make sure that we are looking at the right kind of config file
        if self.config['type'] != "MvnCommitWalker":
            raise RuntimeError("Unexpected configuration type: "+self.config['type'])

        self.project = ProjectConfig(self.config)
        self.arguments = str(self.config.jmh_arguments.cdata).strip()


class ProjectConfig:

    def __init__(self, config):
        self.dir = str(config.project["dir"])
        self.start = str(config.project.versions.start.cdata).strip()
        self.end = str(config.project.versions.end.cdata).strip()

