#!/usr/bin/env python3

import re
import argparse
import os

def replace_redmine_wiki_with_textile_link(page_content):
    """
    Restructure links from [[Wiki Page]] to "Wiki page":wiki_page.md
    """
    proper = re.sub(pattern = r'\[\[(.*)\]\]', # capture text within [[]] tags
                    # must use a lambda to allow replacing within a group
                    # https://stackoverflow.com/a/56393435/7418735
                    repl = (lambda match :
                            # link text
                            '"' + match.expand(r"\1") + '"' +
                            # link path
                            ':' + find_nested_wiki_path(match.expand(r"\1").replace(" ", "_")) + "/"
                            ),
                    string = page_content)
    return proper


def find_nested_wiki_path(search):
    search_file = search + ".textile"
    for root, dirs, files in os.walk(os.path.dirname(args.input_file)):
        if (search_file in files):
            wiki_path = os.path.join(root, search)
            # remove everything leading up to the project root to allow a proper path
            nested_path = wiki_path.replace(os.path.dirname(args.input_file), "")[1:]
            return(nested_path)

    return search


def update_file(filename):
    with open(filename) as f:
        content = f.read()
    proper = replace_redmine_wiki_with_textile_link(content)
    with open(filename, 'w') as f:
        f.write(proper)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()
    update_file(args.input_file)
