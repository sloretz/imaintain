#!/usr/bin/env python3

import datetime
import keyring
import requests


def get_api_key():
    key = keyring.get_password("github-api-token", "may-read-all")
    if key is None:
        raise RuntimeError('Failed to get github api key')
    return key


REPO_QUERY_FRAG = """
  r{n}:repository(owner:"{owner}", name:"{name}") {{
    pullRequests({pagenation_prs} states:OPEN) {{
      ...pr_info
    }}
    issues({pagenation_issues} states:OPEN) {{
      ...issue_info
    }}
  }}
"""

PAGENATION_START = 'last: {last}'
PAGENATION_CONT = 'last: {last}, before: "{before}"'

INFO_FRAG = """
fragment pr_info on PullRequestConnection {
  nodes {
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
    repository {
      owner {
          login
      }
      name
    }
  }
  pageInfo {
      hasPreviousPage
      startCursor
  }
}

fragment issue_info on IssueConnection {
  nodes {
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
    repository {
      owner {
          login
      }
      name
    }
  }
  pageInfo {
      hasPreviousPage
      startCursor
  }
}
"""

GRAPHQL_QUERY = """
query {{
  {repo_fragments}
  {INFO_FRAG}
}}
"""


def make_query(repos):
    repo_queries = []
    n = 0
    for owner, name in repos:
        n += 1
        repo_queries.append(REPO_QUERY_FRAG.format(n=n, owner=owner, name=name))

    return GRAPHQL_QUERY.format(
        repo_fragments='\n'.join(repo_queries),
        INFO_FRAG=INFO_FRAG)


def linkify(text, url):
    return '\x1B]8;;{url}\x1B\\{text}\x1B]8;;\x1B\\'.format(url=url, text=text)


def dateify(date_str):
    return datetime.datetime.strptime('2020-10-22T16:02:39Z', '%Y-%m-%dT%H:%M:%SZ')


query = make_query((
    ['colcon', 'colcon-output'],
    ['colcon', 'colcon-ros'],
    ['colcon', 'colcon-spawn-shell'],
    ['colcon', 'colcon-zsh'],
    ['osrf', 'car_demo'],
    ['osrf', 'py3-ready'],
    ['ros', 'collada_urdf'],
    ['ros', 'eigen_stl_containers'],
    ['ros', 'genpy'],
    ['ros', 'kdl_parser'],
    ['ros', 'robot_state_publisher'],
    ['ros', 'ros_comm'],
    ['ros', 'ros_tutorials'],
    ['ros', 'urdf_parser_py'],
    ['ros', 'urdfdom'],
    ['ros-visualization', 'python_qt_binding'],
    ['ros-visualization', 'qt_gui_core'],
    ['ros2', 'darknet_vendor'],
    ['ros2', 'detection_visualizer'],
    ['ros2', 'eigen3_cmake_module'],
    ['ros2', 'examples'],
    ['ros2', 'openrobotics_darknet_ros'],
    ['ros2', 'pybind11_vendor'],
    ['ros2', 'python_cmake_module'],
    ['ros2', 'rclpy'],
    ['ros2', 'ros1_bridge'],
    ['ros2', 'rosidl'],
    ['ros2', 'rosidl_dds'],
    ['ros2', 'rosidl_defaults'],
    ['ros2', 'rosidl_python'],
    ['ros2', 'rosidl_typesupport'],
    ['ros2', 'slide_show'],
    ['ros2', 'urdf'],
    ['ros2', 'urdfdom']))


response = requests.post(
    'https://api.github.com/graphql',
    json={'query': query},
    headers={'Authorization': 'Bearer ' + get_api_key()})

if response.status_code != 200:
    raise response

data = response.json()

json_things = []
for _, repo_data in data['data'].items():
    for issue in repo_data['issues']['nodes']:
        json_things.append(issue)
    for pr in repo_data['pullRequests']['nodes']:
        json_things.append(pr)

# TODO(sloretz) Sort by updated date
# for thing in json_things:
#     if thing['updatedAt'] is None:
#         thing['updatedAt'] = thing['publishedAt']
# 
table_things = []

for thing in sorted(json_things, key=lambda t: t['updatedAt']):
    repo = thing['repository']['owner']['login'] + '/' + thing['repository']['name']
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
