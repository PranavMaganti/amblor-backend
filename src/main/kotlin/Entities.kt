import org.jetbrains.exposed.dao.IntEntity
import org.jetbrains.exposed.dao.IntEntityClass
import org.jetbrains.exposed.dao.id.EntityID

class UserEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<UserEntity>(UserTable)

    var username by UserTable.username
    var email by UserTable.email
}

class AlbumEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<AlbumEntity>(AlbumTable)

    var name by AlbumTable.name
    var image by AlbumTable.image
    var spotifyId by AlbumTable.spotifyId
}

class ArtistEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<ArtistEntity>(ArtistTable)

    var name by ArtistTable.name
    var image by ArtistTable.image
    var genreSetId by ArtistTable.genreSetId
    var spotifyId by ArtistTable.spotifyId
}


class ArtistSetEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<ArtistSetEntity>(ArtistSetTable)

    var artistId by ArtistSetTable.artistId
    var setId by ArtistSetTable.setId
}

class TrackEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<TrackEntity>(TrackTable)

    var name by TrackTable.name
    var unmatchedName by TrackTable.unmatchedName
    var albumId by TrackTable.albumId
    var spotifyId by TrackTable.spotifyId
    var preview by TrackTable.preview
    var artistSetId by TrackTable.artistSetId
}

class ScrobbleEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<ScrobbleEntity>(ScrobbleTable)

    var userId by ScrobbleTable.userId
    var trackId by ScrobbleTable.trackId
    @ExperimentalUnsignedTypes
    var time by ScrobbleTable.time
}

class GenreSetEntity(id: EntityID<Int>) : IntEntity(id) {
    companion object : IntEntityClass<GenreSetEntity>(GenreSetTable)

    var genreName by GenreSetTable.genreName
    var setId by GenreSetTable.setId
}

