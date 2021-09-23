from imports import *
import configparser


class Language:
    def __init__(self, language_name: str, encoding: str):
        self.path = os.path.join(APPDIR, 'languages', '%s.lang' % language_name)
        if not os.path.exists(self.path):
            raise FileNotFoundError(f'languagefile for {language_name} not found')
        self.encoding = encoding
        self.parser: configparser.ConfigParser = self._parse()
        atexit.register(self.cleanup)
        # self.debug_print()

    def __del__(self):
        atexit.unregister(self.cleanup)

    def cleanup(self):
        if DEBUG:
            with open(self.path, 'w', encoding=self.encoding) as langfile:
                self.parser.write(langfile, space_around_delimiters=True)

    def debug_print(self):
        pprint({
            k: {k2: v2 for k2, v2 in v.items()}
            for k, v in self.parser.items()
        })

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

    def __call__(self, text: str) -> str:
        section = self._get_file()
        if not self.parser.has_section(section):
            warn(f'missing {section=} {"(automatically added)" if DEBUG else ""}')
            if DEBUG:
                self.parser.add_section(section)
            return text
        if not self.parser.has_option(section, text):
            warn(f'missing {text=} (in {section=}) {"(automatically added)" if DEBUG else ""}')
            if DEBUG:
                self.parser.set(section, text, 'TO_REPLACE')
            return text
        return self.parser.get(section, text)

    @staticmethod
    def _get_file():
        # pprint(traceback.StackSummary.extract(traceback.walk_stack(None)))

        stack = list(traceback.walk_stack(None))
        frame, _ = stack[1]  # get stack (lineno)
        code = frame.f_code  # get code-object
        filename = code.co_filename  # get filename
        filename = os.path.splitext(filename)[0]  # remove .py extension
        return os.path.relpath(filename, APPDIR)  # make path relativ


def get_language():
    area, encoding = locale.getlocale()
    langname = area.split('_')[0]
    print(f'{area=} {encoding=}')
    # pprint(locale.locale_alias)
    try:
        return Language(langname, encoding)
    except FileNotFoundError:
        return Language('en', 'utf-8')
