import reflex as rx
import reflex_enterprise as rxe
from app.states.map_state import MapState, Field, PointOfInterest


def map_view() -> rx.Component:
    """The map view component for the dashboard."""


def field_polygon(field: Field) -> rx.Component:
    is_selected = MapState.selected_field_id == field["id"]
    map_api = rxe.map.api("traceability-map")
    return rxe.map.polygon(
        rxe.map.tooltip(
            f"Producer: {field['farmer_name']}\nCrop: {field['crop']} | Area: {field['area']} ha"
        ),
        positions=field["polygon"],
        path_options=rxe.map.path_options(
            color=rx.cond(is_selected, "#F3340B", "#2B79D1"),
            fill_color=rx.cond(is_selected, "#F97A58", "#5595e0"),
            fill_opacity=rx.cond(is_selected, 0.8, 0.6),
            weight=rx.cond(is_selected, 3, 2),
        ),
        on_click=[
            MapState.select_field(field["id"]),
            MapState.go_to_producer_page(field["farmer_id"]),
        ],
    )


def map_view() -> rx.Component:
    """The map view component for the dashboard."""
    return rxe.map(
        rxe.map.tile_layer(
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        ),
        rx.cond(
            MapState.show_fields,
            rx.foreach(MapState.filtered_fields, field_polygon),
            None,
        ),
        rx.cond(
            MapState.show_pois,
            rx.foreach(
                MapState.points_of_interest,
                lambda poi: rxe.map.marker(
                    rxe.map.tooltip(f"{poi['type']}: {poi['name']}"),
                    position=poi["location"],
                ),
            ),
            None,
        ),
        rxe.map.zoom_control(position="topright"),
        rxe.map.scale_control(position="bottomleft"),
        id="traceability-map",
        center=MapState.center,
        zoom=MapState.zoom,
        height="100%",
        width="100%",
        zoom_control=False,
        class_name="rounded-lg shadow-md border border-gray-200",
    )