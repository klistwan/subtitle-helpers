import sys

class Subtitle():

  def __init__(self, segment):
    split_segment = segment.strip().split('\n')
    self.idx = split_segment[0]
    times = split_segment[1]
    content = split_segment[2:]
    self.start = times.split()[0]
    self.end = times.split()[2]
    self.content = "\n".join(content)
    self.prev = None
    self.next = None

  def __str__(self):
    return "\n%s\n%s --> %s\n%s\n" % (self.idx, self.start, self.end, self.content)

  def __repr__(self):
    return self.__str__()

def file_to_content(filename):
  f = open(filename, 'r')
  content = f.read()
  return content.replace('\r', '')

def parse_to_subtitles(content):
  """
    Parses through a string and creates Subtitle objects.

    args: a String, represents the entire content of an SRT file
    returns: List of Subtitle objects
  """ 
  segments = [s for s in content.split("\n\n") if s.strip()]
  initial_subtitle = Subtitle(segments[0].strip())
  subtitles = [initial_subtitle]
  prev = initial_subtitle
  for segment in segments[1:]:
    subtitle = Subtitle(segment.strip())
    prev.next = subtitle
    subtitle.prev = prev
    prev = subtitle
    subtitles.append(subtitle)
  return subtitles

def can_merge_split_subtitles(first_sub, second_sub):
  """
    args: Subtitle, Subtitle
    returns: boolean (True if you can merge them. False if you can't)
  """
  return (first_sub.end == second_sub.start) and (first_sub.content == second_sub.content)

def merge_split_subtitles(first_sub, second_sub):
  """
    args: Subtitle, Subtitle
    returns: Subtitle
  """
  first_sub.end = second_sub.end
  return first_sub

def prompt_for_merge(current_sub, merge_candidate_sub):
  '''
  print "\nThese are the two candidates: ", current_sub, merge_candidate_sub
  print "\nThey would result in: ", merge_split_subtitles(current_sub, merge_candidate_sub)
  result = raw_input("\nDo you want to merge them? ")
  return result in ["y", "Y"]
  '''
  return True

def clean_subtitles(subtitles):
  """
    Finds any subtitles that were split by the OCR,
    and merges them together into a single subtitle.

    args: List of Subtitles
    returns: List of Subtitles, without split ones
  """
  current_idx = 0
  while current_idx < len(subtitles):
    current_sub = subtitles[current_idx]
    up_ahead = subtitles[current_idx + 1: current_idx + 6]
    potential_matches = filter(
      lambda s: (s.content == current_sub.content) and (s.start == current_sub.end), 
      up_ahead)
    # If no merge candidates, move to next sub.
    if not potential_matches:
      current_idx += 1
      continue
    # If there are, merge them.
    decision = prompt_for_merge(current_sub, potential_matches[0])
    if decision:
      current_sub = merge_split_subtitles(current_sub, potential_matches[0])
      subtitles[current_idx] = current_sub
      subtitles.remove(potential_matches[0])
  return subtitles

def join_subs(sub_a, sub_b):
  sub_a.content = sub_a.content.replace('\n', ' ')
  sub_b.content = sub_b.content.replace('\n', ' ')
  sub_a.content = "-%s\n-%s" % (sub_a.content, sub_b.content)
  return sub_a

def prompt_for_join(sub_a, sub_b):
  print "\nThese are the two candidates: ", sub_a, sub_b
  print "\nThey would result in: ", join_subs(sub_a, sub_b)
  result = raw_input("\nDo you want to merge them? ")
  return result in ["y", "Y"]

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
    potential_matches = filter(
      lambda s: (s.start == current_sub.start) or (s.end == current_sub.end), 
      up_ahead)
    # If no merge candidates, move to next sub.
    if not potential_matches:
      current_idx += 1
      continue
    # If there are, join them.
    decision = prompt_for_join(current_sub, potential_matches[0])
    if decision:
      current_sub = join_subs(current_sub, potential_matches[0])
      subtitles[current_idx] = current_sub
      subtitles.remove(potential_matches[0])
  return subtitles

def main2(filename):
  new_filename = filename.replace(".srt", " (reduced).srt")
  content = file_to_content(filename)
  subtitles = parse_to_subtitles(content)
  original_count = len(subtitles)
  subtitles = combine_simultaneous_subtitles(subtitles)
  print "original segment count: ", original_count
  print "current segment count : ", len(subtitles)
  f = open(new_filename, 'w')
  f.write("\n\n".join(map(lambda s: s.__str__(), subtitles)))
  f.close()
  print "Created new file: ", f.name

def main(filename):
  new_filename = filename.replace(".srt", " (cleaned).srt")
  content = file_to_content(filename)
  subtitles = parse_to_subtitles(content)
  subtitles = clean_subtitles(subtitles)
  print "original segment count: ", len(subtitles)
  print "current segment count : ", len(subtitles)
  f = open(new_filename, 'w')
  f.write("\n\n".join(map(lambda s: s.__str__(), subtitles)))
  f.close()
  print "Created new file: ", f.name

if __name__ == "__main__":
  main2(sys.argv[1])






























