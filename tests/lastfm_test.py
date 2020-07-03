""" Testing for LastFM module """
import asyncio
import json
import unittest

from modules.lastfm import _parse_track
from modules.models import Album, Artist, Track


class LastFMTests(unittest.TestCase):
    """ Unit tests for LastFM module """

    def __init__(self, *args, **kwargs):
        super(LastFMTests, self).__init__(*args, **kwargs)
        with open("res/lastfm_samples.json", "r") as readfile:
            self.test_samples = json.loads(readfile.read())

    def test_track_parser(self):
        expected = [
            Track(
                name="Scared of the Dark (feat. XXXTENTACION)",
                artists=[Artist("Lil Wayne"), Artist("Ty Dolla $ign")],
                time=1593522882,
                album=Album(
                    "Spider-Man: Into the Spider-Verse (Soundtrack From & Inspired by the Motion Picture)",
                    "https://lastfm.freetls.fastly.net/i/u/300x300/0c9a42c47c4b2e26cedfbd117f9f0c24.jpg",
                ),
            ),
            Track(
                name="Jump (Acoustic)",
                artists=[
                    Artist(
                        "Julia Michaels", mbid="4757df70-6c3e-46b8-99c0-a68644595c9a"
                    )
                ],
                time=1593796849,
                album=Album(
                    "Jump (Acoustic)",
                    "https://lastfm.freetls.fastly.net/i/u/300x300/ded77226f141248e12497f69b0af6715.jpg",
                    mbid="1c15461e-d42b-48c7-98da-11dbec0b617e"
                ),
                mbid="57476328-1358-47b8-a273-9c3308640e48"
            ),
            Track(
                name="Lucky",
                artists=[Artist("Chelsea Cutler")],
                time=1593696607,
                album=Album(
                    "How To Be Human",
                    "https://lastfm.freetls.fastly.net/i/u/300x300/e6ad6e29c4e764a7f82b45aba645cd83.jpg",
                    mbid="9eab73c5-a614-4a63-a700-8f0c90bd970b"
                ),
            ),
            Track(
                name="If The World Was Ending (feat. Julia Michaels)",
                artists=[Artist("JP Saxe"), Artist("Julia Michaels")],
                time=1593552783,
            ),
            Track(
                name="Sunday Candy",
                artists=[Artist("Donnie Trumpet"), Artist("The Social Experiment")],
                time=1593552616,
                album=Album(
                    "Surf",
                    "https://lastfm.freetls.fastly.net/i/u/300x300/29ce6058b6b0439691511d104b8252d0.jpg",
                    mbid="2f536a6a-ffbe-4396-a6a5-098302d6c4d0"
                ),
                mbid="40c3001c-3b26-4629-bdb3-be4abf8e509a"
            ),
        ]

        inputs = self.test_samples["sample_tracks"]
        for (index, expected_output) in enumerate(expected):
            output: Track = _parse_track(inputs[index])
            self.assertEqual(expected_output, output, "Test Parser")


if __name__ == "__main__":
    unittest.main()
