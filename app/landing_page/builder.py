from app.database.db import execute_query
from app.storage.minio_client import upload_file, get_file_url
from app.landing_page.templates import get_template
import json

def create_page_block(event_id, block_type, content, order_index, styles=None):
    query = """
    INSERT INTO page_blocks (event_id, block_type, content, order_index, styles)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (event_id, block_type, content, order_index, json.dumps(styles))
    result = execute_query(query, params)
    return result is not None

def get_page_blocks(event_id):
    query = """
    SELECT * FROM page_blocks WHERE event_id = %s ORDER BY order_index
    """
    params = (event_id,)
    return execute_query(query, params)

def update_page_block(block_id, content, order_index, styles=None):
    query = """
    UPDATE page_blocks SET content = %s, order_index = %s, styles = %s WHERE id = %s
    """
    params = (content, order_index, json.dumps(styles), block_id)
    result = execute_query(query, params)
    return result is not None

def delete_page_block(block_id):
    query = "DELETE FROM page_blocks WHERE id = %s"
    params = (block_id,)
    result = execute_query(query, params)
    return result is not None

def upload_image(file_data, file_name):
    file_path = upload_file(file_data, file_name, bucket_name="landing_page_images")
    if file_path:
        return get_file_url(file_path, bucket_name="landing_page_images")
    return None

def landing_page_builder(event_id):
    st.subheader("Landing Page Builder")

    # Template selection
    template_options = ["Custom", "Basic", "Webinar", "Concert"]
    selected_template = st.selectbox("Select a template", template_options)

    if selected_template != "Custom" and st.button("Apply Template"):
        template_blocks = get_template(selected_template.lower())
        for block in template_blocks:
            create_page_block(event_id, block['type'], block['content'], len(get_page_blocks(event_id)))
        st.success(f"Applied {selected_template} template successfully!")
        st.rerun()  # Changed from st.experimental_rerun()

    st.write("Add New Block")
    block_type = st.selectbox("Block Type", ["Header", "Subheader", "Text", "Image", "Video", "Button", "Spacer"])
    
    content = ""
    styles = {}

    if block_type in ["Header", "Subheader", "Text"]:
        content = st.text_area(f"{block_type} Content")
        styles["font"] = st.selectbox(f"{block_type} Font", ["Arial", "Helvetica", "Times New Roman", "Courier"])
        styles["font_size"] = st.slider(f"{block_type} Font Size", 10, 72, 16)
        styles["color"] = st.color_picker(f"{block_type} Color", "#000000")
        if block_type == "Text":
            styles["alignment"] = st.selectbox("Text Alignment", ["left", "center", "right", "justify"])
    elif block_type == "Image":
        uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            content = upload_image(uploaded_file.getvalue(), uploaded_file.name)
        styles["width"] = st.slider("Image Width (%)", 10, 100, 100)
        styles["alignment"] = st.selectbox("Image Alignment", ["left", "center", "right"])
    elif block_type == "Video":
        content = st.text_input("Video URL (YouTube or Vimeo)")
        styles["width"] = st.slider("Video Width (%)", 10, 100, 100)
    elif block_type == "Button":
        button_text = st.text_input("Button Text")
        button_url = st.text_input("Button URL")
        content = json.dumps({"text": button_text, "url": button_url})
        styles["background_color"] = st.color_picker("Button Background Color", "#4CAF50")
        styles["text_color"] = st.color_picker("Button Text Color", "#FFFFFF")
        styles["border_radius"] = st.slider("Button Border Radius", 0, 20, 4)
    elif block_type == "Spacer":
        styles["height"] = st.slider("Spacer Height (px)", 10, 200, 50)

    if st.button("Add Block"):
        order_index = len(get_page_blocks(event_id))
        if create_page_block(event_id, block_type, content, order_index, styles):
            st.success("Block added successfully")
        else:
            st.error("Failed to add block")

    st.write("Existing Blocks")
    blocks = get_page_blocks(event_id)
    for i, block in enumerate(blocks):
        with st.expander(f"{block['block_type']} - {block['id']}"):
            new_content = st.text_area("Edit Content", value=block['content'])
            new_order = st.number_input("Order", value=block['order_index'], min_value=0, max_value=len(blocks)-1)
            
            # Edit styles
            styles = json.loads(block['styles']) if block['styles'] else {}
            if block['block_type'] in ["Header", "Subheader", "Text"]:
                styles["font"] = st.selectbox(f"Font", ["Arial", "Helvetica", "Times New Roman", "Courier"], index=["Arial", "Helvetica", "Times New Roman", "Courier"].index(styles.get("font", "Arial")))
                styles["font_size"] = st.slider(f"Font Size", 10, 72, styles.get("font_size", 16))
                styles["color"] = st.color_picker(f"Color", styles.get("color", "#000000"))
                if block['block_type'] == "Text":
                    styles["alignment"] = st.selectbox("Text Alignment", ["left", "center", "right", "justify"], index=["left", "center", "right", "justify"].index(styles.get("alignment", "left")))
            elif block['block_type'] == "Image":
                styles["width"] = st.slider("Image Width (%)", 10, 100, styles.get("width", 100))
                styles["alignment"] = st.selectbox("Image Alignment", ["left", "center", "right"], index=["left", "center", "right"].index(styles.get("alignment", "center")))
            elif block['block_type'] == "Video":
                styles["width"] = st.slider("Video Width (%)", 10, 100, styles.get("width", 100))
            elif block['block_type'] == "Button":
                styles["background_color"] = st.color_picker("Button Background Color", styles.get("background_color", "#4CAF50"))
                styles["text_color"] = st.color_picker("Button Text Color", styles.get("text_color", "#FFFFFF"))
                styles["border_radius"] = st.slider("Button Border Radius", 0, 20, styles.get("border_radius", 4))
            elif block['block_type'] == "Spacer":
                styles["height"] = st.slider("Spacer Height (px)", 10, 200, styles.get("height", 50))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Update Block {block['id']}"):
                    if update_page_block(block['id'], new_content, new_order, styles):
                        st.success("Block updated successfully")
                        st.rerun()  # Changed from st.experimental_rerun()
                    else:
                        st.error("Failed to update block")
            with col2:
                if st.button(f"Delete Block {block['id']}"):
                    if delete_page_block(block['id']):
                        st.success("Block deleted successfully")
                        st.rerun()  # Changed from st.experimental_rerun()
                    else:
                        st.error("Failed to delete block")

    st.write("Preview")
    for block in blocks:
        styles = json.loads(block['styles']) if block['styles'] else {}
        if block['block_type'] == "Header":
            st.markdown(f"<h1 style='font-family:{styles.get('font', 'Arial')};font-size:{styles.get('font_size', 32)}px;color:{styles.get('color', '#000000')};'>{block['content']}</h1>", unsafe_allow_html=True)
        elif block['block_type'] == "Subheader":
            st.markdown(f"<h2 style='font-family:{styles.get('font', 'Arial')};font-size:{styles.get('font_size', 24)}px;color:{styles.get('color', '#000000')};'>{block['content']}</h2>", unsafe_allow_html=True)
        elif block['block_type'] == "Text":
            st.markdown(f"<p style='font-family:{styles.get('font', 'Arial')};font-size:{styles.get('font_size', 16)}px;color:{styles.get('color', '#000000')};text-align:{styles.get('alignment', 'left')};'>{block['content']}</p>", unsafe_allow_html=True)
        elif block['block_type'] == "Image":
            st.markdown(f"<div style='text-align:{styles.get('alignment', 'center')};'><img src='{block['content']}' style='width:{styles.get('width', 100)}%;'></div>", unsafe_allow_html=True)
        elif block['block_type'] == "Video":
            st.video(block['content'])
        elif block['block_type'] == "Button":
            button_data = json.loads(block['content'])
            st.markdown(f"<div style='text-align:center;'><a href='{button_data['url']}' target='_blank'><button style='background-color:{styles.get('background_color', '#4CAF50')};color:{styles.get('text_color', '#FFFFFF')};border:none;padding:15px 32px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;border-radius:{styles.get('border_radius', 4)}px;'>{button_data['text']}</button></a></div>", unsafe_allow_html=True)
        elif block['block_type'] == "Spacer":
            st.markdown(f"<div style='height:{styles.get('height', 50)}px;'></div>", unsafe_allow_html=True)
