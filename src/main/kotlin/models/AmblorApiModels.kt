package models

import kotlinx.serialization.Serializable

@Serializable
data class Token(
    val access_token: String,
    val refresh_token: String,
    val expires_at: Int,
    val token_type: String
)

@Serializable
data class RefreshedToken(
    val access_token: String,
    val expires_at: Int
)

@Serializable
data class NewUser(
    val username: String,
    val firebase_token: String
)

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
)