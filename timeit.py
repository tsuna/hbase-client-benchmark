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
"""Times how long it takes to execute a program."""

import resource
import subprocess
import sys
import time


class TimingResult(object):
  """Stores basic information about a process we timed."""

  def __init__(self, rc, rtime, utime, stime, csw, icsw):
    self.rc = rc
    self.rtime = rtime
    self.utime = utime
    self.stime = stime
    self.csw = csw
    self.icsw = icsw

  def __str__(self):
    return ("real=%.1f; user=%.1f; sys=%.1f; csw=%r; icsw=%r;"
            % (self.rtime, self.utime, self.stime, self.csw, self.icsw))


DEVNULL = open("/dev/null", "w")

def run(cmdline, output=None):
  """Runs the given command line and returns a TimingResult about it."""
  if output is None:
     output = DEVNULL
  start = time.time() * 1000
  before = resource.getrusage(resource.RUSAGE_CHILDREN)
  p = subprocess.Popen(cmdline, stdout=output, stderr=output)
  rc = p.wait()
  end = time.time() * 1000
  after = resource.getrusage(resource.RUSAGE_CHILDREN)
  # Store everything in milliseconds.
  return TimingResult(rc,
                      end - start,
                      (after.ru_utime - before.ru_utime) * 1000,
                      (after.ru_stime - before.ru_stime) * 1000,
                      # Not all OSes are required to implement the following:
                      after.ru_nvcsw - before.ru_nvcsw,
                      after.ru_nivcsw - before.ru_nivcsw)


if __name__ == "__main__":
  args = sys.argv[1:]
  assert args, "Need a command-line in argument"
  result = run(args)
  print result
  sys.exit(result.rc)
