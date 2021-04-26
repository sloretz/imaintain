******************************
Branching for a new ROS distro
******************************

When you want to make breaking changes on the latest development branch, but you don't want users of an older ROS distro to be affected, you need to create a new branch for the older ROS distro.
Both `ros/rosdistro <https://github.com/ros/rosdistro>`_ and the release repository need to be updated.
This page will walk you through the process.

.. contents:: Table of Contents

Decisions to Make
=================

What ROS distros will be released from the new branch?
------------------------------------------------------

**Recommendation: Have a branch for every ROS distro, except ROS Rolling.**

ROS Rolling should have its own branch too, but that should be the default branch (``master`` or ``main`` or ``ros2``) on your repository.
Having a branch for every other ROS distro makes it easy to accept breaking changes on your default branch (where they can be released into ROS Rolling), while allowing you to backport non-breaking changes to older ROS distros.

.. note:: Some repositories release into multiple ROS distros including ROS Rolling from the same branch. The advantage of this style is it requires fewer PRs to backport a single change to multiple older ROS distros, but the disadvantage is it requires more work to merge breaking changes. If you encounter a repository where the default branch is a really old ROS distro name like ``crystal-devel`` then consider updating it to the above recommendation.

What should the new branch be called?
-------------------------------------

**Recommendation: Use the lowercase ROS distro codename.**

Are you creating a branch for ROS Galactic? Call the branch ``galactic``.

.. note:: Some repositories use the lowercase ROS distro codename with the suffix ``-devel``. If you already have branches ending in ``-devel`` then be consistent.
  Are you creating a branch for ROS Galactic and are all of the other branches ending in ``-devel``? Call the new branch ``galactic-devel``.

Branching the source repository
===============================

**Goal: Make a branch like this one:** `ros/kdl_parser galactic <https://github.com/ros/kdl_parser/tree/galactic>`_

1. Clone the source repository if you haven't already

.. code-block:: console

  git clone git@github.com:<organization>/<repository>.git

2. Checkout the branch you want to base the new one off of

.. code-block:: console

  git checkout master

3. Pull to make sure the branch is up to date

.. code-block:: console

  git pull

4. Create the new branch

.. code-block:: console

  git checkout -b galactic

5. Push the new branch to your source repository

.. code-block:: console

  git push --set-upstream origin galactic

Updating the release repository
===============================

**Goal: Make a commit like this one:** `ros2-gbp/kdl_parser@09ab794 <https://github.com/ros2-gbp/kdl_parser-release/commit/09ab79474a217834258fcf5a618ba453c73178f9>`_

1. Clone the release repository if you haven't already and checkout the ``master`` branch

.. code-block:: console

  git clone git@github.com:<release organization>/<release repository>.git
  git checkout master

.. note:: Not sure what the release repository is? A typical release repository URL is ``https://github.com/ros2-gbp/rosbag2-release.git``. If your repo has been released before, replace ``<rosdistro>`` in this url ``https://github.com/ros/rosdistro/blob/master/<rosdistro>/distribution.yaml`` with the lower case ROS distro name it has been released into (ex: ``galactic``, or ``rolling``) and look for the ``url`` under ``release:`` for your repository.

2. Find the relevant ROS distros in ``tracks.yaml``. The "track" name is almost always the same as the lower case ROS distro name.
3. In ``tracks.yaml`` Change ``devel_branch`` to the new branch you created in your source repository
4. Commit the changes to ``tracks.yaml`` with a descriptive message and push the changes upstream

.. code-block:: console

  git add tracks.yaml
  git commit -s -m "galactic devel_branch: master -> galactic"
  git push origin master

Updating ros/rosdistro
======================

**Goal: Make a pull request like this one:** `ros/rosdistro#29286 <https://github.com/ros/rosdistro/pull/29286>`_

1. Fork ``ros/rosdistro``
2. Clone the original ``ros/rosdistro`` first

.. code-block:: console

  git clone https://github.com/ros/rosdistro.git

3. Add your own fork of ros/rosdistro as a remote

.. code-block:: console

  git remote add mine git@github.com:<your username>/rosdistro.git

4. Checkout the ``master`` branch and create a one-off branch for the change

.. code-block:: console

  git checkout master
  git pull origin master
  git checkout -b some_new_branch_name

5. Open the relevant ``<distro>/distribution.yaml`` files and find your repository
6. Change ``doc:`` -> ``version:`` from the old branch name to the new branch name
7. Change ``source:`` -> ``version:`` from the old branch name to the new branch name
8. Commit and push the changes to your fork

.. code-block:: console

  git add <distro>/distribution.yaml
  git commit -s -m "rosbag2 galactic devel_branch: master -> galactic"
  git push mine some_new_branch_name

9. Open a Pull Request on ros/rosdistro with the changes

