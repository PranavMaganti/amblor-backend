package db

import org.jetbrains.exposed.dao.IntEntity
import org.jetbrains.exposed.dao.IntEntityClass
import org.jetbrains.exposed.dao.id.EntityID

class UserEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<UserEntity>(UserTable)

    var username_ by UserTable.username
    var email_ by UserTable.email
}

class AlbumEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<AlbumEntity>(AlbumTable)

    var name_ by AlbumTable.name
    var image_ by AlbumTable.image
    var spotifyId_ by AlbumTable.spotifyId
}

class ArtistEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<ArtistEntity>(ArtistTable)

    var name_ by ArtistTable.name
    var image_ by ArtistTable.image
    var genreId_ by ArtistTable.genreSetId
    var spotifyId_ by ArtistTable.spotifyId
}


class ArtistSetEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<ArtistSetEntity>(ArtistSetTable)

    var artistId_ by ArtistSetTable.artistId
    var setId_ by ArtistSetTable.setId
}

class TrackEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<TrackEntity>(TrackTable)

    var name_ by TrackTable.name
    var unmatchedName_ by TrackTable.unmatchedName
    var albumId_ by TrackTable.albumId
    var spotifyId_ by TrackTable.spotifyId
    var preview_ by TrackTable.preview
    var artistSetId_ by TrackTable.artistSetId
}

class ScrobbleEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<ScrobbleEntity>(ScrobbleTable)

    var userId_ by ScrobbleTable.userId
    var trackId_ by ScrobbleTable.trackId
    @ExperimentalUnsignedTypes
    var time_ by ScrobbleTable.time
}

class GenreSetEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<GenreSetEntity>(GenreTable)
    var genres_ by GenreTable.genres
}

