package models

import kotlinx.serialization.Serializable

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
)

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