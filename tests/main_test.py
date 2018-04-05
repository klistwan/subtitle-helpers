#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unittest

import main


class SubsTestCase(unittest.TestCase):
    def test_subtitle_init(self):
        content = "1\n00:05:14 --> 00:06:19\na\nb"
        subtitle = main.Subtitle(content)
        self.assertEqual(subtitle.start, "00:05:14")
        self.assertEqual(subtitle.end, "00:06:19")
        self.assertEqual(subtitle.content, "a\nb")

    def test_subtitle_length(self):
        content = "1\n00:05:14,192 --> 00:05:19,934\na\nb"
        subtitle = main.Subtitle(content)
        self.assertEqual(subtitle.length(), datetime.timedelta(0, 5, 742000))

    def test_create_subtitles_from_file(self):
        subtitles = main.create_subtitles_from_file('tests/fixtures/3.srt')
        self.assertEqual(subtitles[0].content, "どうして?")
        self.assertEqual(subtitles[1].content, "どうして?")
        self.assertEqual(subtitles[2].content,
                         "(哲也)入ってきたばっかのとき\n結構カッコつけてたからね")

    def test_can_merge_split_subtitles(self):
        first_sub = main.Subtitle("1\n00:05:14 --> 00:06:19\na\nb")
        second_sub = main.Subtitle("2\n00:06:19 --> 00:08:93\na\nb")
        self.assertTrue(main.can_merge_split_subtitles(first_sub, second_sub))

        # If content is different, it should fail.
        first_sub.content = "no"
        self.assertFalse(main.can_merge_split_subtitles(first_sub, second_sub))

        # If end times are different, it should fail.
        second_sub.content = first_sub.content
        first_sub.end = "00:05:99"
        self.assertFalse(main.can_merge_split_subtitles(first_sub, second_sub))

    def test_extend(self):
        first_sub = main.Subtitle("1\n00:05:14 --> 00:06:19\na\nb")
        second_sub = main.Subtitle("2\n00:06:19 --> 00:08:93\na\nb")
        first_sub.extend(second_sub)
        self.assertEqual(first_sub.start, "00:05:14")
        self.assertEqual(first_sub.end, "00:08:93")
        self.assertEqual(first_sub.content, "a\nb")

    def test_merge_split_subtitles(self):
        subtitles = main.create_subtitles_from_file('tests/fixtures/1.srt')
        self.assertEqual(len(subtitles), 6)
        subtitles = main.merge_split_subtitles(subtitles)
        self.assertEqual(len(subtitles), 4)

        subtitles = main.create_subtitles_from_file('tests/fixtures/3.srt')
        self.assertEqual(len(subtitles), 3)
        subtitles = main.merge_split_subtitles(subtitles)
        self.assertEqual(len(subtitles), 2)

    def test_add_simultaneous_subtitles(self):
        first_sub = main.Subtitle("1\n00:05:14 --> 00:07:19\nwhat is love")
        second_sub = main.Subtitle("2\n00:06:19 --> 00:07:19\ndon't hurt me")
        first_sub.add_simultaneous_sub(second_sub)
        self.assertEqual(first_sub.content, "-what is love\n-don't hurt me")

    def test_join_subtitles(self):
        subtitles = main.create_subtitles_from_file('tests/fixtures/2.srt')
        self.assertEqual(len(subtitles), 5)
        subtitles = main.combine_simultaneous_subtitles(subtitles)
        self.assertEqual(len(subtitles), 3)


if __name__ == '__main__':
    unittest.main()
