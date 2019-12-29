# Copyright 2009--2019 Mark Dickinson.
#
# This file is part of the bigfloat package.
#
# The bigfloat package is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The bigfloat package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bigfloat package.  If not, see <http://www.gnu.org/licenses/>.

major = 0
minor = 4
patch = 0
prerelease = ''

if prerelease:
    __version__ = "{}.{}.{}-{}".format(major, minor, patch, prerelease)
else:
    __version__ = "{}.{}.{}".format(major, minor, patch)

# Release and version for Sphinx purposes.

# The short X.Y version.
version = "{}.{}".format(major, minor)

# The full version, including patchlevel and alpha/beta/rc tags.
release = __version__
