plugins {
    id("com.android.application")
    kotlin("android")
    id("kotlin-android-extensions")
}
group = "com.vanpra"
version = "1.0-SNAPSHOT"

repositories {
    gradlePluginPortal()
    google()
    jcenter()
    mavenCentral()
    maven {
        url = uri("https://dl.bintray.com/kotlin/kotlin-eap")
    }
    maven { url = uri("https://androidx.dev/snapshots/builds/6656359/artifacts/ui/repository") }
}

android {
    compileSdkVersion(30)
    defaultConfig {
        applicationId = "com.vanpra.scrobbler"
        minSdkVersion(24)
        targetSdkVersion(30)
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }

    kotlinOptions { jvmTarget = "1.8" }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerVersion = "1.3.70-dev-withExperimentalGoogleExtensions-20200424"
        kotlinCompilerExtensionVersion = "0.1.0-dev14"
    }
}

dependencies {
    val composeVersion = "0.1.0-dev14"

    implementation("com.google.android.material:material:1.1.0")

    implementation("androidx.ui:ui-tooling:$composeVersion")
    implementation("androidx.ui:ui-layout:$composeVersion")
    implementation("androidx.ui:ui-foundation:$composeVersion")
    implementation("androidx.ui:ui-material:$composeVersion")
    implementation("androidx.ui:ui-material-icons-extended:$composeVersion")
    implementation("androidx.compose:compose-runtime:$composeVersion")

    implementation(project(":shared"))
    implementation("androidx.core:core-ktx:1.3.0")
    implementation("androidx.appcompat:appcompat:1.1.0")
    implementation(kotlin("stdlib-jdk7"))
}
