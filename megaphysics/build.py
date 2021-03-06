# The build code for the site.

# -------- Standard Libraries -------- #

import os
import re
import subprocess


# -------- Third Party Libraries -------- #

import markdown


# -------- Project Libraries -------- #

import megaphysics.views
from megaphysics.urls import generate_links
from megaphysics.minify import compress_assets


# -------- Globals -------- #

BUILD_DIR = os.getcwd()
STYLES_LOCATION = 'assets/site_assets'
JQUERY_PATH = 'assets/jquery/jquery-1.11.1.min.js'


# -------- Functions -------- #

def files():

    """Returns a list of articles."""

    return os.listdir("./articles")


def metadata(filename):

    """Extract the metadata block at the top of each article and parse it into a
    dictionary.
    """

    with open("./articles/" + filename) as f:
        contents = f.read()

    md = markdown.Markdown(extensions=['meta'])
    md.convert(contents)
    meta = md.Meta
    meta["course"] = meta["course"][0]
    meta["title"] = meta["title"][0]
    meta["author"] = meta["author"][0]

    return meta


def generate_base_site(articles_metadata):

    """Builds the core site pages (index, about etc.)."""

    megaphysics.views.index()
    megaphysics.views.about()
    megaphysics.views.article_list(articles_metadata)
    megaphysics.views.course_list(articles_metadata)


def run():

    """Runs the build."""

    # Check if we're in the root dir.
    if re.search("MegaPhysics$", os.getcwd()) is None:
        raise Exception(
            "This script must be run from the root MegaPhysics directory")

    # Empty and recreate the build dir.
    if os.path.isdir("build"):
        subprocess.call(['rm', '-r', 'build'])
    subprocess.call(['mkdir', 'build'])
    subprocess.call(['mkdir', 'build/assets'])

    # Copy articles to temp location for processing.
    subprocess.call(['cp', '-r', 'articles', 'temp'])

    # This dictionary will store all metadata for the articles.
    articles_metadata = {}

    # Get metadata for all the articles,
    # TODO: check that all metadata is valid at this point.
    for f in files():
        if f[0] == ".":
            continue
        name = re.match("(.+)\.", f).group(1)
        articles_metadata[name] = metadata(f)

    try:

        generate_links(articles_metadata)

        # Builds each individual article page.
        for f in files():
            if f[0] == ".":
                break
            megaphysics.views.generate_article(f, articles_metadata, BUILD_DIR)

        # Builds the core site pages (index, about etc.).
        generate_base_site(articles_metadata)

        # Copies in the assets folders.
        subprocess.call([
            'cp',
            '-r',
            'assets/article_assets',
            'build/assets/article_assets'])
        subprocess.call(['mkdir', 'build/assets/bootstrap'])
        subprocess.call([
            'cp',
            '-r',
            'assets/site_assets/bootstrap/fonts',
            'build/assets/bootstrap/fonts'])

        # Creates CSS and js files.
        compress_assets(JQUERY_PATH, STYLES_LOCATION)

    finally:
        # Clean up after ourselves
        subprocess.call(['rm', '-r', 'temp'])
