#!/usr/bin/env python3

import datetime
import keyring
import requests


def get_api_key():
    key = keyring.get_password("github-api-token", "may-read-all")
    if key is None:
        raise RuntimeError('Failed to get github api key')
    return key



class GithubQuery:
    REPO_QUERY = """
r{n}:repository(owner:"{owner}", name:"{name}") {{
  {info}
  owner {{
      login
  }}
  name
}}"""

    PR_QUERY = """
pullRequests({pagination}, states:OPEN) {{
  ...pr_info
}}"""

    ISSUE_QUERY = """
issues({pagination}, states:OPEN) {{
  ...issue_info
}}"""

    pagination_START = 'first: 100'

    pagination_CONT = 'first: 100, after: "{after}"'

    PR_INFO_FRAG = """
fragment pr_info on PullRequestConnection {
  edges {
    cursor
    node {
        number
        publishedAt
        isDraft
        title
        updatedAt
        url
        comments {
          totalCount
        }
        author {
          login
        }
    }
  }
  pageInfo {
      hasNextPage
  }
}"""

    ISSUE_INFO_FRAG = """
fragment issue_info on IssueConnection {
  edges {
    cursor
    node {
        number
        publishedAt
        updatedAt
        title
        url
        comments {
          totalCount
        }
        author {
          login
        }
    }
  }
  pageInfo {
      hasNextPage
  }
}"""

    GRAPHQL_QUERY = """
query {{
  {repo_fragments}
}}
{INFO_FRAG}"""

    def __init__(self, repos):
        self._repos = [(owner, name) for owner, name in repos]

    def next_query(self, last_results=None):
        pagination_issues = {}
        pagination_prs = {}
        for repo in self._repos:
            if last_results is None:
                pagination_issues[repo] = self.pagination_START
                pagination_prs[repo] = self.pagination_START
            else:
                for _, repo_info in last_results['data'].items():
                    if repo != (repo_info['owner']['login'], repo_info['name']):
                        # not the data for this repo, keep looking
                        continue
                    if 'issues' in repo_info and repo_info['issues']['pageInfo']['hasNextPage']:
                        pagination_issues[repo] = self.pagination_CONT.format(
                            after=repo_info['issues']['edges'][-1]['cursor'])
                    if 'pullRequests' in repo_info and repo_info['pullRequests']['pageInfo']['hasNextPage']:
                        pagination_prs[repo] = self.pagination_CONT.format(
                            after=repo_info['pullRequests']['edges'][-1]['cursor'])

        info_frags = []
        repo_queries = []
        n = 0
        for repo in self._repos:
            owner, name = repo
            queries = []
            if repo in pagination_issues:
                queries.append(self.ISSUE_QUERY.format(pagination=pagination_issues[repo]))
                if self.ISSUE_INFO_FRAG not in info_frags:
                    info_frags.append(self.ISSUE_INFO_FRAG)
            if repo in pagination_prs:
                queries.append(self.PR_QUERY.format(pagination=pagination_prs[repo]))
                if self.PR_INFO_FRAG not in info_frags:
                    info_frags.append(self.PR_INFO_FRAG)
            if queries:
                n += 1
                repo_queries.append(self.REPO_QUERY.format(
                    n=n, owner=owner, name=name, info='\n'.join(queries)))

        if repo_queries:
            return self.GRAPHQL_QUERY.format(
                repo_fragments='\n'.join(repo_queries),
                INFO_FRAG='\n'.join(info_frags))


def linkify(text, url):
    return '\x1B]8;;{url}\x1B\\{text}\x1B]8;;\x1B\\'.format(url=url, text=text)


def dateify(date_str):
    return datetime.datetime.strptime('2020-10-22T16:02:39Z', '%Y-%m-%dT%H:%M:%SZ')

repos = (
    ('colcon', 'colcon-spawn-shell'),
    ('osrf', 'car_demo'),
    ('osrf', 'py3-ready'),
    ('ros', 'collada_urdf'),
    ('ros', 'eigen_stl_containers'),
    ('ros', 'kdl_parser'),
    ('ros', 'robot_state_publisher'),
    ('ros', 'ros'),
    ('ros', 'sdformat_urdf'),
    ('ros', 'urdf'),
    ('ros', 'urdf_parser_py'),
    ('ros', 'urdfdom'),
    ('ros-gbp', 'collada_urdf-release'),
    ('ros-gbp', 'eigen_stl_containers-release'),
    ('ros-gbp', 'kdl_parser-release'),
    ('ros-gbp', 'python_qt_binding-release'),
    ('ros-gbp', 'robot_state_publisher-release'),
    ('ros-gbp', 'ros-release'),
    ('ros-gbp', 'urdf-release'),
    ('ros-gbp', 'urdfdom-release'),
    ('ros-gbp', 'urdfdom_py-release'),
    ('ros-visualization', 'python_qt_binding'),
    ('ros2', 'darknet_vendor'),
    ('ros2', 'detection_visualizer'),
    ('ros2', 'eigen3_cmake_module'),
    ('ros2', 'examples'),
    ('ros2', 'openrobotics_darknet_ros'),
    ('ros2', 'pybind11_vendor'),
    ('ros2', 'python_cmake_module'),
    ('ros2', 'rclpy'),
    ('ros2', 'ros1_bridge'),
    ('ros2', 'rosidl'),
    ('ros2', 'rosidl_dds'),
    ('ros2', 'rosidl_defaults'),
    ('ros2', 'rosidl_python'),
    ('ros2', 'rosidl_runtime_py'),
    ('ros2', 'rosidl_typesupport'),
    ('ros2', 'rosidl_typesupport_fastrtps'),
    ('ros2', 'slide_show'),
    ('ros2', 'system_tests'),
    ('ros2', 'urdf'),
    ('ros2-gbp', 'eigen3_cmake_module-release'),
    ('ros2-gbp', 'eigen_stl_containers-release'),
    ('ros2-gbp', 'examples-release'),
    ('ros2-gbp', 'kdl_parser-release'),
    ('ros2-gbp', 'pybind11_vendor-release'),
    ('ros2-gbp', 'python_cmake_module-release'),
    ('ros2-gbp', 'python_qt_binding-release'),
    ('ros2-gbp', 'rclpy-release'),
    ('ros2-gbp', 'robot_state_publisher-release'),
    ('ros2-gbp', 'ros1_bridge-release'),
    ('ros2-gbp', 'rosidl-release'),
    ('ros2-gbp', 'rosidl_dds-release'),
    ('ros2-gbp', 'rosidl_defaults-release'),
    ('ros2-gbp', 'rosidl_python-release'),
    ('ros2-gbp', 'rosidl_runtime_py-release'),
    ('ros2-gbp', 'rosidl_typesupport-release'),
    ('ros2-gbp', 'rosidl_typesupport_fastrtps-release'),
    ('ros2-gbp', 'sdformat_urdf-release'),
    ('ros2-gbp', 'slide_show-release'),
    ('ros2-gbp', 'urdf-release'),
    ('ros2-gbp', 'urdfdom-release'),
    ('ros2-gbp', 'urdfdom_py-release'),
)

query = GithubQuery(repos)
next_query = query.next_query()
json_things = []


while next_query:
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': next_query},
        headers={'Authorization': 'Bearer ' + get_api_key()})

    if response.status_code != 200:
        raise response

    data = response.json()

    for _, repo_data in data['data'].items():
        repo_name = f'{repo_data["owner"]["login"]}/{repo_data["name"]}'
        if 'issues' in repo_data:
            for issue in repo_data['issues']['edges']:
                issue['node']['repo'] = repo_name
                json_things.append(issue['node'])
        if 'pullRequests' in repo_data:
            for pr in repo_data['pullRequests']['edges']:
                pr['node']['repo'] = repo_name
                json_things.append(pr['node'])

    next_query = query.next_query(data)

table_things = []

for thing in sorted(json_things, key=lambda t: t['updatedAt']):
    repo = thing['repo']
    repo = linkify(repo, 'https://github.com/' + repo)

    title = thing['title']

    if 'isDraft' in thing:
        if thing['isDraft']:
            title = '[DRAFT]' + title
        type_ = 'PR'
    else:
        type_ = 'I'

    number = "#" + str(thing['number'])
    number = linkify(number, thing['url'])

    author = thing['author']
    if author is not None:
        author = author['login']
    else:
        author = 'ghost'

    if len(title) > 79:
        title = title[:79 -3] + '...'
    title = linkify(title, thing['url'])

    table_things.append((repo, type_, number, title, author))

from tabulate import tabulate
print(tabulate(table_things))
print(f'total: {len(table_things)}')
