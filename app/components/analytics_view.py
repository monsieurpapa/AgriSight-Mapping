import reflex as rx
from app.states.analytics_state import AnalyticsState


def chart_container(title: str, chart: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-sm font-semibold text-gray-700 mb-2"),
        chart,
        class_name="p-4 bg-gray-50 rounded-lg border border-gray-200",
    )


def html_legend() -> rx.Component:
    """Custom HTML legend for the pie chart."""
    return rx.el.div(
        rx.foreach(
            AnalyticsState.crop_distribution,
            lambda item: rx.el.div(
                rx.el.div(
                    class_name="w-3 h-3 rounded-full",
                    style={"background-color": item["fill"]},
                ),
                rx.el.span(
                    f"{item['name']} ({item['value']})",
                    class_name="text-xs text-gray-600",
                ),
                class_name="flex items-center gap-2",
            ),
        ),
        class_name="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 pt-2",
    )


def crop_distribution_chart() -> rx.Component:
    return chart_container(
        "Crop Distribution",
        rx.el.div(
            rx.recharts.pie_chart(
                rx.recharts.graphing_tooltip(),
                rx.recharts.pie(
                    data_key="value",
                    name_key="name",
                    data=AnalyticsState.crop_distribution,
                    cx="50%",
                    cy="50%",
                    inner_radius=40,
                    outer_radius=60,
                    padding_angle=2,
                    label=True,
                    stroke="#fff",
                    stroke_width=2,
                ),
                width="100%",
                height=150,
            ),
            html_legend(),
            class_name="flex flex-col items-center",
        ),
    )


def yield_over_time_chart() -> rx.Component:
    """Placeholder for a chart showing yield over time."""
    return chart_container(
        "Yield Over Time (t/ha)",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.x_axis(data_key="year"),
            rx.recharts.y_axis(),
            rx.recharts.bar(data_key="yield", fill="#8884d8"),
            data=AnalyticsState.yield_data,
            height=200,
            width="100%",
        ),
    )


def analytics_view() -> rx.Component:
    """The view for displaying analytics and charts."""
    return rx.el.div(
        rx.el.h2(
            "Analytics Dashboard",
            class_name="px-4 pt-4 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
        ),
        rx.el.div(
            crop_distribution_chart(),
            yield_over_time_chart(),
            class_name="flex flex-col gap-3 p-2",
        ),
        class_name="border-t border-gray-200",
    )