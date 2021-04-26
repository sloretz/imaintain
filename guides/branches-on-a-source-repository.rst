***********************************************
What branches should be on a source repository?
***********************************************

Different branches are needed on a source repository, though many maintainers have different ideas about this.
This guide is recommends a common way of doing it.

.. contents:: Table of Contents

Default Branch
==============

The default branch is the one checked out by default when you clone the repository.
It's shown by default when someone navigates to your repository's web page.
It should be called ``master`` or ``main``.
When you release a repository into `ROS Rolling <https://docs.ros.org/en/rolling/Releases/Release-Rolling-Ridley.html>`_, it should be released from this branch.

This branch should never be deleted.

ROS distro branches
===================

There should be one branch for every ROS distro this repository is released into.
The branch should be called the lowercase ROS distro name optionally with a ``-devel`` prefix (ex: ``galactic`` or ``galactic-devel``).
These branches should live as long as the ROS distro is not EOL.
On most repositories these branches are never deleted.

Feature or bug fix branches
===========================

Create a new branch for every feature or bug fix you work on.
It can be called anything you like, as long as it isn't easily confused with the default branch or a ROS distro branch.
They should be based off of the default branch, and merged into the default branch via a pull request once complete.
Delete these branches as soon as their pull request is merged.
Once the feature or bug fix is merged, you can consider backporting them to an older ROS distro.

Backport branches
=================

Sometimes you'll want to backport changes into an older ROS distro.
These branches should be based off the ROS distro branch they are targeting.
It can be called anything you like, though including the ROS distro name can be helpful (ex: ``foxy__backport_284``).
In most cases the commits on these branches are ``git cherry-pick`` of commits on the default branch.
Delete these branches as soon as their pull request is merged.
