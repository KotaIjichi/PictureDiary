import os
import openai
import warnings
from transformers import BlipProcessor, BlipForConditionalGeneration
from flask import Flask, request, make_response, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime

warnings.filterwarnings('ignore')

app = Flask(__name__)
num = 1
line_num = 15

processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-large')
model_raw = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-large')

def show_n_generate(path, model = model_raw):
    image = Image.open(path).convert('RGB')
    input = processor(image, return_tensors='pt')
    output = model.generate(**input)
    generated_text = processor.decode(output[0], skip_special_tokens=True)
    return generated_text

def wrap_text(text):
    global line_num

    today = datetime.now ()
    wd = ['月', '火', '水', '木', '金', '土', '日']
    month = today.month
    day = today.day
    weekday = wd[today.weekday ()]

    dt = str (month) + '月' + str (day) + '日　' + weekday + '曜日'
    lines = [dt]
    current_line = '　'
    cnt = 0
    current_cnt = 1
    length = (len (text) + 1) // (line_num - 1) + 1
    while cnt < len (text):
        if current_cnt < length:
            current_line += text[cnt]
            current_cnt += 1
        else:
            lines.append(current_line)
            current_line = text[cnt]
            current_cnt = 1
        cnt += 1
    lines.append (current_line)
    return lines

def generate_image(image_path, text):
    global num
    global line_num

    image = Image.open(image_path)
    width, height = image.size
    font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc'
    padding = width // 40
    font_size = (width + padding) // line_num - padding
    text_font = ImageFont.truetype(font_path, font_size)
    lines = wrap_text(text)

    new_image = Image.new('RGB', (width + 2 * padding, height + font_size * len (lines[1]) + 3 * padding), (255, 255, 255))
    new_image.paste(image, (padding, padding))

    draw = ImageDraw.Draw(new_image)
    text_position = ((line_num - 1) * font_size + line_num * padding, height + 2 * padding)

    for line in lines:
        draw.text(text_position, line, font=text_font, fill=(0, 0, 0), direction='ttb')
        l_top = (text_position[0] - padding / 2, text_position[1])
        l_bottom = (text_position[0] - padding / 2, text_position[1] + len(lines[1]) * font_size)
        if line != lines[-1]:
            draw.line (l_top + l_bottom, fill=(0, 0, 0), width=5)
        text_position = (text_position[0] - (font_size + padding), text_position[1])

    output_path = 'static/image/output/' + str (num) + '.jpg'
    new_image.save(output_path)

    return new_image

@app.route('/', methods = ['GET'])
def index ():
    global num
    path = 'static/image/input/' + str (num) + '.jpg'
    img = Image.open (path).convert ('RGB')
    text = '今日は公園に行ってきた。木々が立ち並ぶ中で、人々が散歩していた。青々とした木々が風に揺れ、爽やかな空気が心地よかった。人々は笑顔で歩いており、リラックスした様子が伺えた。公園では子供たちが駆け回り、友達同士がおしゃべりを楽しんでいた。鳥のさえずりが響き渡り、自然の中で過ごす平和なひとときだった。私も木陰で休みながら、心を落ち着ける時間を過ごした。公園は人々にとって憩いの場であり、自然の中で活気を感じることができる場所だ。明日もまた公園に行きたいと思った。'

    caption = show_n_generate(path)
    print (caption)

    # with open ('api_key.dat') as f:
    #     openai.api_key = f.readline ()

    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "以下の文の状況に沿った日記を、200文字以下の日本語で出力してください。文体は「だ・である調」に統一してください。"},
    #         {"role": "user", "content": caption}
    #     ]   
    # )

    # text = response["choices"][0]["message"]["content"]

    img = generate_image (path, text)
    img_io = BytesIO ()
    img.save (img_io, 'JPEG', quality = 95)
    img_io.seek (0)
    response = make_response (send_file (img_io, mimetype = 'image/jpeg'))
    return response

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    global num
    if request.method == 'POST':
        if 'file' not in request.files:
            print ('No file part')
            return 'No file part', 400

        file = request.files['file']

        if file.filename == '':
            print ('No selected file')
            return 'No selected file', 400
        
        if file.mimetype != 'image/jpeg':
            print ('Not a jpeg file')
            return 'Not a jpeg file', 400
        
        while os.path.exists ('static/image/input/' + str (num) + '.jpg'):
            num += 1
        file.save ('static/image/input/' + str (num) + '.jpg')
        
        print ('File uploaded successfully')
        return 'File uploaded successfully'
    else:
        return 'upload page'

if __name__ == '__main__':
    app.run (port = 8080, debug = True, host = '0.0.0.0')