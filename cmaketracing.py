#!/usr/bin/env python3
# Copyright 2018 Nico Weber
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Converts one (or several) CMake instrumentation index file
   into chrome's about:tracing format.

If clang -ftime-trace .json files are found adjacent to generated files they
are embedded.

Usage:
    python cmaketracing.py {index_file} > trace.json
"""

from __future__ import print_function
import json
import os
import optparse
import re
import sys


class Target:
    """Represents a single line read for a .ninja_log file. Start and end times
    are milliseconds."""
    def __init__(self, start, end):
        self.start = int(start)
        self.end = int(end)
        self.targets = []


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

def read_targets(index, show_all):
    """Reads all targets from .ninja_log file |log_file|, sorted by start
    time"""
    snippets = []
    with open(index, 'r') as f:
        snippet_files = json.load(f)["snippets"]
    for file in snippet_files:
        with open(os.path.join(os.path.dirname(os.path.dirname(index)), file)) as f:
            snippets.append(json.load(f))
            snippets[-1]["name"] = file

    targets = {}
    last_end_seen = 0
    show_all = True
    for x in snippets:
        start, end = x["timeStart"], x["timeStart"]+x["duration"]
        name = x["testName"] if "testName" in x else x["role"]
        if "outputs" in x and len(x["outputs"]) > 0:
            name = os.path.basename(x["outputs"][0])
        cmdhash = str(hash(x["command"] + str(x["timeStart"])))
        if not show_all and int(end) < last_end_seen:
            # An earlier time stamp means that this step is the first in a new
            # build, possibly an incremental build. Throw away the previous
            # data so that this new build will be displayed independently.
            targets = {}
        last_end_seen = int(end)
        targets.setdefault(cmdhash, Target(start, end)).targets.append(name)
    return sorted(targets.values(), key=lambda job: job.end, reverse=True)


class Threads:
    """Tries to reconstruct the parallelism from a .ninja_log"""
    def __init__(self):
        self.workers = []  # Maps thread id to time that thread is occupied for

    def alloc(self, target):
        """Places target in an available thread, or adds a new thread."""
        for worker in range(len(self.workers)):
            if self.workers[worker] >= target.end:
                self.workers[worker] = target.start
                return worker
        self.workers.append(target.start)
        return len(self.workers) - 1


def read_events(trace, options):
    """Reads all events from time-trace json file |trace|."""
    trace_data = json.load(trace)

    def include_event(event, options):
        """Only include events if they are complete events, are longer than
        granularity, and are not totals."""
        return ((event['ph'] == 'X') and
                (event['dur'] >= options['granularity']) and
                (not event['name'].startswith('Total')))

    return [x for x in trace_data['traceEvents'] if include_event(x, options)]


def trace_to_dicts(target, trace, options, pid, tid):
    """Read a file-like object |trace| containing -ftime-trace data and yields
    about:tracing dict per eligible event in that log."""
    ninja_time = (target.end - target.start) * 1000
    for event in read_events(trace, options):
        # Check if any event duration is greater than the duration from ninja.
        if event['dur'] > ninja_time:
            print("Inconsistent timing found (clang time > ninja time). Please"
                  " ensure that timings are from consistent builds.")
            sys.exit(1)

        # Set tid and pid from ninja log.
        event['pid'] = pid
        event['tid'] = tid

        # Offset trace time stamp by ninja start time.
        event['ts'] += (target.start * 1000)

        yield event


def embed_time_trace(ninja_log_dir, target, pid, tid, options):
    """Produce time trace output for the specified ninja target. Expects
    time-trace file to be in .json file named based on .o file."""
    for t in target.targets:
        o_path = os.path.join(ninja_log_dir, t)
        json_trace_path = os.path.splitext(o_path)[0] + '.json'
        try:
            with open(json_trace_path, 'r') as trace:
                for time_trace_event in trace_to_dicts(target, trace, options,
                                                       pid, tid):
                    yield time_trace_event
        except IOError:
            pass


def log_to_dicts(log, pid, options):
    """Reads a file-like object |log| containing a .ninja_log, and yields one
    about:tracing dict per command found in the log."""
    threads = Threads()
    for target in read_targets(log, options['showall']):
        tid = threads.alloc(target)

        yield {
            'name': '%0s' % ', '.join(target.targets), 'cat': 'targets',
            'ph': 'X', 'ts': (target.start * 1000),
            'dur': ((target.end - target.start) * 1000),
            'pid': pid, 'tid': tid, 'args': {},
            }
        if options.get('embed_time_trace', False):
            # Add time-trace information into the ninja trace.
            try:
                ninja_log_dir = os.path.dirname(log.name)
            except AttributeError:
                continue
            for time_trace in embed_time_trace(ninja_log_dir, target, pid,
                                               tid, options):
                yield time_trace


def main(argv, outfile=None):
    usage = __doc__
    parser = optparse.OptionParser(usage)
    parser.add_option('-a', '--showall', action='store_true', dest='showall',
                      default=False,
                      help='report on last build step for all outputs. Default '
                      'is to report just on the last (possibly incremental) '
                      'build')
    parser.add_option('-g', '--granularity', type='int', default=50000,
                      dest='granularity',
                      help='minimum length time-trace event to embed in '
                      'microseconds. Default: %default')
    parser.add_option('-e', '--embed-time-trace', action='store_true',
                      default=False, dest='embed_time_trace',
                      help='embed clang -ftime-trace json file found adjacent '
                      'to a target file')
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print("Must specify at least one index file")
        parser.print_help()
        return 1

    entries = []
    for pid, log_file in enumerate(args):
        entries += list(log_to_dicts(log_file, pid, vars(options)))
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(entries, f)
    else:
        json.dump(entries, sys.stdout)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
