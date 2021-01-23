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
        val spotifyApiBuilder = spotifyAppApi(clientId, clientSecret)
        spotifyApi = spotifyApiBuilder.build()
    }

    suspend fun matchTrack(query: ScrobbleQuery): MatchedScrobble? {
        val spotifyQuery = query.getSpotifyQuery()
        val candidateTracks = spotifyApi.search.searchTrack(spotifyQuery, limit = 3).items

        if (candidateTracks.isEmpty()) return null

        val track = chooseValidTrack(query, candidateTracks)
        val artistIds = track.artists.map { it.id }
        val artists = spotifyApi.artists.getArtists(*artistIds.toTypedArray())

        return MatchedScrobble(track, artists, query.time, query)
    }

    private fun chooseValidTrack(query: ScrobbleQuery, tracks: List<Track>): Track {
        // TODO: Add proper checking
        return tracks[0]
    }
}

