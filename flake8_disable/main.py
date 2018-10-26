# -*- coding: utf-8 -*-

"""Main module."""
import re
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


def insert_comment(line, comment):
    comment_position = None

    # Find the location of any pre-existing comment, if any
    try:
        for token_num, token_val, start, _, _ in generate_tokens(StringIO(line).readline):
            if token_num == COMMENT:
                comment_position = start[1]
    except TokenError:
        pass

    if comment_position is None:
        line = line.rstrip('\n')
        line = '{line}  # {comment}\n'.format(line=line, comment=comment)
    else:
        existing_comment = line[comment_position:].strip('#')
        line = line[:comment_position] + '# {comment} #{existing_comment}\n'.format(comment=comment, existing_comment=existing_comment)

    return line


def main():
    violations = (_parse_default_format(line) for line in sys.stdin)
    for filename, results in groupby(ifilter(None, violations), key=lambda x: x['filename']):
        with open(filename, 'r') as f:
            # get all the lines from a single file
            lines = f.readlines()
            for lineno, lineinfo in groupby(results, key=lambda x: x['lineno']):
                # group violations per line and insert the comment
                idx = lineno - 1
                comment = 'noqa: ' + ','.join((info['errcode'] for info in lineinfo))
                lines[idx] = insert_comment(lines[idx], comment)
                print('Disabling error codes: {comment} in {file}:{line}'.format(comment=comment, file=filename, line=lineno))
        with open(filename, 'w+') as f:
            f.writelines(lines)
