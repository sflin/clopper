import untangle

class MvnVersionWalker():
    """ This is the backend implementation that assumes that we are tracking the performance of a
     Java/mvn project over the course of Maven releases. As this backend does not actually compile
     the project, it is a fair bit faster than other backends, and does not actually require
     the source code of the project. Instead, it only needs a JMH project with the benchmarks.
     The actual project is downloaded as Maven releases, typically from Maven Central.
    """

    def __init__(self, config_file):
        self.config = self.parse_config(config_file)

    def parse_config(self, config_file):
        return Configuration(config_file)

    def generate_version_list(self, start = None, end = None, step = None, **kwargs):

        # note that this implementation ignores "step"

        # invoked as self.generate_version_list(config), this really just returns the
        # list given in the XML config file

        # assign additional defaults
        if not start:
            start = self.config.project.versions[0]
        if not end:
            end = self.config.project.versions[-1]

        start_slice = self.config.project.versions.index(start)
        end_slice = self.config.project.versions.index(end) + 1
        return self.config.project.versions[start_slice:end_slice]


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
        if self.config['type'] != "MvnVersionWalker":
            raise RuntimeError("Unexpected configuration type: "+self.config['type'])

        self.project = ProjectConfig(self.config)

class ProjectConfig:

    def __init__(self, config):
        self.versions = []
        for v in config.project.versions.version:
            self.versions.append(str(v.cdata).strip())
