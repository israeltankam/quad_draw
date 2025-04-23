import streamlit as st
import math
import json
from streamlit.components.v1 import html


def show_draw_field():
    st.title("Test renderer")


    st.markdown("Click to add and move points. Draw a convex quadrilateral.")

    # Initialize session state for coordinates
    if 'coordinates' not in st.session_state:
        st.session_state.coordinates = None

    html(f"""
    <canvas id="drawCanvas" width="600" height="600" style="border:1px solid #000000;"></canvas>
    <button onclick="resetCanvas()" style="margin-bottom: 10px;">Reset</button>

    <script>
    const canvas = document.getElementById('drawCanvas');
    const ctx = canvas.getContext('2d');
    const scale = 10;
    const size = canvas.width;
    const step = size / 10;
    let points = [];

    // Load existing coordinates on component initialization
    const streamlitInput = window.parent.document.querySelectorAll('[data-testid="stTextInput"] input')[0];
    if (streamlitInput && streamlitInput.value) {{
        try {{
            points = JSON.parse(streamlitInput.value).map(p => ({{x: p[0], y: p[1]}}));
        }} catch (e) {{
            console.error('Error parsing existing coordinates:', e);
        }}
    }}

    function drawGrid() {{
        ctx.clearRect(0, 0, size, size);
        ctx.strokeStyle = '#ddd';
        ctx.font = "10px sans-serif";
        for (let i = 0; i <= 10; i++) {{
            let pos = i * step;
            ctx.beginPath();
            ctx.moveTo(pos, 0);
            ctx.lineTo(pos, size);
            ctx.stroke();
            ctx.fillStyle = '#000';
            ctx.fillText((i * scale / 10).toFixed(0), pos + 2, size - 2);

            ctx.beginPath();
            ctx.moveTo(0, size - pos);
            ctx.lineTo(size, size - pos);
            ctx.stroke();
            ctx.fillText((i * scale / 10).toFixed(0), 2, size - pos - 2);
        }}
    }}

    function drawPolygon() {{
        drawGrid();
        if (points.length >= 2) {{
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {{
                ctx.lineTo(points[i].x, points[i].y);
            }}
            ctx.closePath();
            ctx.strokeStyle = '#f00';
            ctx.stroke();
            ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
            ctx.fill();
        }}
        for (let p of points) {{
            ctx.beginPath();
            ctx.arc(p.x, p.y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = '#00f';
            ctx.fill();
        }}
    }}

    canvas.addEventListener('click', (e) => {{
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        if (points.length < 4) {{
            points.push({{x, y}});
        }} else {{
            let nearest = 0;
            let minDist = Infinity;
            for (let i = 0; i < points.length; i++) {{
                let dx = points[i].x - x;
                let dy = points[i].y - y;
                let dist = dx*dx + dy*dy;
                if (dist < minDist) {{
                    minDist = dist;
                    nearest = i;
                }}
            }}
            points[nearest] = {{x, y}};
        }}
        drawPolygon();
        sendCoordsToStreamlit();
    }});

    function resetCanvas() {{
        points = [];
        drawGrid();
        sendCoordsToStreamlit();
    }}

    function sendCoordsToStreamlit() {{
        const coords = points.map(p => [p.x, p.y]);
        const streamlitInput = window.parent.document.querySelectorAll('[data-testid="stTextInput"] input')[0];
        if (streamlitInput) {{
            streamlitInput.value = JSON.stringify(coords);
            streamlitInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}

    drawGrid();
    drawPolygon();
    </script>
    """, height=700)

    # Text input for JavaScript communication
    coords_json = st.text_input("Coordinates (auto-filled):", key="coords_input", label_visibility="collapsed")

    # Validation button
    if st.button("Validate"):
        if coords_json:
            try:
                pixel_points = json.loads(coords_json)
                
                if len(pixel_points) != 4:
                    st.warning("Please draw exactly 4 points to form a quadrilateral.")
                else:
                    # Convert pixel coordinates to scaled system
                    scaled_points = []
                    for x_pixel, y_pixel in pixel_points:
                        x = (x_pixel / 600) * 10 # 10 == scale
                        y = ((600 - y_pixel) / 600) * 10  # Invert Y-axis
                        scaled_points.append((x, y))
                    
                    st.subheader("Scaled Coordinates")
                    for i, (x, y) in enumerate(scaled_points, 1):
                        st.write(f"Point {i}: ({x:.2f}, {y:.2f})")
                    
            except json.JSONDecodeError:
                st.error("Invalid coordinate format. Please draw again.")
            except Exception as e:
                st.error(f"Error processing coordinates: {str(e)}")
        else:
            st.warning("Please draw a quadrilateral first!")

if __name__ == "__main__":
    show_draw_field()
