#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Subtitle helper scripts.

This module merges two DXFP files together.
"""

from datetime import datetime
import re
import sys


class Subtitle(object):
    """
        A Subtitle object that contains content, with a start and end time.
    """
    def __init__(self, **kwargs):
        """
            A kwargs['entry'] has the format:
              <p begin="00:00:12.011" end="00:00:13.972">
                （ﾄﾘﾝﾄﾞﾙ）こんばんは<br />
                （一同）こんばんは
              </p>
        """
        if "entry" in kwargs:
            regex = '<p begin="(\d{2}:\d{2}:\d{2}.\d{3})" end="(\d{2}:\d{2}:\d{2}.\d{3})">(.+)</p>'
            result = re.compile(regex).match(kwargs["entry"])
            time_format = "%H:%M:%S.%f"
            self.start = datetime.strptime(result.groups()[0], time_format)
            self.end = datetime.strptime(result.groups()[1], time_format)
            self.content = result.groups()[2]
        else:
            self.start = kwargs["start"]
            self.end = kwargs["end"]
            self.content = kwargs["content"]

    def __str__(self):
        start = self.start.strftime("%H:%M:%S.%f")[:-3]
        end = self.end.strftime("%H:%M:%S.%f")[:-3]
        return '<p begin="%s" end="%s">%s</p>' % (start, end, self.content)


def create_subtitles_from_file(filename):
    """
        Reads a file and returns a list of Subtitles created.

        args: String (name of the file to read from)
        returns: List (of Subtitle objects)
    """
    _file = open(filename, 'r')
    subtitles = []
    for line in _file:
        if line.startswith("<p begin"):
            subtitles.append(Subtitle(entry=line))
    return subtitles


def create_file_from_subtitles(filename, subtitles):
    """
        Creates a DFXP file containing the provided subtitles.

        args: String (filename), List (of Subtitles)
        returns: None
    """
    starting_boilerplate = """<?xml version="1.0" encoding="UTF-8"?>\n<tt xml:lang='en' xmlns='http://www.w3.org/2006/10/ttaf1' xmlns:tts='http://www.w3.org/2006/10/ttaf1#style'>\n<body>\n<div xml:id="captions">\n"""
    _file = open(filename, 'w')
    _file.write(starting_boilerplate)
    for subtitle in subtitles:
        _file.write(subtitle.__str__() + "\n")
    ending_boilerplate = """</div>\n</body>\n</tt>"""
    _file.write(ending_boilerplate)
    _file.close()


def completely_overlap(subtitle_a, subtitle_b):
    """
        Checks if the subtitles completely overlap, by checking if
        the sum is off by only 0.9 seconds, or if 1 is off by < 0.3 seconds.

        args: Subtitle, Subtitle
        returns: Boolean, true if they completely overlap
    """
    diff_a = abs(subtitle_a.start - subtitle_b.start).total_seconds()
    diff_b = abs(subtitle_a.end - subtitle_b.end).total_seconds()
    return (diff_a < 0.3) or (diff_b < 0.3) or (diff_a + diff_b < 0.9)


def merge(subtitle_a, subtitle_b):
    """
        Creates a new Subtitle based on the two provided.

        args: Subtitle, Subtitle
        returns: Subtitle

    """
    return Subtitle(
        start=min(subtitle_a.start, subtitle_b.start),
        end=max(subtitle_a.end, subtitle_b.end),
        content=subtitle_a.content + "<br />" + subtitle_b.content
    )


def merge_subtitles(subtitles_a, subtitles_b):
    """
        Combines two lists of subtitles into a single one,
        merging any that overlap.

        args: List (of Subtitles), List (of Subtitles)
        returns: List (of Subtitles)
    """
    resulting_subtitles = []
    while subtitles_a and subtitles_b:
        # Check if the next subtitle from each start and end together.
        if completely_overlap(subtitles_a[0], subtitles_b[0]):
            # print "Merging subtitles", subtitles_a[0], subtitles_b[0]
            resulting_subtitles.append(merge(subtitles_a[0], subtitles_b[0]))
            # Remove the first two from each.
            subtitles_a.remove(subtitles_a[0])
            subtitles_b.remove(subtitles_b[0])
        else:
            # If they don't overlap, remove the earlier occuring one.
            if subtitles_a[0].start < subtitles_b[0].start:
                resulting_subtitles.append(subtitles_a[0])
                subtitles_a.remove(subtitles_a[0])
            else:
                resulting_subtitles.append(subtitles_b[0])
                subtitles_b.remove(subtitles_b[0])
    resulting_subtitles += subtitles_a
    resulting_subtitles += subtitles_b
    return resulting_subtitles


if __name__ == "__main__":
    first_subtitles = create_subtitles_from_file(sys.argv[1])
    second_subtitles = create_subtitles_from_file(sys.argv[2])
    print len(first_subtitles) + len(second_subtitles)
    new_subtitles = merge_subtitles(first_subtitles, second_subtitles)
    print len(new_subtitles)
    new_filename = sys.argv[1].replace('.dfxp', '-merged.dfxp')
    create_file_from_subtitles(new_filename, new_subtitles)
