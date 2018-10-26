# -*- coding: utf-8 -*-

"""Main module."""
import re
import string
import sys
from cStringIO import StringIO
from itertools import ifilter, groupby
from tokenize import generate_tokens, COMMENT, untokenize, TokenError

DEFAULT_FORMAT = re.compile(
    r'(?P<filename>.+):'
    r'(?P<lineno>\d+):'
    r'(?P<column>\d+):'
    r'\s*(?P<errcode>[A-Z0-9]+)\s+(?P<message>.+)'
)

VIOLATIONS_REGEX = re.compile(r'noqa:\s*(?P<violations>[A-Z0-9,]+)(\s(?P<rest>.*))?')


def is_whitespace(line):
    return all((char in string.whitespace for char in line))


def _parse_default_format(line):
    match = DEFAULT_FORMAT.match(line)
    if not match:
        return None

    result = {
        'filename': match.group('filename'),
        'lineno': int(match.group('lineno')),
        'column': int(match.group('column')),
        'errcode': match.group('errcode'),
        'message': match.group('message'),
    }
    return result


def build_comment(violations, comment=''):
    match = VIOLATIONS_REGEX.match(comment)

    if match:
        current_violations = set(','.split(match.group('violations')))
        current_violations.remove(',')  # HACK: need to figure out why this is happening
        current_violations |= set(violations)  # merge all the violations

        violations = tuple(current_violations)
        comment = match.group('rest') if match.group('rest') is not None else ''

    whitespace = ' ' if comment else ''
    return 'noqa:{violations}{whitespace}{comment}'.format(violations=','.join(violations), comment=comment, whitespace=whitespace)


def disable_violation(line, violations):
    """ disables violation comment on a given line """
    comment_position = None

    # Find the location of any pre-existing comment, if any
    try:
        for token_num, token_val, start, _, _ in generate_tokens(StringIO(line).readline):
            if token_num == COMMENT:
                comment_position = start[1]
    except TokenError:
        pass

    if comment_position is None:
        # strip out the last new line in the line
        line = line.rstrip('\n')
        # if the line has code, we should add our comment after 2 spaces (PEP8)
        whitespace = '' if is_whitespace(line) else '  '
        line = '{line}{whitespace}# {comment}\n'.format(line=line, comment=build_comment(violations), whitespace=whitespace)
    else:
        existing_comment = line[comment_position:].strip('#').strip()
        line = line[:comment_position] + '# {comment}\n'.format(comment=build_comment(violations, existing_comment))

    return line


def main():
    # violations = (_parse_default_format(line) for line in sys.stdin)
    with open(sys.argv[1]) as f:
        violations = [_parse_default_format(line) for line in f]

    for filename, results in groupby(ifilter(None, violations), key=lambda x: x['filename']):
        with open(filename, 'r') as f:
            # get all the lines from a single file
            lines = f.readlines()
            for lineno, lineinfo in groupby(results, key=lambda x: x['lineno']):
                # group violations per line and insert the comment
                idx = lineno - 1
                violations = list((info['errcode'] for info in lineinfo))
                try:
                    lines[idx] = disable_violation(lines[idx], violations)
                except IndexError:
                    print('exception occurred while adding {violations} {file}:{line}'.format(violations=violations, file=filename, line=lineno))

                # print('Disabling error codes: {violations} in {file}:{line}'.format(violations=violations, file=filename, line=lineno))

        with open(filename, 'w+') as f:
            f.writelines(lines)
