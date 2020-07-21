package com.vanpra.scrobbler

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.Composable
import androidx.compose.getValue
import androidx.compose.remember
import androidx.compose.setValue
import androidx.ui.core.Modifier
import androidx.ui.core.setContent
import androidx.ui.foundation.ContentColorAmbient
import androidx.ui.foundation.Image
import androidx.ui.foundation.Text
import androidx.ui.foundation.drawBackground
import androidx.ui.graphics.Color
import androidx.ui.graphics.ColorFilter
import androidx.ui.graphics.vector.VectorAsset
import androidx.ui.layout.ConstraintLayout
import androidx.ui.layout.Dimension
import androidx.ui.layout.fillMaxSize
import androidx.ui.material.BottomNavigation
import androidx.ui.material.BottomNavigationItem
import androidx.ui.material.MaterialTheme
import androidx.ui.material.icons.Icons
import androidx.ui.material.icons.filled.Album
import androidx.ui.material.icons.filled.BarChart
import androidx.ui.material.icons.filled.Home
import androidx.ui.savedinstancestate.savedInstanceState
import androidx.ui.text.font.FontWeight
import androidx.ui.unit.dp
import androidx.ui.unit.sp
import com.vanpra.scrobbler.ui.ScrobblerTheme

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ScrobblerTheme {
                ConstraintLayout(
                    Modifier
                        .fillMaxSize()
                        .drawBackground(MaterialTheme.colors.background)
                ) {
                    val (title, bottomNav) = createRefs()
                    ScrobblerTitle(Modifier.constrainAs(title) {
                        top.linkTo(parent.top, 8.dp)
                        centerHorizontallyTo(parent)
                    })

                    ScrobblerNavigation(Modifier.constrainAs(bottomNav) {
                        bottom.linkTo(parent.bottom)
                        linkTo(parent.start, parent.end)
                        width = Dimension.fillToConstraints
                    })
                }
            }
        }
    }
}

@Composable
fun ScrobblerTitle(modifier: Modifier = Modifier) {
    Text(
        "Scrobbler",
        color = MaterialTheme.colors.onBackground,
        fontSize = 20.sp,
        fontWeight = FontWeight.W700,
        modifier = modifier
    )
}

data class NavigationItem(val name: String, val icon: VectorAsset)

@Composable
fun ScrobblerNavigation(modifier: Modifier = Modifier) {
    var selectedIndex by savedInstanceState { 0 }
    val items = remember {
        listOf(
            NavigationItem("Home", Icons.Default.Home),
            NavigationItem("Scrobbles", Icons.Default.Album),
            NavigationItem("Stats", Icons.Default.BarChart)
        )
    }

    BottomNavigation(modifier) {
        items.forEachIndexed { index, it ->
            BottomNavigationItem(
                modifier = Modifier.drawBackground(MaterialTheme.colors.background),
                icon = { Image(it.icon, colorFilter = ColorFilter.tint(ContentColorAmbient.current)) },
                text = { Text(it.name, color = ContentColorAmbient.current) },
                alwaysShowLabels = false,
                selected = index == selectedIndex,
                onSelected = { selectedIndex = index },
                activeColor = MaterialTheme.colors.primaryVariant,
                inactiveColor = Color.Gray
            )
        }
    }
}
