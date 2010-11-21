#!/usr/bin/python
# Copyright 2010  Benoit Sigoure
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
"""Small library to parse Java GC logs and extract basic stats."""

import re
import sys

class GcStats(object):

  def __init__(self):
    self.memused = {}  # Maps generation used to (used, total).

  def __str__(self):
    return "\n".join("%s: %dK / %dK" % (gen, used, total)
                     for gen, (used, total) in self.memused.iteritems())
def parse(path):
  gc = GcStats()
  for line in open(path):
    if line == "Heap\n":
      continue
    m = re.match(r"\s*([- \w]+) ?[gG]en(?:eration)?\s+total (\d+)K, used (\d+)K.*", line)
    if m:
      gc.memused[m.group(1).strip()] = (int(m.group(3)), int(m.group(2)))
      continue
    m = re.match("  \w+\s+space \d+K,\s+\d+% used \[[^)]+\)$", line)
    if m:
      continue
    sys.stderr.write("Unrecognized line in %s: %r\n" % (path, line))
  return gc

if __name__ == "__main__":
  args = sys.argv[1:]
  assert len(args) == 1, "Need a single path in argument"
  result = parse(args[0])
  print result
