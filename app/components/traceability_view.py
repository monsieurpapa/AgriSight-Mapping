import reflex as rx
from app.states.traceability_state import (
    TraceabilityState,
    TimelineEvent,
    SupplyChainStep,
)
from app.states.map_state import MapState


def get_stage_icon(stage: rx.Var[str]) -> rx.Component:
    return rx.match(
        stage,
        ("Harvest", rx.icon("tractor", class_name="size-5 text-green-500")),
        ("Drying/Fermentation", rx.icon("sun", class_name="size-5 text-yellow-500")),
        ("Processing", rx.icon("factory", class_name="size-5 text-orange-500")),
        ("Export", rx.icon("ship", class_name="size-5 text-blue-500")),
        rx.icon("package", class_name="size-5 text-gray-500"),
    )


def timeline_item(event: TimelineEvent, is_last: rx.Var[bool]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                get_stage_icon(event["stage"]),
                class_name="flex items-center justify-center size-8 bg-gray-100 rounded-full ring-4 ring-white",
            ),
            rx.cond(~is_last, rx.el.div(class_name="w-px h-full bg-gray-200"), None),
            class_name="flex flex-col items-center mr-4",
        ),
        rx.el.div(
            rx.el.h3(event["stage"], class_name="font-semibold text-sm text-gray-800"),
            rx.el.p(event["description"], class_name="text-xs text-gray-500"),
            rx.el.div(
                rx.el.span(
                    event["date"], class_name="text-xs font-medium text-gray-400"
                ),
                rx.el.span(" • ", class_name="mx-1 text-gray-400"),
                rx.el.span(
                    event["location"], class_name="text-xs font-medium text-gray-400"
                ),
                class_name="mt-1",
            ),
            class_name="pb-6",
        ),
        class_name="flex",
    )


def traceability_view() -> rx.Component:
    """The view for displaying traceability information."""
    return rx.el.div(
        rx.el.h2(
            "Traceability Chain",
            class_name="px-4 pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
        ),
        rx.cond(
            MapState.selected_field_id,
            rx.el.div(
                rx.foreach(
                    TraceabilityState.selected_field_timeline,
                    lambda event, index: timeline_item(
                        event,
                        index == TraceabilityState.selected_field_timeline.length() - 1,
                    ),
                ),
                class_name="p-4",
            ),
            rx.el.div(
                rx.icon("info", class_name="size-5 text-gray-400"),
                rx.el.p(
                    "Select a field on the map or from the list to see its traceability chain.",
                    class_name="text-sm text-center text-gray-500",
                ),
                class_name="flex flex-col items-center justify-center gap-2 p-8 text-center bg-gray-50 rounded-lg m-4",
            ),
        ),
        class_name="border-t border-gray-200",
    )