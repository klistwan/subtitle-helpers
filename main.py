import sys


class Subtitle(object):
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
        self.end = next_subtitle.end

    def add_simultaneous_sub(self, next_sub):
        self.content = self.content.replace('\n', ' ')
        next_sub.content = next_sub.content.replace('\n', ' ')
        self.content = "-%s\n-%s" % (self.content, next_sub.content)


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


def merge_simultaneous_subtitles(filename):
    new_filename = filename.replace(".srt", " (reduced).srt")
    content = file_to_content(filename)
    subtitles = parse_to_subtitles(content)
    original_count = len(subtitles)
    subtitles = combine_simultaneous_subtitles(subtitles)
    print "original segment count: ", original_count
    print "current segment count : ", len(subtitles)
    _file = open(new_filename, 'w')
    _file.write("\n\n".join([s.__str__() for s in subtitles]))
    _file.close()
    print "Created new file: ", _file.name


def merge_broken_subtitles(filename):
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
