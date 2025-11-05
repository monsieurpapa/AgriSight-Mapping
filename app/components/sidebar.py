import reflex as rx
from app.states.map_state import MapState
from app.states.traceability_state import TraceabilityState
import reflex_enterprise as rxe
from app.states.map_state import MapState, Field
from app.states.auth_state import AuthState, User
from app.components.analytics_view import analytics_view
from app.components.traceability_view import traceability_view


def stat_card(icon: str, label: str, value: rx.Var[str | int]) -> rx.Component:
    """A card for displaying a single statistic."""
    return rx.el.div(
        rx.icon(icon, class_name="h-6 w-6 text-gray-400"),
        rx.el.div(
            rx.el.p(value, class_name="text-lg font-bold text-gray-800"),
            rx.el.p(label, class_name="text-xs text-gray-500"),
            class_name="leading-tight",
        ),
        class_name="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200",
    )


def layer_toggle(
    text: str,
    icon_name: str,
    state_var: rx.Var[bool],
    on_change_event: rx.event.EventType,
) -> rx.Component:
    """A reusable toggle switch for map layers."""
    unique_id = f"toggle-{text.lower().replace(' ', '-')}"
    return rx.el.label(
        rx.el.div(
            rx.icon(icon_name, class_name="h-5 w-5 text-gray-500"),
            rx.el.span(text, class_name="text-sm font-medium text-gray-700"),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.input(
                type="checkbox",
                id=unique_id,
                class_name="sr-only peer",
                checked=state_var,
                on_change=on_change_event,
            ),
            rx.el.div(
                class_name="relative w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
            ),
            class_name="relative",
        ),
        class_name="flex items-center justify-between w-full p-3 rounded-lg hover:bg-gray-100 cursor-pointer",
        html_for=unique_id,
    )


def field_list_item(field: Field) -> rx.Component:
    is_selected = MapState.selected_field_id == field["id"]
    map_api = rxe.map.api("traceability-map")
    return rx.el.button(
        rx.el.div(
            rx.icon("bar-chart-big", class_name="h-5 w-5 text-blue-500"),
            rx.el.div(
                rx.el.p(field["farmer_name"], class_name="font-semibold text-gray-800"),
                rx.el.p(
                    f"{field['crop']} - {field['area']} ha", class_name="text-gray-500"
                ),
                class_name="flex-1 text-sm text-left leading-tight",
            ),
            class_name="flex items-center gap-3",
        ),
        class_name=rx.cond(
            is_selected,
            "w-full p-3 rounded-lg text-left transition-colors bg-blue-100 border-l-4 border-blue-500",
            "w-full p-3 rounded-lg text-left transition-colors hover:bg-gray-100",
        ),
        on_click=[
            MapState.select_field(field["id"]),
            map_api.fly_to(field["polygon"][0], 14.0),
            MapState.go_to_producer_page(field["farmer_id"]),
        ],
    )


def sidebar() -> rx.Component:
    """The sidebar component for map controls."""
    return rx.el.aside(
        rx.el.div(
            rx.icon("map", class_name="h-8 w-8 text-blue-600"),
            rx.el.h1(
                "AgriTrace", class_name="text-xl font-bold text-gray-800 tracking-tight"
            ),
            class_name="flex items-center gap-3 p-4 border-b border-gray-200 shrink-0",
        ),
        rx.el.div(
            rx.el.div(
                stat_card(
                    "scan-search", "Total Area (ha)", MapState.total_area.to_string()
                ),
                stat_card("tractor", "Total Fields", MapState.total_fields.to_string()),
                class_name="grid grid-cols-2 gap-3 p-3 border-b border-gray-200 shrink-0",
            ),
            rx.el.div(
                rx.el.h2(
                    "Map Controls",
                    class_name="px-4 pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                ),
                rx.el.div(
                    layer_toggle(
                        "Fields",
                        "bar-chart-big",
                        MapState.show_fields,
                        MapState.toggle_fields,
                    ),
                    layer_toggle(
                        "Points of Interest",
                        "building-2",
                        MapState.show_pois,
                        MapState.toggle_pois,
                    ),
                    class_name="flex flex-col gap-1 p-2",
                ),
                class_name="shrink-0 border-b border-gray-200",
            ),
            rx.el.div(
                rx.el.h2(
                    "Field Directory",
                    class_name="px-4 pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Search Farmer or Crop...",
                        on_change=MapState.set_search_query,
                        class_name="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-300 outline-none",
                    ),
                    class_name="px-3 pb-2",
                ),
                rx.el.div(
                    rx.foreach(MapState.filtered_fields, field_list_item),
                    class_name="flex flex-col gap-1 px-2 pb-4",
                ),
                class_name="flex flex-col",
            ),
            analytics_view(),
            traceability_view(),
            class_name="flex-1 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon("download", class_name="h-4 w-4 mr-2"),
                    "Export CSV",
                    on_click=TraceabilityState.export_fields_csv,
                    class_name="flex items-center text-xs font-medium text-gray-600 hover:text-blue-600 p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors",
                ),
                rx.el.button(
                    rx.icon("file-json-2", class_name="h-4 w-4 mr-2"),
                    "Export JSON",
                    on_click=TraceabilityState.export_fields_json,
                    class_name="flex items-center text-xs font-medium text-gray-600 hover:text-blue-600 p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors",
                ),
                class_name="grid grid-cols-2 gap-2 p-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Switch User (Demo)",
                        class_name="text-xs font-medium text-gray-500",
                    ),
                    rx.el.select(
                        rx.foreach(
                            AuthState.users,
                            lambda user: rx.el.option(user["name"], value=user["id"]),
                        ),
                        value=AuthState.current_user_id,
                        on_change=AuthState.login_as,
                        class_name="w-full text-xs p-1 border border-gray-200 rounded-md",
                    ),
                    class_name="px-2 pb-2",
                ),
                rx.el.div(
                    rx.image(
                        src=rx.cond(
                            AuthState.current_user,
                            f"https://api.dicebear.com/9.x/notionists/svg?seed={AuthState.current_user['email']}",
                            "",
                        ),
                        class_name="size-10 rounded-full",
                    ),
                    rx.el.div(
                        rx.el.p(
                            rx.cond(
                                AuthState.current_user,
                                AuthState.current_user["name"],
                                "",
                            ),
                            class_name="text-sm font-semibold text-gray-800",
                        ),
                        rx.el.p(
                            rx.cond(
                                AuthState.current_user,
                                AuthState.current_user["email"],
                                "",
                            ),
                            class_name="text-xs text-gray-500",
                        ),
                        class_name="flex-1",
                    ),
                    rx.icon(
                        "settings",
                        class_name="h-5 w-5 text-gray-500 hover:text-gray-800 cursor-pointer",
                    ),
                    class_name="flex items-center gap-3 p-4 border-t border-gray-200",
                ),
                class_name="shrink-0",
            ),
            class_name="border-t border-gray-200 shrink-0",
        ),
        class_name="w-72 h-screen bg-white border-r border-gray-200 flex flex-col shrink-0 shadow-lg",
    )