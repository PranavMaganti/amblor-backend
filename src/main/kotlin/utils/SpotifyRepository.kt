package utils

import com.adamratzman.spotify.SpotifyAppApi
import com.adamratzman.spotify.models.Artist
import com.adamratzman.spotify.models.Track
import com.adamratzman.spotify.spotifyAppApi
import models.ScrobbleQuery

data class MatchedScrobble(val track: Track, val artists: List<Artist?>, val time: Int, val query: ScrobbleQuery)

object SpotifyRepository {
    lateinit var spotifyApi: SpotifyAppApi

    suspend fun init() {
        val clientId = System.getenv("SPOTIFY_CLIENT_ID")
        val clientSecret = System.getenv("SPOTIFY_CLIENT_SECRET")
        spotifyApi = spotifyAppApi(clientId, clientSecret).build()
    }

    suspend fun matchTrack(query: ScrobbleQuery, titleOnly: Boolean = false): MatchedScrobble? {
        val spotifyQuery = query.getSpotifyQuery(titleOnly)
        val candidateTracks = spotifyApi.search.searchTrack(spotifyQuery, limit = 3).items

        if (candidateTracks.isEmpty() && titleOnly) {
            return null
        } else if (candidateTracks.isEmpty()) {
            return matchTrack(query, true)
        }

        return chooseValidTrack(query, candidateTracks)?.let { track ->
            val artistIds = track.artists.map { it.id }
            val artists = spotifyApi.artists.getArtists(*artistIds.toTypedArray())

            return MatchedScrobble(track, artists, query.time, query)
        }
    }

    private fun chooseValidTrack(query: ScrobbleQuery, tracks: List<Track>): Track? {
        // TODO: Make checking more robust
        val targetArtist = query.getMainArtist()
        tracks.forEach { track ->
            if (track.artists.map { it.name }.contains(targetArtist)) {
                return track
            }
        }
        return null
    }
}
