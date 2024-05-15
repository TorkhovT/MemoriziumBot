from PIL import Image, ImageDraw, ImageFont

MAX_WIDTH = 500
WIDTH_RATIO = 2.5
FONT = 'image_generation/used_font.ttf'
MAX_FONT_SIZE = 30
MIN_FONT_SIZE = 15


def find_font_size(text, font, image, target_width_ratio):
    test_font_size = 100
    test_font = ImageFont.truetype(font, test_font_size)
    observed_width, _ = get_text_size(text, image, test_font)
    estimated_font_size = test_font_size / (observed_width / image.width) * target_width_ratio
    return round(max(min(estimated_font_size, MAX_FONT_SIZE), MIN_FONT_SIZE))


def get_text_size(text, image, font):
    draw = ImageDraw.Draw(Image.new('RGB', (image.width, image.height)))
    return draw.textsize(text, font)


def create_photo(text, card_id, side, user_id):
    text = text.replace('\n', ' ')
    image = Image.open('image_generation/bg.jpg')
    width, height = image.size
    editable_image = ImageDraw.Draw(image)
    font_size = find_font_size(text, FONT, image, WIDTH_RATIO)
    font = ImageFont.truetype(FONT, font_size)

    line_arr = []
    line = ''
    for word in text.split():
        if get_text_size(line + word + ' ', image, font)[0] <= MAX_WIDTH:
            line += word + ' '
        else:
            line_arr.append(line[:-1])
            line = word + ' '
    line_arr.append(line[:-1])

    count = ((len(line_arr) - 1) // 2) * get_text_size(text, image, font)[1]
    if len(line_arr) % 2 == 0:
        count += get_text_size(text, image, font)[1] / 2
    for line in line_arr:
        editable_image.text((width / 2, (height + 30) / 2 - count), line, font=font, fill='black', anchor="mm")
        count -= get_text_size(text, image, font)[1]

    image.save(f'image_generation/generated_cards/{user_id}_{card_id}_{side}.png')
