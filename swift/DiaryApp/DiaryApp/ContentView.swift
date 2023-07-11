//
//  ContentView.swift
//  DiaryApp
//
//  Created by 伊地知孝太 on 2023/06/23.
//

import SwiftUI
import AVFoundation
import Alamofire

class TURLImage: ObservableObject {
    enum TNetStatus { case none; case standby; case successful }
    
    @Published var netStatus: TNetStatus = .none
    @Published var img: UIImage = UIImage()
    
    func getImg(_ urlStr: String) -> Void {
        guard let url1 = URL(string: urlStr) else { return }
        
        netStatus = .standby
        
        URLSession.shared.dataTask(with: url1) { data, _, _ in
            guard let d1 = data,
                let d2 = UIImage(data: d1, scale: 5) else {
                return
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1 ) {
                self.netStatus = .successful
                self.img = d2
            }
        }.resume()
    }
}

class ImageSaver: NSObject {
    @Binding var showAlert: Bool
    
    init(_ showAlert: Binding<Bool>) {
        _showAlert = showAlert
    }
    
    func writeToPhotoAlbum(image: UIImage) {
        UIImageWriteToSavedPhotosAlbum(image, self, #selector(didFinishSavingImage), nil)
    }

    @objc func didFinishSavingImage(_ image: UIImage, didFinishSavingWithError error: Error?, contextInfo: UnsafeRawPointer) {
        
        if error != nil {
            print("保存に失敗しました。")
        } else {
            showAlert = true
        }
    }
}

struct ContentView: View {
    enum AppStatus { case camera; case diary; case other }

    @State private var isCameraShown: Bool = false
    @State private var uiImage: UIImage?
    @State var showAlert: Bool = false
    @State var uStr: String
    @State var status: AppStatus = .camera
    @State var source: UIImagePickerController.SourceType = .camera
    @ObservedObject var urlImage: TURLImage = TURLImage()
    
    func uploadImage (){
        guard let uiImage = uiImage else { return }
        guard let url = URL(string: uStr + "/upload") else { return }
        guard let imageData = uiImage.jpegData(compressionQuality: 1) else { return }
        
        self.status = AppStatus.other
        
        AF.upload( multipartFormData: { multipartFormData in
                multipartFormData.append(imageData, withName: "file", fileName: "image.jpg", mimeType: "image/jpeg")
            },
            to: url
        )
        .responseString {
            (response) in
                if let statusCode = response.response?.statusCode {
                    print(statusCode)
                    if case 200...299 = statusCode{
                        self.status = AppStatus.diary
                        print("正常")
                    }
                    else
                    {
                        resetAll()
                        print("通信エラー")
                    }
                }
        }
    }
    
    func resetAll () {
        self.isCameraShown = false
        self.uiImage = nil
        self.showAlert = false
        self.status = .camera
        self.urlImage.netStatus = .none
        self.urlImage.img = UIImage()
    }
    
    var body: some View {
        if (self.status == AppStatus.diary) {
            VStack {
                if (self.urlImage.netStatus == TURLImage.TNetStatus.successful ) {
                    Image(uiImage: self.urlImage.img)
                        .resizable()
                        .scaledToFit()
                    HStack {
                        Spacer()
                        Button("保存", action: {
                            ImageSaver($showAlert).writeToPhotoAlbum(image: self.urlImage.img)
                        }).alert(isPresented: $showAlert) {
                            Alert(title: Text("情報"), message: Text("画像を保存しました。"), dismissButton: .default(Text("OK"), action: {
                                resetAll()
                            }))
                        }
                        Spacer()
                        Button("終了", action: {
                            resetAll()
                        })
                        Spacer()
                    }
                } else if (self.urlImage.netStatus == TURLImage.TNetStatus.standby) {
                    Text("読み込み中...")
                } else {
                    VStack {
                        Text("アップロードが完了しました")
                        Button("画像を取得", action: {
                            self.urlImage.getImg(self.uStr)
                        })
                    }
                }
            }
        } else if (self.status == AppStatus.camera) {
            VStack {
                if uiImage != nil {
                    Image (uiImage: uiImage!)
                        .resizable()
                        .scaledToFit()
                    HStack {
                        Spacer()
                        Button("アップロード", action: uploadImage)
                        Spacer()
                        if (source == .camera) {
                            Button("別の写真を撮影", action: { isCameraShown = true })
                        } else {
                            Button("別の写真を選択", action: { isCameraShown = true })
                        }
                        Spacer()
                    }
                } else {
                    HStack {
                        Spacer()
                        Button("写真を撮影", action: {
                            isCameraShown = true
                            source = .camera
                        })
                        Spacer()
                        Button("写真を選択", action: {
                            isCameraShown = true
                            source = .photoLibrary
                        })
                        Spacer()
                    }
                }
            }
            .sheet(isPresented: $isCameraShown) {
                CameraView(uiImage: $uiImage, source: $source)
            }
        } else {
            Text("アップロード中...")
        }
    }
}


struct CameraView: UIViewControllerRepresentable {
    @Binding var uiImage: UIImage?
    @Binding var source: UIImagePickerController.SourceType

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let imagePicker = UIImagePickerController()
        imagePicker.sourceType = source
        imagePicker.delegate = context.coordinator
        return imagePicker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(uiImage: $uiImage)
    }

    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        @Binding var uiImage: UIImage?

        init(uiImage: Binding<UIImage?>) {
            _uiImage = uiImage
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let uiImage2 = info[.originalImage] as? UIImage {
                uiImage = uiImage2
            }

            picker.dismiss(animated: true, completion: nil)
        }
    }
}
