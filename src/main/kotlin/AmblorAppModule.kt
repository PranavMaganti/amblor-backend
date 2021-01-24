import com.google.api.services.sql.model.Database
import db.DatabaseFactory
import db.DatabaseRepository
import org.koin.dsl.module

val amblorAppModule = module {
    single { DatabaseRepository() }
}