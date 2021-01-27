package models

import db.AlbumTable
import db.ArtistAliases
import db.ScrobbleTable
import db.TrackTable
import kotlinx.serialization.Serializable
import org.jetbrains.exposed.sql.ResultRow

@Serializable
data class NewUser(val username: String)

@Serializable
data class ScrobbleData(
    val time: Int = 0,
    val name: String = "",
    val preview_url: String = "",
    val album_name: String = "",
    val image: String = "",
    val artist_names: String = "",
    val artist_images: String = "",
    val artist_genres: String = ""
) {
    companion object {
        fun fromRowResult(rowResult: ResultRow, artistAliases: ArtistAliases): ScrobbleData {
            return ScrobbleData(
                rowResult[ScrobbleTable.time].toInt(),
                rowResult[TrackTable.name].toString(),
                rowResult[TrackTable.preview].toString(),
                rowResult[AlbumTable.name].toString(),
                rowResult[AlbumTable.image].toString(),
                rowResult[artistAliases.artistNames],
                rowResult[artistAliases.artistImages],
                rowResult[artistAliases.artistGenre]
            )
        }
    }
}

@Serializable
data class ScrobbleQuery(
    val track_name: String,
    val artist_name: String,
    val time: Int
) {
    fun getSpotifyQuery(): String = "track:${getCleanTitle()} artist:${getMainArtist()}"

    private fun getCleanTitle(): String {
        val cleanTitle = Regex("\\((feat|From).*\\)").replace(track_name, "").trim()
        val features = Regex("(feat|From)[^)]*").find(track_name)?.value?.replace("feat.", "")?.trim()

        return cleanTitle
    }

    private fun getMainArtist(): String = artist_name.split(Regex("[&,]"))[0].trim()
}
