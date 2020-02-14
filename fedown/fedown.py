#!/usr/bin/env python3

"""
Prints Fedora Pagure projects ownership information.

Pulls repository member information from the Pagure API and prints to stdout
accordingly to command line arguments either in human or machine readable
format.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import argparse
import json
from urllib.request import urlopen
from urllib.error import HTTPError


# https://src.fedoraproject.org
PAGURE_API_URL = 'https://src.fedoraproject.org/api/0'


class Format:
    """
    Template string index

    """
    # Index
    STDOUT_HEADER = 0
    STDOUT_LIST_HEADER = 1
    STDOUT_LIST_ITEM = 2
    STDOUT_NONE = 3

    def __init__(self):
        self.templates = {self.STDOUT_HEADER:      ' ** {} **',
                          self.STDOUT_LIST_HEADER: '\n   * {}:',
                          self.STDOUT_LIST_ITEM:   '     - {}',
                          self.STDOUT_NONE:        '{}'}


class FormatColored(Format):
    """
    Template string index with terminal colors

    """

    def __init__(self):
        Format.__init__(self)
        self.templates[self.STDOUT_HEADER] = \
            self.templates[self.STDOUT_HEADER].format(
                    '\u001b[34;1m{}\u001b[0m')
        self.templates[self.STDOUT_LIST_HEADER] = \
            self.templates[self.STDOUT_LIST_HEADER].format(
                    '\u001b[35;1m{}\u001b[0m')
        self.templates[self.STDOUT_LIST_ITEM] = \
            self.templates[self.STDOUT_LIST_ITEM].format(
                    '\u001b[36;1m{}\u001b[0m')


def _api_url_from_query(query, namespace):
    """
    Returns Pagure API request URL based on namespace

    Parameters:
        query               (str):            Username or repository
                                              (based on namespace)

    Returns:
        request_url         (str):            Resulting Pagure API request URL

    """
    if namespace == 'users':
        # query username
        return '{pagure}/user/{username}'.format(pagure=PAGURE_API_URL,
                                                 username=query)

    # query repository
    return '{pagure}/{namespace}/{repo}?{opts}'.format(pagure=PAGURE_API_URL,
                                                       namespace=namespace,
                                                       repo=query,
                                                       opts='per_page=100')


def _user_access_query_to_stdout(query, member_type, formatter,
                                 namespace='rpms', human_readable=False,
                                 skip_on_failure=False, include_forks=False,
                                 names_only=False):
    """
    Print user access information parsed from the Pagure API response to stdout

    Parameters:
        query               (list):           List of repositories or usernames
        member_type         (str):            Member type Admin/Commit/Owner
        formatter           (Format):         Format object providing templates
        namespace           (str):            Namespace to query
        human_readable      (bool):           Print in human readable format
        skip_on_failure     (bool):           Skip/Quit on failed request

    """

    def user_query_response_to_stdout(response, member_type):
        """
        Print users of a given member type to stdout.

        Parameters:
            response        (HTTPResponse):   Pagure API HTTP Response object
            member_type     (str):            Member type Admin/Commit/Owner

        """
        if response['access_users'][member_type]:
            print_formatted(member_type.title(),
                            output_format=Format.STDOUT_LIST_HEADER)
            for _ in response['access_users'][member_type]:
                print_formatted(_, output_format=Format.STDOUT_LIST_ITEM)

    def repo_query_response_to_stdout(response, member_type, user):
        """
        Print repositories of a given user to stout.

        Parameters:
            response        (HTTPResponse):   Pagure API HTTP Response object
            member_type     (str):            Member type Admin/Commit/Owner
            user            (str):            Username to query the result for

        """
        repos = [_ for _ in response['repos']
                 if user in _['access_users'][member_type]]

        # Repos
        if repos:
            print_formatted(member_type.title(),
                            output_format=Format.STDOUT_LIST_HEADER)
            for _ in repos:
                print_formatted(_['name'] if names_only else _['fullname'],
                                output_format=Format.STDOUT_LIST_ITEM)

        # Forks
        if member_type == 'owner' and include_forks:
            if response['forks']:
                print_formatted('Forks',
                                output_format=Format.STDOUT_LIST_HEADER)
                for _ in response['forks']:
                    print_formatted(_['name'] if names_only else _['fullname'],
                                    output_format=Format.STDOUT_LIST_ITEM)

    def print_formatted(text, output_format=Format.STDOUT_NONE,
                        output=sys.stdout):
        """
        Print text with a given format

        Parameters:
            text            (str):            Text of the header
            format          (int):            Text format

        """
        if human_readable and output_format != Format.STDOUT_NONE:
            print_formatted(formatter.templates[output_format].format(text))
        elif output_format == Format.STDOUT_LIST_HEADER \
                or output_format == Format.STDOUT_HEADER:
            pass
        elif output_format == Format.STDOUT_LIST_ITEM:
            output_format = Format.STDOUT_NONE
            print_formatted(formatter.templates[output_format].format(text))
        else:
            output.write('{}\n' .format(
                formatter.templates[Format.STDOUT_NONE].format(text)))

    def print_separator(length=30):
        """
        Print visual separator line

        Parameters:
            length          (int):            Length of the separator line

        """
        # Output for user queries is typically longer
        if namespace == 'users':
            length = 80

        if human_readable and len(query) > 1:
            print_formatted('-' * length, output_format=Format.STDOUT_NONE)

    print_separator()

    for q in query:
        request_url = _api_url_from_query(q, namespace)

        try:
            # Load API response JSON returned by urlopen request
            response = json.load(urlopen(request_url))

            # Load next repos pages
            while 'repos_pagination' in response \
                    and response['repos_pagination']['next']:
                next_response = json.load(urlopen(
                    response['repos_pagination']['next']))
                response['repos'] += next_response['repos']
                response['repos_pagination']['next'] = \
                    next_response['repos_pagination']['next']

            # Load next forks pages
            if include_forks:
                while 'forks_pagination' in response \
                        and response['forks_pagination']['next']:
                    next_response = json.load(urlopen(
                        response['forks_pagination']['next']))
                    response['forks'] += next_response['forks']
                    response['forks_pagination']['next'] = \
                        next_response['forks_pagination']['next']
        except HTTPError as err:
            print_formatted(request_url, output=sys.stderr)
            if skip_on_failure:
                # skip on failure
                print_formatted('{}. Skipping..'.format(err),
                                output=sys.stderr)
                print_separator()
                continue
            else:
                # quit on failure
                print_formatted('{}. Quitting..'.format(err),
                                output=sys.stderr)
                print_formatted('Use --skip-on-failure option to skip.',
                                output=sys.stderr)
                sys.exit(2)
        else:
            # Print username for each query
            if namespace == 'users':
                print_formatted(q, output_format=Format.STDOUT_HEADER)

            # print to stdout
            if namespace == 'users':
                # ## Human readable format:
                # | ** USERNAME **
                # |
                # |  * MEMBER_TYPE
                # |    - REPOSITORY
                # |    - REPOSITORY
                # ## Normal format:
                # |REPOSITORY
                # |REPOSITORY
                if member_type == 'all':
                    repo_query_response_to_stdout(response, 'owner', q)
                    repo_query_response_to_stdout(response, 'admin', q)
                    repo_query_response_to_stdout(response, 'commit', q)
                elif member_type == 'owner':
                    repo_query_response_to_stdout(response, member_type, q)
                elif member_type == 'admin':
                    repo_query_response_to_stdout(response, member_type, q)
                elif member_type == 'commit':
                    repo_query_response_to_stdout(response, member_type, q)

                print_separator()
            else:
                # Human readable format:
                # | ** FULLNAME **
                # |
                # |   * MEMBER_TYPE
                # |     - USERNAME
                # |     - USERNAME
                # Normal format:
                # |USERNAME
                # |USERNAME
                if human_readable:
                    print_formatted(response['fullname'],
                                    output_format=Format.STDOUT_HEADER)
                if member_type == 'all':
                    user_query_response_to_stdout(response, 'owner')
                    user_query_response_to_stdout(response, 'admin')
                    user_query_response_to_stdout(response, 'commit')
                elif member_type == 'owner':
                    user_query_response_to_stdout(response, member_type)
                elif member_type == 'admin':
                    user_query_response_to_stdout(response, member_type)
                elif member_type == 'commit':
                    user_query_response_to_stdout(response, member_type)

                print_separator()


def main():
    """
    Program execution entry point with argument parsing using argparse.

    """
    desc = 'Print Fedora Pagure repo ownership information.'
    version = '0.1'

    parser = argparse.ArgumentParser(description=desc)

    # member type
    parser.add_argument('-t', '--type', type=str, choices={'all',
                                                           'owner',
                                                           'admin',
                                                           'commit'},
                        default='owner',
                        help='Pagure access type to query (default: owner)')
    # namespace
    parser.add_argument('-n', '--namespace', type=str, choices={'rpms',
                                                                'modules',
                                                                'containers',
                                                                'tests',
                                                                'users'},
                        default='rpms',
                        help='Pagure namespace to query (default: rpms)')
    # repo(s) or user(s)
    parser.add_argument('query', nargs='+', type=str,
                        help='Pagure repo(s) or user(s) to query')
    # skip on failure
    parser.add_argument('-S', '--skip-on-failure', action='store_true',
                        default=False,
                        help='Skip on request failure (default: True)')
    # colors
    parser.add_argument('-C', '--colors', action='store_true',
                        default=False,
                        help='Use colors for stdout')
    # human readable output
    parser.add_argument('-H', '--human-readable', action='store_true',
                        default=False,
                        help='Human readable format (default: False)')
    # Print names only on user query
    parser.add_argument('-N', '--names-only', action='store_true',
                        default=False,
                        help='Do not print repo fullname (default: False)')
    # Include forks on user query
    parser.add_argument('-F', '--include-forks', action='store_true',
                        default=False,
                        help='Include forks (default: False)')
    # Print version information and exit
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(version))
    args = parser.parse_args()

    if args.colors:
        formatter = FormatColored()
    else:
        formatter = Format()

    _user_access_query_to_stdout(args.query,
                                 args.type,
                                 formatter=formatter,
                                 namespace=args.namespace,
                                 human_readable=args.human_readable,
                                 skip_on_failure=args.skip_on_failure,
                                 include_forks=args.include_forks,
                                 names_only=args.names_only)


if __name__ == '__main__':
    main()
