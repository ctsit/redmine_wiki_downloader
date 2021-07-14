#!/usr/bin/env python3

import re
import argparse

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
                            # ':' + match.expand(r"\1").replace(" ", "_") + ".md"
                            ':' + match.expand(r"\1").replace(" ", "_") + "/"
                            ),
                    string = page_content)
    return proper

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
