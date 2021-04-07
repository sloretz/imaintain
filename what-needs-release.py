#!/usr/bin/env python3

import argparse
import contextlib
import os
import pathlib
import subprocess
import yaml


@contextlib.contextmanager
def cd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)

DIR = pathlib.Path(__file__).parent.absolute()

DEFAULT_DISTROS = (
    'kinetic',
    'melodic',
    'noetic',
    'dashing',
    'foxy',
    'galactic',
    'rolling'
)


def find_source_repo(vcs_uri):
    # TODO(sloretz) get rid of assuption about where repos are located
    root_stack = [DIR / 'repos']
    while root_stack:
        root = root_stack.pop(0)
        files = os.listdir(str(root))
        if '.git' in files:
            source_uri = get_remote_uri(root)
            if same_github_repo(source_uri, vcs_uri):
                return root
        for f in files:
            abspath = os.path.join(root, f)
            if os.path.isdir(abspath):
                root_stack.insert(0, abspath)
    print('failed to find source repo?', vcs_uri)


def get_remote_uri(path):
    remote_uri = None
    # TODO(sloretz) remove assumption about remote being named origin
    with cd(path):
        output = subprocess.check_output(['git', 'remote', 'get-url', 'origin'])
    return output.decode('utf-8').strip()


class ReleaseRepo:

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self._release_info = {}

        with (self.path / 'tracks.yaml').open() as fin:
            release_data = yaml.safe_load(fin)

        for track in release_data['tracks'].values():
            info = LastReleaseInfo.from_track(track)
            self._release_info[info.ros_distro] = info

    def release_info(self, distro):
        if distro in self._release_info:
            return self._release_info[distro]


class LastReleaseInfo:
    __slots__ = ['ros_distro', 'vcs_uri', 'release_tag', 'devel_branch']

    @classmethod
    def from_track(cls, track):
        inst = cls()
        inst.ros_distro = track['ros_distro']
        inst.vcs_uri = track['vcs_uri']
        if ':{version}' == track['release_tag']:
            inst.release_tag = track['last_version']
        else:
            inst.release_tag = track['release_tag']
        inst.devel_branch = track['devel_branch']
        return inst

    def __repr__(self):
        return f'<LastReleaseInfo({self.ros_distro}, {self.vcs_uri}, {self.release_tag}, {self.devel_branch})>'


def same_github_repo(url1, url2):
    """Return True if URLs point to the same github repo."""
    if url1 == url2:
        return True

    def _get_suffix(url):
        if url.startswith('git@'):
            return url[len('git@github.com:'):]
        elif url.startswith('https://'):
            return url[len('https://github.com/'):]
        else:
            raise NotImplementedError(f'unknown vcs url format: {url}')

    return _get_suffix(url1) == _get_suffix(url2)


# What's the ideal output I'm going for?
"""
Kinetic
    kdl_parser 0 commits since 0.2.1
    rclpy 1 commit and 1 day 4 hours since 0.1.7
Melodic
    kdl_parser 24 commits and 1 year 6mo 2 days since 0.2.1
"""

def print_repo_status(repo_path, release_info):
    repo_name = pretty_repo_name(repo_path)
    num_commits = num_commits_between(repo_path, release_info.release_tag, release_info.devel_branch)
    time_since_str = time_since_tag(repo_path, release_info.release_tag)
    current_version = release_info.release_tag

    commits_str = f'{num_commits} commits'
    if num_commits == 1:
        commits_str = commits_str[:-1]
    since_str = ''
    if num_commits > 0:
        since_str = f' and {time_since_str.strip()} since {current_version.strip()}'
    print(f'  {repo_name} {commits_str}{since_str}')


def pretty_ros_distro(rosdistro):
    return f'ROS {rosdistro[0].upper()}{rosdistro.lower()[1:]}'


def pretty_repo_name(repo_path):
    repo_path = pathlib.Path(repo_path)
    components = []
    # TODO(sloretz) remove assumption about all repos being in a 'repos' folder
    while repo_path.name != 'repos' and repo_path != repo_path.parent:
        components.append(repo_path.name)
        repo_path = repo_path.parent
    components.reverse()
    return '/'.join(components)


def num_commits_between(repo_path, ver1, ver2):
    with cd(repo_path):
        # TODO(sloretz) get rid of assumption of remote name being 'origin'
        output = subprocess.check_output(
            ['git', 'rev-list', '--count', f'{ver1}..remotes/origin/{ver2}', '--'])
        return int(output)


def time_since_tag(repo_path, tag):
    with cd(repo_path):
        output = subprocess.check_output(
            ['git', 'show', '-s', '--format=%cr', tag])
        return output.decode('utf-8').strip()


def main():
    parser = argparse.ArgumentParser(description='Figure out if ROS repos need to be released')
    parser.add_argument(
        'ros_distros', metavar='DISTRO', type=str, nargs='*',
        help=f'ROS Distros to check for needed releases (default: {" ".join(DEFAULT_DISTROS)})',
        default=DEFAULT_DISTROS
        )
    args = parser.parse_args()

    release_repos = []
    # TODO(sloretz) get rid of assuption about where repos are located
    base_path = DIR / 'repos'
    for root, dirs, files in os.walk(str(base_path)):
        if 'tracks.yaml' in files:
            release_repos.append(ReleaseRepo(root))

    for distro in args.ros_distros:
        print(pretty_ros_distro(distro))
        for repo in release_repos:
            info = repo.release_info(distro)
            if info:
                print_repo_status(find_source_repo(info.vcs_uri), info)


if __name__ == '__main__':
    main()
