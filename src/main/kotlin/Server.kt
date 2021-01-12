import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseAuthException
import com.google.firebase.auth.FirebaseToken
import io.ktor.application.Application
import io.ktor.application.call
import io.ktor.application.install
import io.ktor.features.ContentNegotiation
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.request.authorization
import io.ktor.request.receive
import io.ktor.request.receiveText
import io.ktor.response.respond
import io.ktor.response.respondText
import io.ktor.routing.Route
import io.ktor.routing.head
import io.ktor.routing.post
import io.ktor.routing.route
import io.ktor.routing.routing
import io.ktor.serialization.json
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.util.KtorExperimentalAPI
import models.NewUser
import com.google.auth.oauth2.GoogleCredentials

import com.google.firebase.FirebaseOptions

@KtorExperimentalAPI
fun main(args: Array<String>) {
    val port = System.getenv("PORT")?.toInt() ?: 23567
    embeddedServer(
        Netty, watchPaths = listOf(), port = port,
        module = Application::mainModule
    ).start(true)
}

@KtorExperimentalAPI
fun Application.mainModule() {
    DatabaseFactory.init()

    install(ContentNegotiation) {
        json()
    }

    routing {
        route("/users") {
            users()
        }
    }
}

fun Route.users() {
    val dbRepository = DatabaseRepository()

    val options = FirebaseOptions.builder()
        .setCredentials(GoogleCredentials.getApplicationDefault())
        .build()
    FirebaseApp.initializeApp(options);

    post {
        val userData = call.receive<NewUser>()

        if (dbRepository.isUsernameTaken(userData.username)) {
            call.respond(HttpStatusCode.Conflict)
            return@post
        }

        try {
            val decodedToken = FirebaseAuth.getInstance().verifyIdToken(userData.firebase_token)
            dbRepository.addNewUser(userData.username, decodedToken.email)
            call.respond(HttpStatusCode.OK)
        } catch (e: FirebaseAuthException) {
            call.respond(HttpStatusCode.Unauthorized)
        }
    }

    head("{username}") {
        if (dbRepository.isUsernameTaken(call.parameters["username"]!!)) {
            call.respond(HttpStatusCode.OK)
        } else {
            call.respond(HttpStatusCode.NotFound)
        }
    }

    head("/users") {
        val userData = call.receive<NewUser>()

        try {
            val decodedToken = FirebaseAuth.getInstance().verifyIdToken(userData.firebase_token)
            if (dbRepository.isEmailRegistered(decodedToken.email)) {
                call.respond(HttpStatusCode.OK)
            } else {
                call.respond(HttpStatusCode.NotFound)
            }
        } catch (e: FirebaseAuthException) {
            call.respond(HttpStatusCode.Unauthorized)
        }
    }
}
































