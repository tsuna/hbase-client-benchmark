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
"""Runs a micro benchmark to compare HBase and Async HBase."""

import atexit
import optparse
import os
import sys
import tempfile

import gcstats
import timeit

argp = optparse.OptionParser()
argp.add_option("--debug", dest="debug", action="store_true",
                help="Debug the microbenchark (don't delete temp files etc.)")
argp.add_option("--name", dest="name", metavar="NAME",
                help="Name of the test")
argp.add_option("--hbase_cp", dest="hbase_cp", metavar="CLASSPATH",
                help="CLASSPATH to use for the HBase test")
argp.add_option("--asynchbase_cp", dest="asynchbase_cp", metavar="CLASSPATH",
                help="CLASSPATH to use for the HBase Async test")
argp.add_option("--hbase_class", dest="hbase_class", metavar="CLASS",
                help="Class to execute for the HBase test")
argp.add_option("--asynchbase_class", dest="asynchbase_class", metavar="CLASS",
                help="Class to execute for the HBase Async test")

options, args = argp.parse_args()
if args:
  parser.error("Unexpected arguments: %s" % " ".join(args))

tmpdir = tempfile.mkdtemp(prefix="hbench-")
if options.debug:
  print "tmpdir:", tmpdir
else:
  atexit.register(timeit.run, ["rm", "-rf", tmpdir])

BENCH_NUM = 0

def bench(cp, klass):
  global BENCH_NUM
  BENCH_NUM += 1

  ITERATIONS = 3
  timings = []
  for iteration in xrange(ITERATIONS + 1):
    gclog = tmpdir + "/%02d-gclog-%02d" % (BENCH_NUM, iteration)
    output = open(tmpdir + "/%02d-output-%02d" % (BENCH_NUM, iteration), "w")
    cmdline = ["java",
      "-verbose:gc", "-XX:+PrintGCDetails", "-XX:+PrintGCTimeStamps",
      "-XX:+PrintClassHistogram", "-XX:+PrintHeapAtGC", "-XX:+PrintTLAB",
      "-Xloggc:" + gclog, "-cp", cp + ":build", klass]
    if iteration == 0 and "linux" in sys.platform:
      cmdline[:0] = ["strace", "-qfc"]
    timing = timeit.run(cmdline, output=output)
    output.close()
    #if options.debug:
    #  print "%s: %s" % (" ".join(cmdline), timing)
    if timing.rc:
      print "error: command returned %d: %s" % (timing.rc, " ".join(cmdline))
      print open(output.name).read(),
      sys.exit(1)
    timing.VmRSS = 0
    timing.threads = 0
    timing.futex_calls = 0
    timing.nsyscalls = 0
    if "linux" in sys.platform:
      for line in open(output.name):
        if line.startswith("Vm"):  # e.g. "VmRSS:    39500 kB\n"
          what, size, kb = line.split()
          what = what[:-1]  # Remove trailing colon
          size = int(size)
          setattr(timing, what, size)
        elif line.startswith("Threads:"):
          timing.threads = int(line.split()[1])
        elif iteration == 0 and line.endswith(" futex\n"):
          timing.futex_calls = int(line.split()[3])
      if iteration == 0:
        assert line.endswith("total\n")
        timing.nsyscalls = int(line.split()[2])
    timing.gc = gcstats.parse(gclog)
    timings.append(timing)

  # 1st itertion = warm up (to ensure that all binaries and libraries are in
  # the buffer cache etc.)
  nsyscalls = timings[0].nsyscalls
  futex_calls = timings[0].futex_calls
  del timings[0]
  n = float(len(timings))
  rss   = sum(t.VmRSS for t in timings) / n
  rtime = sum(t.rtime for t in timings) / n
  utime = sum(t.utime for t in timings) / n
  stime = sum(t.stime for t in timings) / n
  csw   = sum(t.csw   for t in timings) / n
  icsw  = sum(t.icsw  for t in timings) / n
  memused = dict((gen, (sum(t.gc.memused[gen][0] for t in timings) /n,
                        sum(t.gc.memused[gen][1] for t in timings) / n))
                  for gen in timings[0].gc.memused)
  print ("real=%.1f; user=%.1f; sys=%.1f; csw=%.1f; icsw=%.1f; syscalls=%d;"
         " futex=%d; rss=%.0f;"
         % (rtime, utime, stime, csw, icsw, nsyscalls, futex_calls, rss))
  for gen, (used, total) in memused.iteritems():
    print "             %s: %dK / %dK" % (gen, used, total)

print options.name
print "=" * len(options.name)
print "HBase:      ",
bench(options.hbase_cp, options.hbase_class)
print "HBase Async:",
bench(options.asynchbase_cp, options.asynchbase_class)
