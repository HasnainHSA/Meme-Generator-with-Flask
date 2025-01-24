from flask import Flask, render_template, request, url_for, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# Folder configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home route
@app.route('/')
def index():
    return render_template('upload.html')

# Route to handle image upload and meme generation
@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Save the uploaded image
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Get meme text from the form
        top_text = request.form.get('top_text', '')
        bottom_text = request.form.get('bottom_text', '')

        # Generate the meme
        meme_path = create_meme(filepath, top_text, bottom_text)

        # Return the generated meme
        filename = os.path.basename(meme_path)
        return render_template('result.html', filename=filename)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Meme generation function
def create_meme(filepath, top_text, bottom_text):
    # Open the uploaded image
    image = Image.open(filepath)
    draw = ImageDraw.Draw(image)

    # Load font
    font_path = "arial.ttf"  # Use a valid TTF font path here
    font_size = int(image.width / 15)
    font = ImageFont.truetype(font_path, font_size)

    # Text settings
    top_text = top_text.upper()
    bottom_text = bottom_text.upper()

    # Calculate text size and position
    def draw_text_with_outline(draw, text, position, font, fill="white", outline="black"):
        x, y = position
        outline_width = 2

        # Draw outline
        for dx, dy in [(-outline_width, -outline_width), (-outline_width, outline_width),
                       (outline_width, -outline_width), (outline_width, outline_width)]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline)

        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)

    # Draw top text
    if top_text:
        top_text_width, top_text_height = draw.textbbox((0, 0), top_text, font=font)[2:]
        top_text_x = (image.width - top_text_width) / 2
        top_text_y = 10
        draw_text_with_outline(draw, top_text, (top_text_x, top_text_y), font)

    # Draw bottom text
    if bottom_text:
        bottom_text_width, bottom_text_height = draw.textbbox((0, 0), bottom_text, font=font)[2:]
        bottom_text_x = (image.width - bottom_text_width) / 2
        bottom_text_y = image.height - bottom_text_height - 10
        draw_text_with_outline(draw, bottom_text, (bottom_text_x, bottom_text_y), font)

    # Save the meme
    meme_path = os.path.join(app.config['UPLOAD_FOLDER'], 'meme_' + os.path.basename(filepath))
    image.save(meme_path)
    return meme_path

if __name__ == '__main__':
    app.run(debug=True)
