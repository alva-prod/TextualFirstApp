import sys
import os

if getattr(sys, 'frozen', False):
    # Ensure streams exist
    if sys.stdin is None or not hasattr(sys.stdin, 'fileno'):
        sys.stdin = open(os.devnull, 'r')
    if sys.stdout is None or not hasattr(sys.stdout, 'fileno'):
        sys.stdout = open(os.devnull, 'w') 
    if sys.stderr is None or not hasattr(sys.stderr, 'fileno'):
        sys.stderr = open(os.devnull, 'w')


from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, HorizontalGroup, Vertical
from textual.widgets import Button, Footer, Header, Static, Input
import func as fu

class WeatherWidget(Vertical):
    def __init__(self, city: str, lat: float, lon: float):
        super().__init__()
        self.city = city
        self.lat = lat
        self.lon = lon

    def compose(self) -> ComposeResult:
        # Left side content
        with Vertical():
            yield Static(f"{self.city}", id="city-title")
            yield Static("Loading...", id="weather-info")
        # Right side button
        yield Button("✕", id="remove", variant="error")
    
    def on_mount(self) -> None:
        # Fetch weather data when widget mounts
        weather_text = fu.weatherGetter(self.lat, self.lon)
        self.query_one("#weather-info").update(weather_text) # pyright: ignore

class WeatherApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_weather", "Add City"),
        ("r", "remove_weather", "Remove Last"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        self.weather_container = VerticalScroll(id="weather-timers")
        yield self.weather_container

    def on_mount(self) -> None:
        # Add Monterrey by default
        lat, lon = fu.coordFinder(None)
        if lat is not None and lon is not None:
            self.weather_container.mount(WeatherWidget("Monterrey, Nuevo Leon", lat, lon))

    def action_add_weather(self) -> None:
        self.push_screen(CityPromptScreen(self.weather_container))

    def action_remove_weather(self) -> None:
        widgets = self.weather_container.query("WeatherWidget")
        if widgets:
            widgets.last().remove()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

from textual.screen import Screen

class CityPromptScreen(Screen):
    def __init__(self, container):
        super().__init__()
        self.container = container

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Enter city name:")
        self.input = Input(placeholder="City,Region", id="city-input")
        yield self.input
        yield Button("Add", id="add", variant="success")
        yield Button("Cancel", id="cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            city = self.input.value.strip()
            lat, lon = fu.coordFinder(city)
            if lat is not None and lon is not None:
                self.container.mount(WeatherWidget(city, lat, lon))
                self.app.pop_screen()
            else:
                self.input.placeholder = "City not found, try again"
                self.input.value = ""
        elif event.button.id == "cancel":
            self.app.pop_screen()

if __name__ == "__main__":
    app = WeatherApp()
    app.run()
