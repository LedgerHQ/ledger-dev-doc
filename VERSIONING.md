# Versioning

The version for this documentation is represented by a single integer number
which is tagged on the commit corresponding to the release of a specific version
of the documentation. In `/source/conf.py`, both the `version` and `release`
option shall always be the same, and represent the latest release version. As
such, they should always be bumped by the commit that was tagged with a version
number.

The version numbers used for this documentation doesn't have any relevant
meaning to the reader. Versioning was implemented such that links to this
documentation could be retained, even in future versions if certain references
change (this is mainly important for intersphinx).

For example, to link to a specific reference for a specific version, you may do
so like this:

https://ledger.readthedocs.io/en/1/bolos/features.html#term-issuer

The version number is simply an integer counter that increments every time the
docs have been changed and are ready for publication. All that matters is that
the version number is bumped every time a new build should be available on RTD.

As such, the checklist for releasing a new version of this documentation is as
follows:

1. Create a final commit that bumps the version numbers in `/source/conf.py`.
2. Tag that commit with the appropriate version number.
3. Done! RTD should find the tag and build the docs automagically.
