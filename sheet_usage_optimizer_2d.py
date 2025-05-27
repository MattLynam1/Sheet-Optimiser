
import streamlit as st
from rectpack import newPacker

SHEET_WIDTH = 560  # in mm
MAX_SHEET_LENGTH = 100000  # in mm (100 meters)

class FileSpec:
    def __init__(self, width, height, quantity, name):
        self.width = width
        self.height = height
        self.quantity = quantity
        self.name = name

def calculate_price(length_m):
    # Round up to nearest 0.5 meters
    rounded_length = ((length_m * 2 + 0.9999) // 1) / 2

    if rounded_length < 3:
        rate = 16
    elif rounded_length < 11:
        rate = 14
    elif rounded_length < 20:
        rate = 12
    else:
        rate = 10

    return rounded_length, rate, rounded_length * rate

def pack_files(files):
    packer = newPacker(rotation=True)

    for f in files:
        for _ in range(f.quantity):
            packer.add_rect(f.width, f.height, rid=f.name)

    packer.add_bin(SHEET_WIDTH, MAX_SHEET_LENGTH)

    packer.pack()

    used_height = 0
    for abin in packer:
        used_height = max(used_height, max(r.y + r.height for r in abin if r is not None))

    used_length_meters = used_height / 1000.0
    placements = []

    for abin in packer:
        for rect in abin:
            placements.append((rect.rid, rect.x, rect.y, rect.width, rect.height))

    return used_length_meters, placements

st.title("🧠 Smart Sheet Optimizer (2D Packing)")

st.markdown("Enter your file specs to calculate efficient sheet usage using 2D bin packing.")

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

    if st.button("🚀 Optimize Layout"):
        total_length, placements = pack_files(st.session_state.file_list)
        rounded_length, rate, price = calculate_price(total_length)

        st.success(f"Total sheet length used: **{total_length:.2f} meters**")
        st.info(f"Rounded length: **{rounded_length:.1f} meters** at €{rate}/meter → **€{price:.2f} total**")

        st.subheader("Placement Summary")
        for p in placements:
            st.markdown(f"- **{p[0]}** at (x={p[1]}mm, y={p[2]}mm), size: {p[3]}mm x {p[4]}mm")
else:
    st.info("No files added yet.")
