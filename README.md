# PictureDiary

## Installation
### libraqm
- `$ brew install freetype harfbuzz fribidi gtk-doc`
- `$ python3 -m pip install meson ninja`
- Download libraqm from [Releases](https://github.com/HOST-Oman/libraqm/releases) page
- Move to raqm-X.Y.Z
- `$ meson build`
- `$ ninja -C build`
- `$ ninja -C build install`

### Alamofire
- `$ sudo gem install cocoapods`
- `$ pod setup`
- Move to project directory
- `$ pod init`
- Edit Podfile
- Add `pod "Alamofire` after `use_frameworks!`
- `$ pod install`

### OpenAI API
- Get OpenAI API key
- Save it as "api_key.dat"