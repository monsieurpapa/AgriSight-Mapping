import reflex as rx
import reflex_enterprise as rxe
from app.components.map_view import map_view
from app.components.sidebar import sidebar
from app.pages.producer_page import producer_page
from app.pages.admin_page import admin_page


def index() -> rx.Component:
    """The main dashboard page."""
    return rx.el.div(
        sidebar(),
        rx.el.main(map_view(), class_name="flex-1 h-screen p-4 bg-gray-50"),
        class_name="flex h-screen w-screen font-['Inter'] bg-gray-50",
    )


app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
            integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=",
            cross_origin="",
        ),
    ],
)
app.add_page(index)
app.add_page(producer_page, route="/producers/[producer_id]")
app.add_page(admin_page, route="/admin")