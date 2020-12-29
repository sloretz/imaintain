#!/usr/bin/env python3

import datetime
import keyring
import requests


def get_api_key():
    key = keyring.get_password("github-api-token", "may-read-all")
    if key is None:
        raise RuntimeError('Failed to get github api key')
    return key


GRAPHQL_QUERY = """
query {
  r2:repository(owner:"colcon", name:"colcon-output") {
    ...pr_and_issue_info
  }
  r3:repository(owner:"colcon", name:"colcon-ros") {
    ...pr_and_issue_info
  }
  r4:repository(owner:"colcon", name:"colcon-spawn-shell") {
    ...pr_and_issue_info
  }
  r5:repository(owner:"colcon", name:"colcon-zsh") {
    ...pr_and_issue_info
  }
  r6:repository(owner:"osrf", name:"car_demo") {
    ...pr_and_issue_info
  }
  r7:repository(owner:"osrf", name:"py3-ready") {
    ...pr_and_issue_info
  }
  r8:repository(owner:"ros", name:"collada_urdf") {
    ...pr_and_issue_info
  }
  r9:repository(owner:"ros", name:"eigen_stl_containers") {
    ...pr_and_issue_info
  }
  r10:repository(owner:"ros", name:"genpy") {
    ...pr_and_issue_info
  }
  r11:repository(owner:"ros", name:"kdl_parser") {
    ...pr_and_issue_info
  }
  r12:repository(owner:"ros", name:"robot_state_publisher") {
    ...pr_and_issue_info
  }
  r13:repository(owner:"ros", name:"ros_comm") {
    ...pr_and_issue_info
  }
  r14:repository(owner:"ros", name:"ros_tutorials") {
    ...pr_and_issue_info
  }
  r15:repository(owner:"ros", name:"urdf_parser_py") {
    ...pr_and_issue_info
  }
  r16:repository(owner:"ros", name:"urdfdom") {
    ...pr_and_issue_info
  }
  r17:repository(owner:"ros-visualization", name:"python_qt_binding") {
    ...pr_and_issue_info
  }
  r18:repository(owner:"ros-visualization", name:"qt_gui_core") {
    ...pr_and_issue_info
  }
  r19:repository(owner:"ros2", name:"darknet_vendor") {
    ...pr_and_issue_info
  }
  r20:repository(owner:"ros2", name:"detection_visualizer") {
    ...pr_and_issue_info
  }
  r21:repository(owner:"ros2", name:"eigen3_cmake_module") {
    ...pr_and_issue_info
  }
  r22:repository(owner:"ros2", name:"examples") {
    ...pr_and_issue_info
  }
  r23:repository(owner:"ros2", name:"openrobotics_darknet_ros") {
    ...pr_and_issue_info
  }
  r24:repository(owner:"ros2", name:"pybind11_vendor") {
    ...pr_and_issue_info
  }
  r25:repository(owner:"ros2", name:"python_cmake_module") {
    ...pr_and_issue_info
  }
  r26:repository(owner:"ros2", name:"rclpy") {
    ...pr_and_issue_info
  }
  r27:repository(owner:"ros2", name:"ros1_bridge") {
    ...pr_and_issue_info
  }
  r28:repository(owner:"ros2", name:"rosidl") {
    ...pr_and_issue_info
  }
  r29:repository(owner:"ros2", name:"rosidl_dds") {
    ...pr_and_issue_info
  }
  r30:repository(owner:"ros2", name:"rosidl_defaults") {
    ...pr_and_issue_info
  }
  r31:repository(owner:"ros2", name:"rosidl_python") {
    ...pr_and_issue_info
  }
  r32:repository(owner:"ros2", name:"rosidl_typesupport") {
    ...pr_and_issue_info
  }
  r33:repository(owner:"ros2", name:"slide_show") {
    ...pr_and_issue_info
  }
  r34:repository(owner:"ros2", name:"urdf") {
    ...pr_and_issue_info
  }
  r35:repository(owner:"ros2", name:"urdfdom") {
    ...pr_and_issue_info
  }
}

fragment pr_and_issue_info on Repository {
  pullRequests(last: 100, states:OPEN) {
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
  }
  issues(last: 100, states:OPEN) {
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
  }
}
"""


def linkify(text, url):
    return '\x1B]8;;{url}\x1B\\{text}\x1B]8;;\x1B\\'.format(url=url, text=text)


def dateify(date_str):
    return datetime.datetime.strptime('2020-10-22T16:02:39Z', '%Y-%m-%dT%H:%M:%SZ')


response = requests.post(
    'https://api.github.com/graphql',
    json={'query': GRAPHQL_QUERY},
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
