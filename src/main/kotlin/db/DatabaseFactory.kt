package db

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.SchemaUtils
import org.jetbrains.exposed.sql.transactions.experimental.newSuspendedTransaction
import org.jetbrains.exposed.sql.transactions.transaction

object DatabaseFactory {
    private val CLOUD_SQL_CONNECTION_NAME = System.getenv("CLOUD_SQL_CONNECTION_NAME")

    fun init() {
        Database.connect(hikari())
        transaction {
            SchemaUtils.create(
                UserTable,
                AlbumTable,
                ArtistTable,
                ArtistSetTable,
                TrackTable,
                ScrobbleTable,
                GenreTable
            )
        }
    }

    private fun hikari(): HikariDataSource {
        val config = HikariConfig()
        config.driverClassName = "com.mysql.cj.jdbc.Driver"
        config.jdbcUrl = "jdbc:mysql://35.246.27.64:3306/amblor"
        config.username = System.getenv("MYSQL_USERNAME")
        config.password = System.getenv("MYSQL_PASSWORD")
        config.maximumPoolSize = 10
        config.isAutoCommit = false
        config.transactionIsolation = "TRANSACTION_REPEATABLE_READ"

        config.addDataSourceProperty("socketFactory", "com.google.cloud.sql.mysql.SocketFactory")
        config.addDataSourceProperty("cloudSqlInstance", CLOUD_SQL_CONNECTION_NAME)

        config.validate()
        return HikariDataSource(config)
    }

    suspend fun <T> dbQuery(
        block: suspend () -> T
    ): T =
        newSuspendedTransaction { block() }
}