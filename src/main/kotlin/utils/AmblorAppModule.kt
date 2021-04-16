
import db.DatabaseRepository
import org.koin.dsl.module

val amblorAppModule = module {
    single { DatabaseRepository() }
}
