package db

import MatchedScrobble
import SpotifyRepository
import com.adamratzman.spotify.models.Artist
import com.adamratzman.spotify.models.SimpleAlbum
import com.adamratzman.spotify.models.Track
import db.DatabaseFactory.dbQuery
import models.ScrobbleQuery
import org.jetbrains.exposed.dao.id.EntityID
import org.jetbrains.exposed.sql.SortOrder

class DatabaseRepository {

    init {
        DatabaseFactory.init()
    }

    suspend fun isUsernameTaken(username: String): Boolean = dbQuery {
        UserEntity.find { UserTable.username eq username }.count() == 1L
    }

    suspend fun addNewUser(newUsername: String, newEmail: String) = dbQuery {
        UserEntity.new {
            username_ = newUsername
            email_ = newEmail
        }
    }

    suspend fun isEmailRegistered(email: String): Boolean = dbQuery {
        UserEntity.find { UserTable.email eq email }.count() == 1L
    }

    private suspend fun getUserIdWithEmail(email: String) = dbQuery {
        UserEntity.find { UserTable.email eq email }.first().id
    }

    @ExperimentalUnsignedTypes
    suspend fun insertScrobble(scrobble: MatchedScrobble, email: String) = dbQuery {
        val dbTrack = TrackEntity.find { TrackTable.spotifyId eq scrobble.track.id }.limit(1)

        val insertedTrackId = if (dbTrack.empty()) {
            val albumId = insertAlbum(scrobble.track.album)
            val artistIds = scrobble.artists.map { insertArtist(it!!) }
            val artistSetId = insertArtistSet(artistIds)
            insertTrack(scrobble.track, artistSetId, albumId, scrobble.query.track_name)
        } else {
            dbTrack.first().id
        }

        val userId = getUserIdWithEmail(email)
        insertScrobble(insertedTrackId, userId, scrobble.query.time)
    }

    @ExperimentalUnsignedTypes
    private suspend fun insertScrobble(trackId: EntityID<Int>, userId: EntityID<Int>, time: Int) = dbQuery {
        ScrobbleEntity.new {
            userId_ = userId
            trackId_ = trackId
            time_ = time.toUInt()
        }
    }

    private suspend fun insertArtist(artist: Artist): EntityID<Int> = dbQuery {
        val dbArtist = ArtistEntity.find { ArtistTable.spotifyId eq artist.id }.limit(1)
        if (!dbArtist.empty()) {
            // Spotify id's are unique
            return@dbQuery dbArtist.first().id
        }

        val genreId = GenreSetEntity.new { genres_ = artist.genres.joinToString(",") }.id
        ArtistEntity.new {
            name_ = artist.name
            image_ = artist.images.last().url
            genreId_ = genreId
            spotifyId_ = artist.id
        }.id
    }

    private suspend fun insertAlbum(album: SimpleAlbum): EntityID<Int> = dbQuery {
        val dbAlbum = AlbumEntity.find { AlbumTable.spotifyId eq album.id }.limit(1)
        if (!dbAlbum.empty()) {
            // Spotify id's are unique
            return@dbQuery dbAlbum.first().id
        }

        AlbumEntity.new {
            name_ = album.name
            image_ = album.images.last().url
            spotifyId_ = album.id
        }.id
    }

    private suspend fun insertArtistSet(artistIds: List<EntityID<Int>>): Int = dbQuery {
        val item = ArtistSetEntity.all().orderBy(ArtistSetTable.setId to SortOrder.DESC).limit(1)
        val artistSetId = if (item.empty()) 1 else item.first().setId_ + 1

        artistIds.forEach { id ->
            ArtistSetEntity.new {
                artistId_ = id
                setId_ = artistSetId
            }
        }

        return@dbQuery artistSetId
    }

    private suspend fun insertTrack(
        track: Track,
        artistSetId: Int,
        albumId: EntityID<Int>,
        queryName: String
    ) =
        dbQuery {
            TrackEntity.new {
                name_ = track.name
                unmatchedName_ = queryName
                albumId_ = albumId
                spotifyId_ = track.id
                preview_ = track.previewUrl ?: ""
                artistSetId_ = artistSetId
            }.id
        }
}

@ExperimentalUnsignedTypes
suspend fun main() {
    val db = DatabaseRepository()
    SpotifyRepository.init()

    // db.addNewUser("vanpra", "pranav.maganti@gmail.com")

    val track = SpotifyRepository.matchTrack(
        ScrobbleQuery(
            "If the World Was Ending (feat. Julia Michaels)",
            "JP Saxe & Julia Michaels",
            1010010
        )
    )
    db.insertScrobble(track!!, "pranav.maganti@gmail.com")
}