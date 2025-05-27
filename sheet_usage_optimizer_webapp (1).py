
import streamlit as st

SHEET_WIDTH = 560  # in mm

class FileSpec:
    def __init__(self, width, height, quantity, name):
        self.width = width
        self.height = height
        self.quantity = quantity
        self.name = name

    def orientations(self):
        return [(self.width, self.height), (self.height, self.width)]


class PackedRow:
    def __init__(self):
        self.items = []
        self.used_width = 0
        self.max_height = 0

    def can_fit(self, w, h):
        return self.used_width + w <= SHEET_WIDTH

    def add(self, file_name, w, h):
        self.items.append((file_name, w, h))
        self.used_width += w
        self.max_height = max(self.max_height, h)


def pack_files(files):
    rows = []
    instances = []
    for f in files:
        for _ in range(f.quantity):
            instances.append((f.name, f.orientations()))

    while instances:
        row = PackedRow()
        remaining = []
        for name, orientation_opts in instances:
            placed = False
            for w, h in orientation_opts:
                if row.can_fit(w, h):
                    row.add(name, w, h)
                    placed = True
                    break
            if not placed:
                remaining.append((name, orientation_opts))
        rows.append(row)
        instances = remaining

    total_length_meters = sum(row.max_height for row in rows) / 1000.0
    return rows, total_length_meters

st.title("📏 Sheet Usage Optimizer")

st.markdown("Enter your file specs below to calculate optimal sheet usage.")

with st.form("file_form", clear_on_submit=True):
    name = st.text_input("File name")
    width = st.number_input("Width (mm)", min_value=1)
    height = st.number_input("Height (mm)", min_value=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    submitted = st.form_submit_button("Add File")

if "file_list" not in st.session_state:
    st.session_state.file_list = []

if submitted and name and width and height and quantity:
    st.session_state.file_list.append(FileSpec(width, height, quantity, name))
    st.success(f"Added {quantity}x '{name}' ({width}mm x {height}mm)")

if st.session_state.file_list:
    st.subheader("Files to Pack")
    for i, f in enumerate(st.session_state.file_list, 1):
        st.markdown(f"**{i}. {f.name}** - {f.quantity}x {f.width}mm x {f.height}mm")

    if st.button("🧠 Optimize Layout"):
        packed_rows, total_length = pack_files(st.session_state.file_list)

        st.success(f"Total sheet length used: **{total_length:.2f} meters**")

        for i, row in enumerate(packed_rows, 1):
            st.markdown(f"### Row {i} (max height {row.max_height}mm)")
            for item in row.items:
                st.markdown(f"- {item[0]}: {item[1]}mm x {item[2]}mm")
else:
    st.info("No files added yet.")
