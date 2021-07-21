This utility downloads wiki pages from a Redmine instance via its [REST API](https://www.redmine.org/projects/redmine/wiki/rest_api). Wikis are downloaded into directories by project, with child directories for nested wikis; scripts are provided to allow the wiki to be managed by [MkDocs](https://www.mkdocs.org/).

# Requirements

* Python 3.6 or later

Optional
* [`pandoc`](https://pandoc.org/installing.html)
* `mkdocs`


This utility is expected to be used in a UNIX like environment. It was developed on MacOS.

# Setup

## Configuration

Copy the `example.env` file to `.env`

``` sh
cp example.env .env
```

Populate `.env` with the appropriate values for your Redmine instance, you will likely want to use credentials for an administrator account.

```
REDMINE_URL=https://example.com/
REDMINE_USER=admin
REDMINE_PASSWORD=password
```

# Use
Once your configuration is set, `download_redmine_wikis.py` may be used directly to download wikis for *all* projects from your Redmine instance, including attached files.

By default, this script will download all projects as siblings of the `download_redmine_wikis.py` script, you may specify an output directory with the optional `--output_dir` flag.

``` sh
python3 download_redmine_wikis.py --output_dir="./redmine_wikis/docs" | tee redmine_download.log
```

It is assumed that the wiki pages are created in the [Textile markup language](https://textile-lang.com/), with [Redmine's wiki specification](https://www.redmine.org/projects/redmine/wiki/RedmineTextFormattingTextile).

## Display with MkDocs

Scripts are provided to make the pages suitable for viewing in [MkDocs](https://www.mkdocs.org/), which requires markdown files.

`convert_all_wiki_pages_to_md.sh` will automatically convert all `.textile` files[^1] to `.md` files and **delete the original `.textile` file**. It is recommended to backup your download prior to running `convert_all_wiki_pages_to_md.sh`, e.g. `tar -zcf redmine_wikis.tgz redmine_wikis`.

Assuming you downloaded your wiki to `redmine_wikis/docs`, the following will create a new MkDocs environment:

``` sh
bash convert_all_wiki_pages_to_md.sh && mkdocs new redmine_wikis
```

Consult the [MkDocs introductory guide](https://www.mkdocs.org/getting-started/) for more information.

[^1]: Redmine's wiki specification differs from default textile format, `convert_wiki_to_md.py` is used by `convert_all_wiki_pages_to_md.sh` to attempt to align the wiki pages with the textile format expected by `pandoc`.
