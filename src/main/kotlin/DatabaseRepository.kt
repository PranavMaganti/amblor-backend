import DatabaseFactory.dbQuery
import io.ktor.application.call
import models.NewUser

class DatabaseRepository {
    suspend fun isUsernameTaken(username: String): Boolean = dbQuery {
        UserEntity.find { UserTable.username eq username }.count() == 1L
    }

    suspend fun addNewUser(newUsername: String, newEmail: String) = dbQuery {
        UserEntity.new {
            username = newUsername
            email = newEmail
        }
    }

    suspend fun isEmailRegistered(email: String): Boolean = dbQuery {
        UserEntity.find { UserTable.email eq email }.count() == 1L
    }
}