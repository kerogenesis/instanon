import os
import re
import shutil

from datetime import datetime
from html import unescape
from sys import exit
from urllib.parse import urlparse

import click
import requests
import urllib3

from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning


class Directories:
    """Contains path information and directory creation function.

    Arg:
        username (str): Instagram username

    Optional args:
        output_flag (str): Custom output path
        chaos_flag (bool): Chaos option (all stories in one directory)

    Methods:
        create() -> Creates the specified directories
        rm_empty_stories_dirs() -> Removes empty dirs from the story dir
    """

    def __init__(self, username, output_flag=False, chaos_flag=False):
        """
        Params:
            username (str): Instagram username
            root_path (str): Root directory path with usernames
            highlights_path (str): Highlights directory path
            stories_path (str): Stories directory path
        """

        self.username = username

        # If custom output path is passed
        # set root_path with this directory
        if output_flag:
            self.root_path = r'{}'.format(output_flag)
        else:
            self.root_path = 'users'

        self.user_path = os.path.join(self.root_path, self.username)
        self.highlights_path = os.path.join(self.user_path, 'highlights')

        # If chaos_flag is not passed
        # add a directory with today's date
        if chaos_flag:
            self.stories_path = os.path.join(self.user_path, 'stories')
        else:
            self.stories_path = os.path.join(self.user_path, 'stories',
                                             datetime.now().strftime("%d-%B-%Y"))

    def create(self, stories_flag=False, highlights_flag=False):
        """Creates the necessary directories.

        Optional args:
            stories_flag (bool): Create stories directory
            highlights_flag (bool): Create highlights directory
        """

        def create_dir(dir_path):
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)

        # Create main directories
        create_dir(self.root_path)
        create_dir(self.user_path)

        # Create optional directories
        if stories_flag:
            create_dir(self.stories_path)
        if highlights_flag:
            create_dir(self.highlights_path)

    def rm_empty_stories_dirs(self):
        """Removes empty dirs from the story dir"""

        try:
            if not os.listdir(os.path.abspath(self.stories_path)):
                shutil.rmtree(os.path.abspath(self.stories_path))
        except FileNotFoundError:
            pass


class Content(Directories):
    """Collects user data.

    Arg:
        username (str): Instagram username
    Optional args:
        output_flag (str): Сustom output path
        chaos_flag (bool): Сhaos option (all stories in one directory)
    Methods:
        exists() -> Checks the user's profile
        get_stories() -> Get user stories
        download_stories() -> Download user stories
        get_highlights() -> Get user highlights
        download_highlights() -> Download user highlights
        validate() -> Check the passed file name in user_path
    """

    def __init__(self, username, output_flag=False, chaos_flag=False):
        """
        Params:
            username (str): Instagram username
            api (str): Main site for parsing
            stories_link (str): Link to user stories
            user_link (str): Link to user content page
            root_page (str): HTML page with user content

            Inherited paths from the Directories class
        """

        self.username = username
        self.api = 'https://insta-stories.com/en'
        self.user_link = self.api + '/stories/' + self.username
        self.root_page = requests.get(self.user_link, verify=False).text
        super().__init__(username, output_flag=output_flag, chaos_flag=chaos_flag)

    def exists(self):
        """Checks the user's profile.

        Return
            True: If the user exists and their profile is open
            False: If not
        """

        if "This username doesn't exist. Please try with another one." in self.root_page:
            instagram_page = f"https://www.instagram.com/{self.username}"
            if requests.get(instagram_page).status_code == 404:
                click.secho(f"[!] User '{self.username}' does not exist", fg='red')
            else:
                click.secho(f"[!] Server error. Please try again later", fg='red')
            return False
        elif "This user has a private account. Please try with another one." in self.root_page:
            click.secho(f"[!] Account '{self.username}' is private", fg='yellow')
            return False
        else:
            return True

    def get_stories(self):
        """Gets user stories.

        Return
            stories (list): Stories links
        """

        if 'No stories available. Please try again later.' in self.root_page:
            click.secho(f"\n[!] Whoops! {self.username} did not post "
                        "any recent stories", fg='yellow')
            return False
        else:
            print(f"\n[*] Getting {self.username} stories")
            stories = self.parsing_content(self.root_page)
            return stories

    def download_stories(self, stories_pool):
        """Downloads user stories.

        Arg
            stories_pool (list): Stories links
        """

        try:
            fill_char = click.style('=', fg='green')
            with click.progressbar(stories_pool,
                                   label='[*] Downloading stories',
                                   fill_char=fill_char) as bar:

                # For every link in stories_pool
                for link in bar:
                    r = requests.get(link, verify=False)
                    parser = urlparse(link)
                    filename = os.path.basename(parser.path.split('/')[-1])

                    # Validate and download stories
                    if self.validate(filename, self.stories_path):
                        with open(os.path.join(self.stories_path, filename), 'wb') as f:
                            f.write(r.content)
                    else:
                        continue
        except KeyboardInterrupt:
            exit()

    def get_highlights(self):
        """Gets user highlights.

        Return
            highlights_dictionary (dict): {link: dirname} of each highlights group
        """

        highlights_array = []  # Absolute links to every highlights group
        highlights_id_array = []
        highlights_names_array = []
        highlights_dir_names = []

        # Parsing URLs
        soup = BeautifulSoup(self.root_page, features="lxml")
        highlight_divs = soup.findAll('div', {'class': re.compile("^highlight ")})
        if highlight_divs:
            print(f"\n[*] Getting {self.username} highlights")

            # Get links to every highlights group
            highlight_links = []
            for div in highlight_divs:
                dirty_link = div.find('a').get('href')
                split_dirty_link = dirty_link.split('/')
                clear_link = '/' + '/'.join(split_dirty_link[2:])
                highlight_links.append(clear_link)

            # Get highlights id and absolute urls
            for url in highlight_links:
                parser = urlparse(url)
                highlight_id = os.path.basename(parser.path)
                highlights_id_array.append(highlight_id)
                highlights_array.append(self.api + url)

            # Get highlights names
            highlight_names = soup.findAll('div', {'class': 'highlight-description'})
            for name in highlight_names:
                highlights_names_array.append(name.text.strip())

            # Get highlights directory names
            for i, j in zip(highlights_names_array, highlights_id_array):
                highlights_dir_names.append(i + '_' + j)

            # Get {link: dirname} of each highlights group
            highlights_dictionary = dict(zip(highlights_array, highlights_dir_names))
            return highlights_dictionary
        else:
            click.secho(f"\n[!] Whoops! {self.username} does not appear "
                        "to have any highlights", fg='yellow')
            return False

    def download_highlights(self, group, name, start, end):
        """Downloads user stories.

        Args
            group (str): Link to every highlights group
            name (str): Highlights directory name
            start (int): Start counter highlights groups
            end (int): End counter highlights groups
        """

        # Get highlights group page
        html = requests.get(group, verify=False).text

        # Create a directory
        highlight_dir = os.path.join(self.highlights_path, name)
        if not os.path.isdir(highlight_dir):
            os.makedirs(highlight_dir)

        # Parsing all highlights of the group
        highlights_links = self.parsing_content(html)

        try:  # Download every highlight
            bar_label = f'[*] Downloading highlight {start} of {end}'
            fill_char = click.style('=', fg='green')
            with click.progressbar(highlights_links,
                                   label=bar_label,
                                   fill_char=fill_char) as bar:
                for url in bar:
                    r = requests.get(url, verify=False)
                    parser = urlparse(url)
                    filename = os.path.basename(parser.path.split('/')[-1])
                    if self.validate(filename, self.highlights_path):
                        with open(os.path.join(highlight_dir, filename), 'wb') as f:
                            f.write(r.content)
                    else:
                        continue
        except KeyboardInterrupt:
            exit()

    @staticmethod
    def parsing_content(page):
        content_links = []
        soup = BeautifulSoup(page, features="lxml")
        content_divs = soup.findAll('div', {'class': 'download-story-container'})
        for div in content_divs:
            download_link = div.find('a', {'class': 'download-story'})
            onclick = str(download_link.get('onclick'))
            url_pattern = r"(https://scontent\S+)(.*?)'"
            element_url = re.search(url_pattern, onclick, re.MULTILINE)
            try:
                content_links.append(unescape(element_url.group(1)))
            except AttributeError:
                continue
        return content_links

    @staticmethod
    def validate(user_file, user_path):
        """Check the passed file name in directory.

        Arg
            user_file (str): file name
            user_path (str): directory
        Return
            True or False
        """

        # Gets all file names in the user_path
        user_data = []
        for root, directories, files in os.walk(user_path):
            for filename in files:
                if not filename.startswith('.'):
                    user_data.append(filename)

        if user_file in user_data:
            return False
        else:
            return True


@click.command()
@click.option('--users', '-u', type=str, multiple=True, required=True, help='Instagram username(s)')
@click.option('--stories', '-s', type=str, is_flag=True, help='Download stories')
@click.option('--highlights', '-h', type=str, is_flag=True, help='Download highlights')
@click.option('--output', '-o', type=click.Path(), help='Directory for data storage')
@click.option('--chaos', '-c', type=str, is_flag=True, help='Save stories in one directory')
def main(users, stories, highlights, output, chaos):
    """Download Instagram stories or highlights anonymously"""

    # disable certificate error
    urllib3.disable_warnings(InsecureRequestWarning)

    for user in users:
        user_content = Content(user, output, chaos)
        if user_content.exists():
            dirs = Directories(user, output, chaos)

            if stories:
                stories_pool = user_content.get_stories()
                if stories_pool:
                    dirs.create(stories_flag=True)
                    user_content.download_stories(stories_pool)
                    dirs.rm_empty_stories_dirs()
                else:
                    pass

            if highlights:
                highlights_pool = user_content.get_highlights()
                if highlights_pool:
                    dirs.create(highlights_flag=True)
                    # init highlights group counter
                    start, end = 1, len(highlights_pool)
                    for group, name in highlights_pool.items():
                        user_content.download_highlights(group, name, start, end)
                        start += 1
                else:
                    pass

    click.secho(f'\n[*] All tasks have been completed\n', fg='green')


if __name__ == "__main__":
    main()
