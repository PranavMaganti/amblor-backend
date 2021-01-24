import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "1.4.21"
    kotlin("plugin.serialization") version "1.4.21"
    id("org.jmailen.kotlinter") version "3.3.0"
    application
}

group = "com.amblor"
version = "1.0-SNAPSHOT"

repositories {
    jcenter()
    mavenCentral()
    maven { url = uri("https://dl.bintray.com/kotlin/kotlinx") }
    maven { url = uri("https://dl.bintray.com/kotlin/ktor") }
    maven("https://kotlin.bintray.com/kotlinx/")
}

dependencies {
    val ktorVersion = "1.5.0"
    val koinVersion = "2.2.2"
    val jupiterVersion = "5.6.0"
    val exposedVersion = "0.28.1"

    implementation("io.ktor:ktor-server-netty:$ktorVersion")
    implementation("io.ktor:ktor-server-tests:$ktorVersion")
    implementation("io.ktor:ktor-html-builder:$ktorVersion")
    implementation("io.ktor:ktor-serialization:$ktorVersion")
    implementation("io.ktor:ktor-auth:$ktorVersion")
    implementation("io.ktor:ktor-auth-jwt:$ktorVersion")
    implementation("ch.qos.logback:logback-classic:1.3.0-alpha5")

    implementation("org.jetbrains.kotlinx:kotlinx-html-jvm:0.7.2")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-core:1.0.1")

    implementation("com.adamratzman:spotify-api-kotlin-core:3.4.03")

    implementation("org.jetbrains.exposed:exposed-core:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-dao:$exposedVersion")
    implementation("org.jetbrains.exposed:exposed-jdbc:$exposedVersion")
    implementation("mysql:mysql-connector-java:8.0.22")
    implementation("com.zaxxer:HikariCP:3.4.5")
    implementation("com.google.cloud.sql:mysql-socket-factory-connector-j-8:1.2.0")

    implementation("com.google.firebase:firebase-admin:7.1.0")

    implementation("org.koin:koin-core:$koinVersion")
    implementation("org.koin:koin-ktor:$koinVersion")
    testImplementation("org.koin:koin-test:$koinVersion")

    testImplementation(kotlin("test-junit5"))
    testImplementation("org.junit.jupiter:junit-jupiter-api:$jupiterVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:$jupiterVersion")
}

tasks.withType<KotlinCompile>().all {
    kotlinOptions {
        freeCompilerArgs = listOf(
            "-Xopt-in=kotlin.Experimental",
            "-Xopt-in=kotlin.ExperimentalUnsignedTypes"
        )
    }
}

tasks.test {
    useJUnitPlatform()
}

tasks.create("stage") {
    dependsOn("installDist")
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "15"
}

application {
    mainClassName = "ServerKt"
}