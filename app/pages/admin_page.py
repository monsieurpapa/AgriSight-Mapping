import reflex as rx
from app.states.admin_state import AdminState
from app.states.map_state import MapState, Farmer, Field, Cooperative, PointOfInterest


def form_label(text: str) -> rx.Component:
    return rx.el.label(text, class_name="text-sm font-medium text-gray-700")


def form_input(
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    type: str = "text",
) -> rx.Component:
    return rx.el.input(
        placeholder=placeholder,
        on_change=on_change,
        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-300 outline-none",
        default_value=value,
        type=type,
    )


def form_textarea(
    placeholder: str, value: rx.Var, on_change: rx.event.EventHandler
) -> rx.Component:
    return rx.el.textarea(
        placeholder=placeholder,
        on_change=on_change,
        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-300 outline-none h-24",
        default_value=value,
    )


def form_select(
    value: rx.Var, on_change: rx.event.EventHandler, options: rx.Var, placeholder: str
) -> rx.Component:
    return rx.el.select(
        rx.el.option(placeholder, value="", disabled=True),
        rx.foreach(options, lambda opt: rx.el.option(opt["name"], value=opt["id"])),
        value=value,
        on_change=on_change,
        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-300 outline-none",
    )


def crud_section(
    title: str,
    button_text: str,
    on_button_click: rx.event.EventHandler,
    table: rx.Component,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(title, class_name="text-xl font-semibold text-gray-800"),
            rx.el.button(
                rx.icon("plus", class_name="mr-2"),
                button_text,
                on_click=on_button_click,
                class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm",
            ),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.el.div(
            table,
            class_name="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden",
        ),
        class_name="mb-12",
    )


def form_dialog(
    title: str,
    form_component: rx.Component,
    on_submit: rx.event.EventHandler,
    open_var: rx.Var[bool],
    on_cancel: rx.event.EventHandler,
) -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(title, class_name="font-semibold"),
            rx.el.form(
                form_component,
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=on_cancel,
                        class_name="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300",
                        type="button",
                    ),
                    rx.el.button(
                        "Save",
                        type="submit",
                        class_name="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700",
                    ),
                    class_name="flex justify-end gap-4 mt-6",
                ),
                on_submit=on_submit,
            ),
        ),
        open=open_var,
    )


def cooperative_form_content() -> rx.Component:
    return rx.el.div(
        form_label("Cooperative Name"),
        form_input(
            "Enter cooperative name",
            AdminState.form_coop_name,
            AdminState.set_form_coop_name,
        ),
        class_name="flex flex-col gap-2 mt-4",
    )


def farmer_form_content() -> rx.Component:
    return rx.el.div(
        form_label("Farmer Name"),
        form_input(
            "Enter farmer name",
            AdminState.form_farmer_name,
            AdminState.set_form_farmer_name,
        ),
        form_label("Cooperative"),
        form_select(
            AdminState.form_farmer_coop_id,
            AdminState.set_form_farmer_coop_id,
            MapState.cooperatives,
            "Select a cooperative",
        ),
        class_name="flex flex-col gap-2 mt-4",
    )


def field_form_content() -> rx.Component:
    return rx.el.div(
        form_label("Farmer"),
        form_select(
            AdminState.form_field_farmer_id,
            AdminState.set_form_field_farmer_id,
            MapState.farmers,
            "Select a farmer",
        ),
        form_label("Crop"),
        form_input(
            "Enter crop type (e.g., Arabica Coffee)",
            AdminState.form_field_crop,
            AdminState.set_form_field_crop,
        ),
        form_label("Area (ha)"),
        form_input(
            "Enter area in hectares",
            AdminState.form_field_area,
            AdminState.set_form_field_area,
            type="number",
        ),
        form_label("Polygon Coordinates"),
        form_textarea(
            "Enter coordinates as lat,lng;lat,lng;...",
            AdminState.form_field_polygon,
            AdminState.set_form_field_polygon,
        ),
        class_name="flex flex-col gap-2 mt-4",
    )


def poi_form_content() -> rx.Component:
    return rx.el.div(
        form_label("Point of Interest Name"),
        form_input(
            "Enter POI name", AdminState.form_poi_name, AdminState.set_form_poi_name
        ),
        form_label("Type"),
        rx.el.select(
            rx.el.option("Warehouse"),
            rx.el.option("Processing Plant"),
            rx.el.option("Farm"),
            value=AdminState.form_poi_type,
            on_change=AdminState.set_form_poi_type,
            class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-300 outline-none",
        ),
        form_label("Latitude"),
        form_input(
            "Enter latitude",
            AdminState.form_poi_lat,
            AdminState.set_form_poi_lat,
            type="number",
        ),
        form_label("Longitude"),
        form_input(
            "Enter longitude",
            AdminState.form_poi_lng,
            AdminState.set_form_poi_lng,
            type="number",
        ),
        class_name="flex flex-col gap-2 mt-4",
    )


def table_header(*cells) -> rx.Component:
    return rx.el.thead(
        rx.el.tr(
            *[rx.el.th(cell, scope="col", class_name="px-6 py-3") for cell in cells],
            rx.el.th(
                rx.el.span("Actions", class_name="sr-only"),
                scope="col",
                class_name="px-6 py-3",
            ),
        ),
        class_name="text-xs text-gray-700 uppercase bg-gray-50",
    )


def table_cell(content: rx.Var | str) -> rx.Component:
    return rx.el.td(
        content, class_name="px-6 py-4 font-medium text-gray-900 whitespace-nowrap"
    )


def action_buttons(
    edit_handler: rx.event.EventHandler, delete_handler: rx.event.EventHandler
) -> rx.Component:
    return rx.el.td(
        rx.el.div(
            rx.el.button(
                "Edit",
                on_click=edit_handler,
                class_name="font-medium text-blue-600 hover:underline",
            ),
            rx.el.button(
                "Delete",
                on_click=delete_handler,
                class_name="font-medium text-red-600 hover:underline ml-4",
            ),
            class_name="flex items-center",
        ),
        class_name="px-6 py-4 text-right",
    )


def admin_page() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.a(
                    rx.icon("arrow-left", class_name="h-5 w-5 mr-2"),
                    "Back to Map",
                    href="/",
                    class_name="flex items-center text-sm font-medium text-gray-600 hover:text-blue-600",
                ),
                rx.el.h1("Admin Dashboard", class_name="text-2xl font-bold"),
                class_name="flex items-center gap-4",
            ),
            class_name="bg-white border-b p-4 shadow-sm sticky top-0 z-10",
        ),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Import GeoJSON Data",
                        class_name="text-xl font-semibold text-gray-800 mb-4",
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.icon(
                                "cloud_upload",
                                class_name="w-10 h-10 text-gray-400 mx-auto",
                            ),
                            rx.el.p(
                                "Drag and drop a GeoJSON file here, or click to select a file.",
                                class_name="font-medium mt-2",
                            ),
                            rx.el.p(
                                "File must be a valid GeoJSON FeatureCollection.",
                                class_name="text-sm text-gray-500",
                            ),
                            class_name="text-center p-8",
                        ),
                        id="geojson-upload",
                        class_name="cursor-pointer bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg hover:bg-gray-100 transition-colors",
                        accept={"application/json": [".geojson"]},
                    ),
                    rx.el.button(
                        "Import Data",
                        on_click=AdminState.handle_upload(
                            rx.upload_files(upload_id="geojson-upload")
                        ),
                        class_name="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors",
                        is_disabled=AdminState.is_uploading,
                    ),
                    class_name="mb-12",
                ),
                crud_section(
                    "Cooperatives",
                    "Add Cooperative",
                    AdminState.open_coop_dialog,
                    rx.el.table(
                        table_header("ID", "Name"),
                        rx.el.tbody(
                            rx.foreach(
                                MapState.cooperatives,
                                lambda coop: rx.el.tr(
                                    table_cell(coop["id"]),
                                    table_cell(coop["name"]),
                                    action_buttons(
                                        lambda: AdminState.edit_cooperative(coop),
                                        lambda: AdminState.delete_cooperative(
                                            coop["id"]
                                        ),
                                    ),
                                    class_name="bg-white border-b hover:bg-gray-50",
                                ),
                            )
                        ),
                        class_name="w-full text-sm text-left text-gray-500",
                    ),
                ),
                crud_section(
                    "Farmers",
                    "Add Farmer",
                    AdminState.open_farmer_dialog,
                    rx.el.table(
                        table_header("ID", "Name", "Cooperative ID"),
                        rx.el.tbody(
                            rx.foreach(
                                MapState.farmers,
                                lambda farmer: rx.el.tr(
                                    table_cell(farmer["id"]),
                                    table_cell(farmer["name"]),
                                    table_cell(farmer["cooperative_id"]),
                                    action_buttons(
                                        lambda: AdminState.edit_farmer(farmer),
                                        lambda: AdminState.delete_farmer(farmer["id"]),
                                    ),
                                    class_name="bg-white border-b hover:bg-gray-50",
                                ),
                            )
                        ),
                        class_name="w-full text-sm text-left text-gray-500",
                    ),
                ),
                crud_section(
                    "Fields",
                    "Add Field",
                    AdminState.open_field_dialog,
                    rx.el.table(
                        table_header("ID", "Farmer ID", "Crop", "Area (ha)"),
                        rx.el.tbody(
                            rx.foreach(
                                MapState.fields,
                                lambda field: rx.el.tr(
                                    table_cell(field["id"]),
                                    table_cell(field["farmer_id"]),
                                    table_cell(field["crop"]),
                                    table_cell(field["area"].to_string()),
                                    action_buttons(
                                        lambda: AdminState.edit_field(field),
                                        lambda: AdminState.delete_field(field["id"]),
                                    ),
                                    class_name="bg-white border-b hover:bg-gray-50",
                                ),
                            )
                        ),
                        class_name="w-full text-sm text-left text-gray-500",
                    ),
                ),
                crud_section(
                    "Points of Interest",
                    "Add POI",
                    AdminState.open_poi_dialog,
                    rx.el.table(
                        table_header("ID", "Name", "Type", "Location"),
                        rx.el.tbody(
                            rx.foreach(
                                MapState.points_of_interest,
                                lambda poi: rx.el.tr(
                                    table_cell(poi["id"]),
                                    table_cell(poi["name"]),
                                    table_cell(poi["type"]),
                                    table_cell(
                                        f"{poi['location'].lat}, {poi['location'].lng}"
                                    ),
                                    action_buttons(
                                        lambda: AdminState.edit_poi(poi),
                                        lambda: AdminState.delete_poi(poi["id"]),
                                    ),
                                    class_name="bg-white border-b hover:bg-gray-50",
                                ),
                            )
                        ),
                        class_name="w-full text-sm text-left text-gray-500",
                    ),
                ),
                form_dialog(
                    rx.cond(
                        AdminState.editing_id, "Edit Cooperative", "Add Cooperative"
                    ),
                    cooperative_form_content(),
                    AdminState.save_cooperative,
                    AdminState.coop_dialog_open,
                    AdminState.close_coop_dialog,
                ),
                form_dialog(
                    rx.cond(AdminState.editing_id, "Edit Farmer", "Add Farmer"),
                    farmer_form_content(),
                    AdminState.save_farmer,
                    AdminState.farmer_dialog_open,
                    AdminState.close_farmer_dialog,
                ),
                form_dialog(
                    rx.cond(AdminState.editing_id, "Edit Field", "Add Field"),
                    field_form_content(),
                    AdminState.save_field,
                    AdminState.field_dialog_open,
                    AdminState.close_field_dialog,
                ),
                form_dialog(
                    rx.cond(AdminState.editing_id, "Edit POI", "Add POI"),
                    poi_form_content(),
                    AdminState.save_poi,
                    AdminState.poi_dialog_open,
                    AdminState.close_poi_dialog,
                ),
                class_name="max-w-7xl mx-auto p-8",
            ),
            class_name="flex-1",
        ),
        class_name="bg-gray-50 min-h-screen font-['Inter']",
        on_mount=AdminState.on_load,
    )