import com.auth0.jwk.JwkProviderBuilder
import com.auth0.jwt.interfaces.Payload
import db.DatabaseFactory
import db.DatabaseRepository
import io.ktor.application.Application
import io.ktor.application.call
import io.ktor.application.install
import io.ktor.auth.Authentication
import io.ktor.auth.authenticate
import io.ktor.auth.jwt.JWTPrincipal
import io.ktor.auth.jwt.jwt
import io.ktor.auth.principal
import io.ktor.features.ContentNegotiation
import io.ktor.http.HttpStatusCode
import io.ktor.request.receive
import io.ktor.response.respond
import io.ktor.routing.Route
import io.ktor.routing.head
import io.ktor.routing.post
import io.ktor.routing.route
import io.ktor.routing.routing
import io.ktor.serialization.json
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.util.KtorExperimentalAPI
import kotlinx.coroutines.runBlocking
import models.NewUser
import models.ScrobbleQuery
import org.koin.dsl.module
import org.koin.ktor.ext.Koin
import org.koin.ktor.ext.inject
import java.net.URL
import java.time.Instant
import java.util.Date

@KtorExperimentalAPI
fun main(args: Array<String>) {
    embeddedServer(
        Netty, watchPaths = listOf(), port = System.getenv("PORT")?.toInt() ?: 8080,
        module = Application::mainModule
    ).start(true)
}

@KtorExperimentalAPI
fun Application.mainModule() {
    DatabaseFactory.init()
    runBlocking {
        SpotifyRepository.init()
    }

    install(ContentNegotiation) {
        json()
    }

//    install(CallLogging) {
//        level = Level.ERROR
//    }

    install(Koin) {
        modules(amblorAppModule)
    }

    val jwkIssuer = URL("https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com")
    val jwtIssuer = "https://securetoken.google.com/amblor"
    val jwkProvider = JwkProviderBuilder(jwkIssuer).build()

    install(Authentication) {
        jwt(name = "main") {
            verifier(jwkProvider, jwtIssuer)
            validate { credentials ->
                val now = Date.from(Instant.now())
                val exp = credentials.payload.expiresAt
                val aud = credentials.payload.audience
                val iat = credentials.payload.issuedAt
                val sub = credentials.payload.subject
                val authTime = credentials.payload.getClaim("auth_time").asDate()

                if (exp.after(now) && aud == listOf("amblor") && iat.before(now) && sub.isNotEmpty() &&
                    authTime.before(now)
                ) {
                    JWTPrincipal(credentials.payload)
                } else {
                    null
                }
            }
        }
    }

    routing {
        route("/api/v1") {
            authenticate("main") {
                route("/users") { users() }
                route("/scrobble") { scrobble() }
            }
        }
    }
}

fun Payload.getEmail(): String = this.getClaim("email").asString()

fun Route.scrobble() {
    val dbRepository by inject<DatabaseRepository>()

    post {
        val payload: Payload = call.principal<JWTPrincipal>()!!.payload
        val scrobbleQuery = call.receive<ScrobbleQuery>()
        SpotifyRepository.matchTrack(scrobbleQuery)?.let {
            val scrobble = dbRepository.insertScrobble(it, payload.getEmail())
            call.respond(HttpStatusCode.OK, scrobble)
        } ?: run {
            println("Can't match song: ${scrobbleQuery.track_name} - ${scrobbleQuery.artist_name}")
            call.respond(HttpStatusCode.BadRequest)
        }
    }
}

fun Route.users() {
    val dbRepository by inject<DatabaseRepository>()

    post {
        val userData = call.receive<NewUser>()
        val payload = call.principal<JWTPrincipal>()!!.payload

        if (dbRepository.isUsernameTaken(userData.username)) {
            call.respond(HttpStatusCode.Conflict)
            return@post
        }

        dbRepository.addNewUser(userData.username, payload.getEmail())
        call.respond(HttpStatusCode.OK)
    }

    head("{username}") {
        if (dbRepository.isUsernameTaken(call.parameters["username"]!!)) {
            call.respond(HttpStatusCode.OK)
        } else {
            call.respond(HttpStatusCode.NotFound)
        }
    }

    head {
        val payload = call.principal<JWTPrincipal>()!!.payload

        if (dbRepository.isEmailRegistered(payload.getEmail())) {
            call.respond(HttpStatusCode.OK)
        } else {
            call.respond(HttpStatusCode.NotFound)
        }
    }
}
