---
title: Scap for deploying at WMF
author: WMF Release Engineering
date: work in progress
bindings: scap.yaml
functions: scap.python
...

Introduction
=============================================================================

Scap is a tool for deploying MediaWiki, and perhaps other software, to
servers at the Wikimedia Foundation (WMF). It's meant to be used by
the WMF release engineering and SRE teams, and trusted other parties.

This document describes some of the acceptance criteria for Scap, and
how they can be verified automatically.


Architecture
=============================================================================

This chapter describes the very highest level of Scap's architecture:
the inputs, output, side-effects, and interactions with various other
entities.

~~~dot
digraph "arch" {
  scap [shape=box];
  git -> scap;
  scap -> group0;
  scap -> group1;
  scap -> group2;
}
~~~



Acceptance criteria
=============================================================================

This chapter documents the acceptance criteria for the software, and
how they're they're verified automatically, in the form of scenarios.


scap version works
-----------------------------------------------------------------------------

This is a smoke test: if "scap version" runs, outputs something that
looks like a version number, and exits with a zero code, we're
satisfied.

~~~scenario
given a built scap
when I run scap version
then the exit code is 0
then the output matches ^\d+(\.\d+)+(-\S+)?$
~~~
