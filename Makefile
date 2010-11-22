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

HBASE_PATH =  # Must be set from the command-line
SHELL_ARGS =
COMPRESSION = none# Can be set to `lzo'
HBASE_SHELL = $(HBASE_PATH)/bin/hbase $(SHELL_ARGS) shell
TABLE = hbench# Cannot be changed now as it's hardcoded in the code.

COMMON_FILES = \
  ProcSelfStatus.java	\

HBASE_TESTS = $(COMMON_FILES) \
  HBaseGet.java	\
  HBaseMultiPut.java	\
  HBasePut.java	\
  HTableFactory.java	\

ASYNCHBASE_TESTS = $(COMMON_FILES) \
  AsyncHBaseGet.java	\
  AsyncHBaseMultiPut.java	\
  AsyncHBasePut.java	\
  HBaseClientFactory.java	\

COMMON_DEPS = \
  third_party/common/zookeeper-3.3.1.jar	\

HBASE_DEPS = $(COMMON_DEPS) \
  third_party/hbase/commons-logging-1.1.1.jar	\
  third_party/hbase/hadoop-core-0.20.3-append-r964955-1240.jar	\
  third_party/hbase/hbase-0.89.20100924.jar	\
  third_party/hbase/log4j-1.2.15.jar	\

ASYNCHBASE_DEPS = $(COMMON_DEPS) \
  third_party/asynchbase/hbaseasync-1.0.jar	\
  third_party/asynchbase/log4j-over-slf4j-1.6.1.jar	\
  third_party/asynchbase/logback-classic-0.9.24.jar	\
  third_party/asynchbase/logback-core-0.9.24.jar	\
  third_party/asynchbase/netty-3.2.2.Final.jar	\
  third_party/asynchbase/slf4j-api-1.6.1.jar	\
  third_party/asynchbase/suasync-1.0.jar	\

HBASE_CP = `echo $(HBASE_DEPS) | tr ' ' :`
ASYNCHBASE_CP = `echo $(ASYNCHBASE_DEPS) | tr ' ' :`

all: build build/.javac-hbase-stamp build/.javac-hbaseasync-stamp build/.mktable-stamp

microbench: all
	@test -n "$(HBASE_PATH)" || { echo 'You must set HBASE_PATH'; exit 1; }
	echo "truncate '$(TABLE)'" | $(HBASE_SHELL)
	./microbench.py --debug --name='Simple edit' \
	  --hbase_cp=$(HBASE_CP) --hbase_class=HBasePut \
	  --asynchbase_cp=$(ASYNCHBASE_CP) --asynchbase_class=AsyncHBasePut
	./microbench.py --debug --name='Simple get' \
	  --hbase_cp=$(HBASE_CP) --hbase_class=HBaseGet \
	  --asynchbase_cp=$(ASYNCHBASE_CP) --asynchbase_class=AsyncHBaseGet
	./microbench.py --debug --name='Multiple edits' \
	  --hbase_cp=$(HBASE_CP) --hbase_class=HBaseMultiPut \
	  --asynchbase_cp=$(ASYNCHBASE_CP) --asynchbase_class=AsyncHBaseMultiPut

build:
	mkdir build

build/.javac-hbase-stamp: $(HBASE_TESTS) $(HBASE_DEPS)
	javac -d build $(JAVAC_FLAGS) -cp $(HBASE_CP) $(HBASE_TESTS)
	@touch build/.javac-hbase-stamp

build/logback.xml: logback.xml
	cp -f $^ $@

build/.javac-hbaseasync-stamp: build/logback.xml $(ASYNCHBASE_TESTS) $(ASYNCHBASE_DEPS)
	javac -d build $(JAVAC_FLAGS) -cp $(ASYNCHBASE_CP) $(ASYNCHBASE_TESTS)
	@touch build/.javac-hbaseasync-stamp

build/.mktable-stamp:
	@test -n "$(HBASE_PATH)" || { echo 'You must set HBASE_PATH'; exit 1; }
	echo 'list' | $(HBASE_SHELL) | fgrep -qw '$(TABLE)' \
	  || echo "create '$(TABLE)', {NAME => 't', COMPRESSION => '$(COMPRESSION)'}" \
	  | $(HBASE_SHELL)
	@touch build/.mktable-stamp

printhcp:
	@echo $(HBASE_CP)

printahcp:
	@echo $(ASYNCHBASE_CP)

clean:
	rm -rf build/

.PHONY: all microbench clean printhcp printahcp
