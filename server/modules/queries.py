insert_album = "INSERT INTO Album (name, image, spotify_id) VALUES ('%s', '%s', '%s')"
insert_genre_set = "INSERT INTO GenreSet (genre_name, set_id) VALUES ('%s', %i)"
insert_artist = "INSERT INTO Artist (name, genre_set_id, image, spotify_id) VALUES ('%s', %i, '%s', '%s')"
insert_artist_set = "INSERT INTO ArtistSet (artist_id, set_id) VALUES (%i, %i)"
insert_track = "INSERT INTO Track (artist_set_id, name, unmatched_name, album_id, spotify_id, preview_url) VALUES (%i, '%s', '%s', %i, '%s', '%s')"
insert_scrobble_entry = (
    "INSERT INTO Scrobble (user_id, track_id, time) VALUES (%i, %i, %i)"
)

get_album = "SELECT * FROM Album WHERE Album.spotify_id='%s'"
get_artist = "SELECT * FROM Artist WHERE Artist.spotify_id='%s'"
get_last_genre_set = "SELECT * FROM GenreSet ORDER BY set_id DESC LIMIT 1"
get_last_artist_set = "SELECT * FROM ArtistSet ORDER BY set_id DESC LIMIT 1"
