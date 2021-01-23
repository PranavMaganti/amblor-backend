package db

import org.jetbrains.exposed.dao.id.IntIdTable

object UserTable : IntIdTable("user", "user_id") {
    val username = varchar("username", 50)
    val email = varchar("email", 254)
}

object AlbumTable : IntIdTable("album", "album_id") {
    val name = varchar("name", 200)
    val image = varchar("image", 500)
    val spotifyId = varchar("spotify_id", 30)
}

object ArtistTable : IntIdTable("artist", "artist_id") {
    val name = varchar("name", 100)
    val image = varchar("image", 500)
    val genreSetId = reference("genre_id", GenreTable)
    val spotifyId = varchar("spotify_id", 30)
}

object ArtistSetTable : IntIdTable("artist_set", "artist_set_id") {
    val artistId = reference("artist_id", ArtistTable)
    val setId = integer("set_id")
}

object TrackTable : IntIdTable("track", "track_id") {
    val name = varchar("name", 200)
    val unmatchedName = varchar("unmatched_name", 200)
    val albumId = reference("album_id", AlbumTable)
    val spotifyId = varchar("spotify_id", 30)
    val preview = varchar("preview_url", 500)
    val artistSetId = integer("artist_set_id")
}

object ScrobbleTable : IntIdTable("scrobble", "scrobble_id") {
    val userId = reference("user_id", UserTable)
    val trackId = reference("track_id", TrackTable)
    @ExperimentalUnsignedTypes
    val time = uinteger("time")
}

object GenreTable : IntIdTable("genre", "genre_id") {
    val genres = varchar("genres", 200)
}