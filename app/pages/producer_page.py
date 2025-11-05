import reflex as rx
from app.states.producer_state import ProducerState


def stat_card(label: str, value: rx.Var[str | int | float], icon: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-6 w-6 text-blue-500"),
        rx.el.div(
            rx.el.p(value, class_name="text-xl font-bold text-gray-900"),
            rx.el.p(label, class_name="text-sm text-gray-500"),
        ),
        class_name="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 shadow-sm",
    )


def field_card(field: dict) -> rx.Component:
    return rx.el.div(
        rx.el.h3(field["crop"], class_name="font-semibold text-gray-800"),
        rx.el.p(f"{field['area']} ha", class_name="text-sm text-gray-600"),
        class_name="p-4 bg-gray-50 rounded-lg border border-gray-200",
    )


def producer_page() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.a(
                    rx.icon("arrow-left", class_name="h-5 w-5 mr-2"),
                    "Back to Map",
                    href="/",
                    class_name="flex items-center text-sm font-medium text-gray-600 hover:text-blue-600",
                ),
                rx.el.h1("Producer Details", class_name="text-lg font-bold"),
                class_name="flex items-center gap-4",
            ),
            class_name="bg-white border-b p-4",
        ),
        rx.el.main(
            rx.cond(
                ProducerState.producer,
                rx.el.div(
                    rx.el.div(
                        rx.image(
                            src=ProducerState.producer_avatar_url,
                            class_name="w-24 h-24 rounded-full border-4 border-white shadow-md",
                        ),
                        rx.el.div(
                            rx.el.h2(
                                ProducerState.producer["name"],
                                class_name="text-2xl font-bold text-gray-900",
                            ),
                            rx.el.p(
                                f"Member of {ProducerState.cooperative_name}",
                                class_name="text-md text-gray-600",
                            ),
                        ),
                        class_name="flex items-center gap-6 p-8 bg-gray-50 rounded-lg",
                    ),
                    rx.el.div(
                        stat_card("Total Area", ProducerState.total_area, "map"),
                        stat_card(
                            "Total Fields", ProducerState.total_fields, "grid-3x3"
                        ),
                        stat_card(
                            "Avg. Yield (t/ha)", ProducerState.average_yield, "sprout"
                        ),
                        class_name="grid md:grid-cols-3 gap-6 mt-6",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Fields",
                            class_name="text-xl font-semibold text-gray-800 mb-4",
                        ),
                        rx.el.div(
                            rx.foreach(ProducerState.producer_fields, field_card),
                            class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-4",
                        ),
                        class_name="mt-8",
                    ),
                    class_name="max-w-4xl mx-auto p-6",
                ),
                rx.el.div(
                    rx.spinner(),
                    rx.el.p("Loading producer data..."),
                    class_name="flex items-center justify-center h-64 gap-4",
                ),
            ),
            class_name="flex-1",
        ),
        class_name="bg-gray-100 min-h-screen font-['Inter']",
        on_mount=ProducerState.load_producer_data,
    )