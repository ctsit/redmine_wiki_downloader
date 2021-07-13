#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import requests
import json
import csv
import re
import subprocess

# Set globals
load_dotenv(".env")
base_dir = os.getcwd()
url = os.getenv("REDMINE_URL")
user, password = os.getenv("REDMINE_USER"), os.getenv("REDMINE_PASSWORD")

def get_data_from_endpoint(target_url):
    response = requests.get(target_url, auth=(user, password))
    try:
        response_object = json.loads(response.content)
    except json.decoder.JSONDecodeError:
        print(f"There was an issue with: {target_url}")
        response_object = {'wiki_page': ''}
    return response_object


# limited to 25 projects
def gather_projects():
    target_url = url + "projects.json"
    return get_data_from_endpoint(target_url)


def gather_wikis_from_project(identifier):
    target_url = url + "projects/" + identifier + "/wiki/index.json"
    return get_data_from_endpoint(target_url)['wiki_pages']


def get_wiki_page_and_attachments(identifier, wiki_title):
    target_url = url + "projects/" + identifier + "/wiki/" + wiki_title + ".json?include=attachments"
    return get_data_from_endpoint(target_url)['wiki_page']


def download_attachment(attachment_obj):
    target_url = attachment_obj['content_url']
    filename = attachment_obj['filename']
    # response is a binary object of the file contents
    response = requests.get(target_url, auth = (user, password))
    # https://docs.python-requests.org/en/master/user/quickstart/#raw-response-content
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size = 128):
            f.write(chunk)
    # Metadata for files is kept in the wiki metadata


def replace_redmine_wiki_with_textile_link(page_content):
    proper = re.sub(pattern = r'\[\[(.*)\]\]', # capture text within [[]] tags
                    # must use a lambda to allow replacing within a group
                    # https://stackoverflow.com/a/56393435/7418735
                    repl = (lambda match :
                            # link text
                            '"' + match.expand(r"\1") + '"' +
                            # link path
                            ':' + match.expand(r"\1").replace(" ", "_") + ".md"
                            ),
                    string = page_content)
    return proper


def download_wiki_page(wiki_obj):
    wiki_title = wiki_obj['title']
    print(f"Downloading {wiki_title}")
    page_content = replace_redmine_wiki_with_textile_link(wiki_obj.pop('text'))
    attachments = wiki_obj['attachments']
    if attachments:
        page_content += "\n" + "Attachments:"
        for attachment in attachments:
            download_attachment(attachment)
            # append a Textile style link to the page
            filename = attachment['filename']
            attachment_link = f"\"{filename}\":{filename}"
            page_content += "\n" + attachment_link
    with open(wiki_title + ".textile", 'w') as f:
        f.write(page_content)
    # FIXME: convert textile to md now instead of needing a bash script
    # subprocess.run(["pandoc", f"{wiki_title}.textile -o {wiki_title}.md"])
    # subprocess.call(["rm", f"{wiki_title}.textile"])
    with open(wiki_title + "-metadata.json", 'w') as f:
        f.write(json.dumps(wiki_obj))


def download_project(identifier):
    project_wikis = gather_wikis_from_project(identifier)
    project_dir = base_dir + "/" + identifier + "/"
    try:
        os.mkdir(project_dir)
    except FileExistsError:
        # dir exists already, just switch to it
        pass
    os.chdir(project_dir)
    project_map = {}
    # create a mapping to hierchically store in parent's dir
    for wiki in project_wikis:
        title = wiki['title']
        project_map.update({title: ''})
        if 'parent' in wiki:
            project_map[title] = wiki['parent']['title']

    for wiki in project_wikis:
        title = wiki['title']
        parent_title = title
        wiki_path = ""
        # prepend parents in file path to enforce nested hierarchy
        while project_map[parent_title] != '':
            parent_title = project_map[parent_title]
            wiki_path = parent_title + "/" + wiki_path

        wiki_path = project_dir + "/" + wiki_path
        wiki_obj = get_wiki_page_and_attachments(identifier, title)
        try:
            os.mkdir(wiki_path)
        except FileExistsError:
            # dir exists already, just switch to it
            pass
        os.chdir(wiki_path)
        if wiki_obj:
            download_wiki_page(wiki_obj)
    os.chdir(base_dir)
