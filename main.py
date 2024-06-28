import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ExifTags
import textwrap
import io
from streamlit_cropper import st_cropper
import os

####################
# Functions

# load fonts
def load_font(font_name, size):
    try:
        return ImageFont.truetype(f"fonts/{font_name}.ttf", size)
    except IOError:
        st.warning("Default font is being used, which may be too small. Consider installing Liberation Sans for better results.")
        return ImageFont.load_default()

# Correct the orientation of an image based on EXIF data
def correct_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # Cases: image don't have getexif
        pass
    return image

# Fit image to area based on longest dimension
def fit_to_area(image, max_width, max_height):
    img_width, img_height = image.size
    ratio = min(max_width / img_width, max_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Center image in the allocated space
def center_image(image, allocated_width, allocated_height):
    img_width, img_height = image.size
    x = (allocated_width - img_width) // 2
    y = (allocated_height - img_height) // 2
    return (x, y)

# Create image with user inputs
def create_image(name, country, goal, challenges, commitment, photo1, photo2):
    # Blank image with gray background
    width, height = 2250, 1580  # Set to the new larger dimensions
    image = Image.new('RGB', (width, height), (221, 221, 221, 255))
    draw = ImageDraw.Draw(image)

    # Correct the orientation of the photos if necessary
    photo1 = correct_orientation(photo1)
    photo2 = correct_orientation(photo2)

    # Resize images
    photo1 = fit_to_area(photo1, 1000, 782)
    photo2 = fit_to_area(photo2, 1000, 782)

    # Calculate positions to center the photos
    img1_x, img1_y = center_image(photo1, 1000, 782)
    img2_x, img2_y = center_image(photo2, 1000, 782)

    # Add the uploaded images to the left
    image.paste(photo1, (0 + img1_x, 0 + img1_y))
    image.paste(photo2, (0 + img2_x, 798 + img2_y))

    # Load fonts
    title_font = load_font("LiberationSans-Bold", 70)
    header_font = load_font("LiberationSans-Bold", 55)
    text_font = load_font("LiberationSans-Regular", 35)
    tag_font = load_font("LiberationSans-Regular", 20)
    
    # Font colors
    name_color = (0, 0, 0)  # Black
    country_color = (128, 128, 128)  # Gray
    header_color = (0, 0, 0)  # Black
    text_color = (0, 100, 100)  # Teal, formerly 0, 128, 128
    tag_color = (128, 128, 128)  # Gray

    # Add the text information to the right
    # Name and Country
    text_start_x = 1120
    text_start_y = 100
    draw.text((text_start_x, text_start_y), name, fill=name_color, font=title_font)
    name_width = draw.textlength(name, font=title_font)
    draw.text((text_start_x + name_width + 25, text_start_y + 15), country, fill=country_color, font=header_font)
    
    # text area width
    text_width = 55

    # Goal
    text_start_y += 150
    draw.text((text_start_x, text_start_y), "Goal", fill=header_color, font=header_font)
    text_start_y += 70
    for line in textwrap.wrap(goal, width=text_width):
        draw.text((text_start_x, text_start_y), line, font=text_font, fill=text_color)
        text_start_y += 45

    # Challenges
    text_start_y += 40
    draw.text((text_start_x, text_start_y), "Challenges", fill=header_color, font=header_font)
    text_start_y += 70
    for line in textwrap.wrap(challenges, width=text_width):
        draw.text((text_start_x, text_start_y), line, font=text_font, fill=text_color)
        text_start_y += 45

    # Commitment
    text_start_y += 40
    draw.text((text_start_x, text_start_y), "Commitment", fill=header_color, font=header_font)
    text_start_y += 70
    for line in textwrap.wrap(commitment, width=text_width):
        draw.text((text_start_x, text_start_y), line, font=text_font, fill=text_color)
        text_start_y += 45
    
    # Add the tag in the bottom-right corner
    tag_text = "made with intentions-maker <3"
    tag_bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
    tag_width = tag_bbox[2] - tag_bbox[0]
    tag_height = tag_bbox[3] - tag_bbox[1]
    padding = 15
    tag_position = (width - tag_width - padding, height - tag_height - padding)
    draw.text(tag_position, tag_text, font=tag_font, fill=tag_color)

    # Save the image to a bytes object
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes

def add_space():
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

####################
# Main Panel

st.title('Set Your Intention')
add_space()

# User inputs
st.markdown('##### Name')
name = st.text_input('Enter your name:', key='name')
add_space()
st.markdown('##### Country')
country = st.text_input('Enter your country:', key='country')
add_space()
st.markdown('##### Goal')
goal = st.text_area('What do you want to be able to do by the end of this course?', key='goal')
add_space()
st.markdown('##### Challenges')
challenges = st.text_area('What challenges are in the way of achieving your goal?', key='challenges')
add_space()
st.markdown('##### Commitment')
commitment = st.text_area('What can you commit to?', key='commitment')
add_space()
st.markdown('##### Photos')
photo1 = st.file_uploader('Upload a photo of you', type=['png', 'jpg', 'jpeg', 'heic'], key='photo1')
if photo1 is not None:
    resize_option1 = st.radio("Resize option for first photo", ["Fit whole image", "Interactive crop"], key="resize_option1")
    if resize_option1 == "Fit whole image":
        photo1 = Image.open(photo1)
        photo1 = fit_to_area(photo1, 1000, 782)
    else:
        photo1 = Image.open(photo1)
        photo1 = st_cropper(photo1, aspect_ratio=(100, 78.2)) # type: ignore

photo2 = st.file_uploader('Upload a photo of something from your life', type=['png', 'jpg', 'jpeg', 'heic'], key='photo2')
if photo2 is not None:
    resize_option2 = st.radio("Resize option for second photo", ["Fit whole image", "Interactive crop"], key="resize_option2")
    if resize_option2 == "Fit whole image":
        photo2 = Image.open(photo2)
        photo2 = fit_to_area(photo2, 1000, 782)
    else:
        photo2 = Image.open(photo2)
        photo2 = st_cropper(photo2, aspect_ratio=(100, 78.2)) # type: ignore

add_space()

if st.button('Create Image'):
    if name and country and goal and challenges and commitment and photo1 and photo2:
        img_bytes = create_image(name, country, goal, challenges, commitment, photo1, photo2)
        st.image(img_bytes, caption='Your Custom Image', use_column_width=True)
        
        stripped_name = name.replace(" ","")
        st.download_button(
            label='Download Image',
            data=img_bytes,
            file_name=f'{stripped_name}-Intention-01.png',
            mime='image/png'
        )
    else:
        st.error('Please fill in all fields and upload both images.')

