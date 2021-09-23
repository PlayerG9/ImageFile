from imports import *
import configparser


class ConfigClass:
    def __init__(self):
        self.path = os.path.join(MEMORYDIR, 'config.ini')
        self.encoding = 'utf-16'
        self.parser = self._parse()
        atexit.register(self.on_close)

    def __del__(self):
        atexit.unregister(self.on_close)

    def _parse(self):
        parser = configparser.ConfigParser(
            allow_no_value=False,
            delimiters=('=',),
            comment_prefixes=(';', '#'),
            inline_comment_prefixes=None,
            empty_lines_in_values=True,
            default_section=configparser.DEFAULTSECT,
            interpolation=configparser.ExtendedInterpolation()
        )

        parser.read(self.path, self.encoding)

        return parser

    def __call__(self, key: str, section='Settings'):
        if not self.parser.has_section(section):
            warn(f'missing {section=} (automatically added)')
            self.parser.add_section(section)
        if not self.parser.has_option(section, key):
            warn(f'missing {key=}')
            return None
        return eval(self.parser.get(section, key), {}, {})

    def set(self, key: str, value, section='Settings'):
        self.parser.set(section, key, repr(value))

    def on_close(self):
        with open(self.path, 'w', encoding=self.encoding) as configfile:
            self.parser.write(configfile, space_around_delimiters=True)


config = ConfigClass()
