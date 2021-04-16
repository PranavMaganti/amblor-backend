import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "1.4.31"
    kotlin("plugin.serialization") version "1.4.31"
    application
    id("com.diffplug.spotless") version "5.11.1"
}

group = "com.amblor"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    jcenter()
    maven { url = uri("https://dl.bintray.com/kotlin/kotlinx") }
    maven { url = uri("https://dl.bintray.com/kotlin/ktor") }
    maven { url = uri("https://dl.bintray.com/kotlin/kotlin-eap") }
}

dependencies {
    val ktorVersion = "1.5.3"
    val koinVersion = "3.0.1-beta-2"
    val jupiterVersion = "5.6.0"
    val exposedVersion = "0.30.1"

    implementation("io.ktor:ktor-server-netty:$ktorVersion")
    implementation("io.ktor:ktor-server-tests:$ktorVersion")
    implementation("io.ktor:ktor-serialization:$ktorVersion")
    implementation("io.ktor:ktor-auth:$ktorVersion")
    implementation("io.ktor:ktor-auth-jwt:$ktorVersion")
    implementation("ch.qos.logback:logback-classic:1.3.0-alpha5")

    implementation("org.jetbrains.kotlinx:kotlinx-serialization-core:1.0.1")

    implementation("com.adamratzman:spotify-api-kotlin-core:3.7.0")

    implementation("org.jetbrains.exposed:exposed-core:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-dao:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-jdbc:$exposedVersion")
    implementation("mysql:mysql-connector-java:8.0.23")
    implementation("com.zaxxer:HikariCP:4.0.3")
    implementation("com.google.cloud.sql:mysql-socket-factory-connector-j-8:1.2.2")

    implementation("com.google.firebase:firebase-admin:7.1.0")

    implementation("io.insert-koin:koin-core:$koinVersion")
    implementation("io.insert-koin:koin-ktor:$koinVersion")
    testImplementation("io.insert-koin:koin-test-junit5:$koinVersion")

    testImplementation(kotlin("test-junit5"))
    testImplementation("org.junit.jupiter:junit-jupiter-api:$jupiterVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$jupiterVersion")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.4.3")

}

tasks.withType<KotlinCompile>().all {
    kotlinOptions {
        freeCompilerArgs = listOf(
            "-Xopt-in=kotlin.Experimental",
            "-Xopt-in=kotlin.ExperimentalUnsignedTypes",
            "-Xopt-in=kotlinx.coroutines.ExperimentalCoroutinesApi"
        )
    }
}

allprojects {
    spotless {
        kotlin {
            target("**/*.kt")
            ktlint("0.41.0")
        }
    }

    tasks.withType<KotlinCompile>().all {
        kotlinOptions {
            freeCompilerArgs = freeCompilerArgs + listOf("-Xskip-prerelease-check")
            jvmTarget = "15"
        }
    }
}

tasks.test {
    useJUnitPlatform()
}

tasks.create("stage") {
    dependsOn("installDist")
}

application {
    mainModule.set("ServerKt")
    applicationDefaultJvmArgs = listOf("-Dio.ktor.development=true")
}
