import unittest
import main

class SubsTestCase(unittest.TestCase):
  def test_subtitle_init(self):
    content = "1\n00:05:14 --> 00:06:19\ndifference is a\ntravel the lands "
    subtitle = main.Subtitle(content)
    self.assertEqual(subtitle.start, "00:05:14")
    self.assertEqual(subtitle.end, "00:06:19")
    self.assertEqual(subtitle.content, "difference is a\ntravel the lands")

  def test_parse_to_subtitles(self):
    content = "1\n00:05:14 --> 00:06:19\ndifference is a\ntravel the lands\n\n"
    content += "2\n00:08:19 --> 00:09:25\nwhat is a life\nnothing else there is"
    subtitles = main.parse_to_subtitles(content)
    self.assertEqual(subtitles[0].start, "00:05:14")
    self.assertEqual(subtitles[1].start, "00:08:19")

  def test_can_merge_split_subtitles(self):
    first_sub = main.Subtitle("1\n00:05:14 --> 00:06:19\ndifference is a\ntravel the lands")
    second_sub = main.Subtitle("2\n00:06:19 --> 00:08:93\ndifference is a\ntravel the lands")
    self.assertTrue(main.can_merge_split_subtitles(first_sub, second_sub))

    first_sub.content = "no"
    self.assertFalse(main.can_merge_split_subtitles(first_sub, second_sub))

    second_sub.content = first_sub.content
    first_sub.end = "00:05:99"
    self.assertFalse(main.can_merge_split_subtitles(first_sub, second_sub))   

  def test_merge_split_subtitles(self):
    first_sub = main.Subtitle("1\n00:05:14 --> 00:06:19\ndifference is a\ntravel the lands")
    second_sub = main.Subtitle("2\n00:06:19 --> 00:08:93\ndifference is a\ntravel the lands")
    subtitle = main.merge_split_subtitles(first_sub, second_sub)
    self.assertEqual(subtitle.start, "00:05:14")
    self.assertEqual(subtitle.end, "00:08:93")
    self.assertEqual(subtitle.content, "difference is a\ntravel the lands")

  def test_clean_subtitles(self):
    content = main.file_to_content('tests/fixtures/1.srt')
    subtitles = main.parse_to_subtitles(content)
    self.assertEqual(len(subtitles), 6)
    subtitles = main.clean_subtitles(subtitles)
    self.assertEqual(len(subtitles), 4)

    content = main.file_to_content('tests/fixtures/3.srt')
    subtitles = main.parse_to_subtitles(content)
    self.assertEqual(len(subtitles), 3)
    subtitles = main.clean_subtitles(subtitles)
    self.assertEqual(len(subtitles), 2)

  def test_join_subtitles(self):
    content = main.file_to_content('tests/fixtures/2.srt')
    subtitles = main.parse_to_subtitles(content)
    self.assertEqual(len(subtitles), 5)
    subtitles = main.combine_simultaneous_subtitles(subtitles)
    self.assertEqual(len(subtitles), 3)

if __name__ == '__main__':
  unittest.main()