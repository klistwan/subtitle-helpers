"""Subtitle helper scripts.

This module contains two scripts to help clean broken Subtitles.
"""

import datetime
import sys


class Subtitle(object):
    """
        Subtitle(segment)

        A Subtitle object that contains content, with a start and end time.
    """
    def __init__(self, segment):
        split_segment = segment.strip().split('\n')
        self.idx = split_segment[0]
        times = split_segment[1]
        content = split_segment[2:]
        self.start = times.split()[0]
        self.end = times.split()[2]
        self.content = "\n".join(content)

    def __str__(self):
        return "\n{}\n{} --> {}\n{}\n".format(
            self.idx, self.start, self.end, self.content)

    def __repr__(self):
        return self.__str__()

    def extend(self, next_subtitle):
        """
            Changes current subtitle's end time to next_subtitle's.

            arg: Subtitle (self), Subtitle
            returns: None
        """
        self.end = next_subtitle.end

    def add_simultaneous_sub(self, next_sub):
        """
            Joins together two subtitles' contents on separate lines,
            starting with a hyphen.

            arg: Subtitle (self), Subtitle)
            returns: None
        """
        self.content = self.content.replace('\n', ' ')
        next_sub.content = next_sub.content.replace('\n', ' ')
        self.content = "-%s\n-%s" % (self.content, next_sub.content)

    def length(self):
        """
            Returns the length of the subtitle.

            args: Subtitle (self)
            returns datetime.timedelta
        """
        time_format = "%H:%M:%S,%f"
        return datetime.datetime.strptime(self.end, time_format) - \
            datetime.datetime.strptime(self.start, time_format)


def file_to_content(filename):
    """
        Opens and returns the contents of a file.

        args: a String, the name of the file to read
        returns: a String, the contents of the file read
    """
    _file = open(filename, 'r')
    content = _file.read()
    _file.close()
    return content.replace('\r', '')


def parse_to_subtitles(content):
    """
        Parses through a string and creates Subtitle objects.

        args: a String, represents the entire content of an SRT file
        returns: List of Subtitle objects
    """
    return [Subtitle(s.strip()) for s in content.split("\n\n") if s.strip()]


def can_merge_split_subtitles(first_sub, second_sub):
    """
        Checks if provided subtitles can be merged together.

        args: Subtitle, Subtitle
        returns: boolean (True if you can merge them. False if you can't)
    """
    return (first_sub.end == second_sub.start) and \
           (first_sub.content == second_sub.content)


def merge_split_subtitles(subtitles):
    """
        Finds all subtitles that were split by the OCR,
        and merges them together into a single subtitle.

        args: List of Subtitles
        returns: List of Subtitles, without split ones
    """
    current_idx = 0
    while current_idx < len(subtitles):
        current_sub = subtitles[current_idx]
        up_ahead = subtitles[current_idx + 1: current_idx + 6]
        potential_matches = \
            [s for s in up_ahead if (s.content == current_sub.content) and
             (s.start == current_sub.end)]
        # If no merge candidates, move to next subtitle.
        if not potential_matches:
            current_idx += 1
            continue
        # If there are, merge them.
        current_sub.extend(potential_matches[0])
        subtitles[current_idx] = current_sub
        subtitles.remove(potential_matches[0])
    return subtitles


def combine_simultaneous_subtitles(subtitles):
    """
        Combines subtitles that occur at the same start or end time
        into a single subtitle.

        args: List of Subtitle objects
        returns: List of Subtitle objects
    """
    current_idx = 0
    while current_idx < len(subtitles):
        current_sub = subtitles[current_idx]
        up_ahead = subtitles[current_idx + 1: current_idx + 6]
        potential_matches = [s for s in up_ahead if
                             (s.start == current_sub.start) or
                             (s.end == current_sub.end)]
        # If no merge candidates, move to next sub.
        if not potential_matches:
            current_idx += 1
            continue
        # If there are, join them.
        current_sub.add_simultaneous_sub(potential_matches[0])
        subtitles[current_idx] = current_sub
        subtitles.remove(potential_matches[0])
    return subtitles


def flag_short_subtitles(subtitles):
    """
        Prints any subtitles that are too short.

        args: List, contains Subtitle objects
        returns: None
    """
    for subtitle in subtitles:
        length = subtitle.length().total_seconds()
        subtitle = " ".join([subtitle.idx, subtitle.start,
                             subtitle.end, subtitle.content])
        if length < 0.9:
            print "Alert: %.3f/1.000 - %s" % (length, subtitle)
        elif length < 1.5:
            print "Warning: %.3f/1.500 - %s" % (length, subtitle)


def merge_simultaneous_subtitles(filename):
    """
        Goes through a file, indicated by the filename, and merges
        all subtitles that start or end at the same time. It writes
        these new subtitles to a new file, which takes the existing
        file's name and adds (reduced) to the end of it.

        args: String, represents the file's name
        returns: None
    """
    new_filename = filename.replace(".srt", " (reduced).srt")
    content = file_to_content(filename)
    subtitles = parse_to_subtitles(content)
    original_count = len(subtitles)
    subtitles = combine_simultaneous_subtitles(subtitles)
    flag_short_subtitles(subtitles)
    print "original segment count: ", original_count
    print "current segment count : ", len(subtitles)
    _file = open(new_filename, 'w')
    _file.write("\n\n".join([s.__str__() for s in subtitles]))
    _file.close()
    print "Created new file: ", _file.name


def merge_broken_subtitles(filename):
    """
        Goes through a file and merges subtitles incorrectly
        split by Google's OCR. It writes these to a new file,
        the name of which is the old file's name and (cleaned).

        args: String, the name of the file
        returns: None
    """
    new_filename = filename.replace(".srt", " (cleaned).srt")
    content = file_to_content(filename)
    subtitles = parse_to_subtitles(content)
    original_count = len(subtitles)
    subtitles = merge_split_subtitles(subtitles)
    print "original segment count: ", original_count
    print "current segment count : ", len(subtitles)
    _file = open(new_filename, 'w')
    _file.write("\n\n".join([s.__str__() for s in subtitles]))
    _file.close()
    print "Created new file: ", _file.name
    merge = raw_input("Do you want to merge simultaneous subtitles too? ")
    if merge in ["y", "yes"]:
        merge_simultaneous_subtitles(_file.name)


if __name__ == "__main__":
    merge_broken_subtitles(sys.argv[1])
