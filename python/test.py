import sys
import json
from flask import Flask, request, make_response, send_file
from PIL import Image
from io import BytesIO

app = Flask (__name__)

@app.route ('/')
def index ():
    path = 'static/image/input.jpg'
    img = Image.open (path).convert ('RGB')
    img_io = BytesIO ()
    img.save (img_io, 'JPEG', quality = 95)
    img_io.seek (0)
    response = make_response (send_file (img_io, mimetype = 'image/jpeg'))
    return response
    # return json.dumps ({'Hello': 'World'}, ensure_ascii = False, indent = 2)

if __name__ == '__main__':
    app.run (port = 5050, debug = True, host = '0.0.0.0')

# from flask import Flask, request, make_response, send_file
# from PIL import Image
# from io import BytesIO
# @app.route('/sample', methods=['POST'])
# def segment(): # Pillowに変換
#     img = Image.open(BytesIO(request.data)).convert('RGB') # 画像処理。ret_imgはPillowイメージ
#     ret_img = something(img)
#     img_io = BytesIO() 
#     ret_img.save(img_io, 'JPEG', quality=95)
#     img_io.seek(0)
#     response = make_response(send_file(img_io, mimetype='image/jpeg'))
#     return response