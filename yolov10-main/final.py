# 导入必要的库
import gradio as gr
import cv2
import tempfile
import os
from ultralytics import YOLOv10


# 定义YOLOv10推理函数
def yolov10_inference(image, video, video_url, model_id, image_size, conf_threshold):
    # 从预训练模型中加载YOLOv10模型
    model = YOLOv10.from_pretrained(f'jameslahm/{model_id}')
    saved_objects = set()  # 用于记录已保存的物体类别

    # 如果输入的是图像
    if image:
        results = model.predict(source=image, imgsz=image_size, conf=conf_threshold)
        annotated_image = results[0].plot()  # 绘制检测结果
        return annotated_image[:, :, ::-1], None

    # 如果输入的是视频文件
    elif video:
        video_path = tempfile.mktemp(suffix=".webm")  # 创建临时文件路径
        with open(video_path, "wb") as f:
            with open(video, "rb") as g:
                f.write(g.read())  # 将视频数据写入临时文件

        cap = cv2.VideoCapture(video_path)  # 打开视频文件

    # 如果输入的是视频URL
    elif video_url:
        cap = cv2.VideoCapture(video_url)  # 打开视频流

    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取视频宽度
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取视频高度

    output_video_path = tempfile.mktemp(suffix=".webm")  # 创建输出视频文件路径
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'vp80'), fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(source=frame, imgsz=image_size, conf=conf_threshold)
        annotated_frame = results[0].plot()  # 绘制检测结果

        # 遍历检测结果
        for result in results:
            for box in result.boxes:
                class_id = box.cls.item()
                class_name = model.names[class_id]
                if class_name not in saved_objects:
                    saved_objects.add(class_name)
                    # 保存检测到的图像
                    detected_image_path = f'detected_{class_name}.jpg'
                    cv2.imwrite(detected_image_path, frame)
                    print(f'Saved {class_name} to {detected_image_path}')

        out.write(annotated_frame)  # 写入输出视频文件

    cap.release()
    out.release()

    return None, output_video_path


# 为示例图像定义推理函数
def yolov10_inference_for_examples(image, model_path, image_size, conf_threshold):
    annotated_image, _ = yolov10_inference(image, None, None, model_path, image_size, conf_threshold)
    return annotated_image


# 定义应用程序界面
def app():
    with gr.Blocks():
        with gr.Row():
            with gr.Column():
                image = gr.Image(type="pil", label="Image", visible=True)  # 图像输入组件
                video = gr.Video(label="Video", visible=False)  # 视频输入组件
                video_url = gr.Textbox(label="Video URL", visible=False)  # 视频流URL输入框
                input_type = gr.Radio(
                    choices=["Image", "Video", "Video URL"],
                    value="Image",
                    label="Input Type",
                )  # 输入类型选择组件
                model_id = gr.Textbox(value="yolov10s", label="Model ID")  # 模型ID输入框
                image_size = gr.Slider(minimum=320, maximum=1280, value=640, label="Image Size")  # 图像大小滑块
                conf_threshold = gr.Slider(minimum=0.0, maximum=1.0, value=0.25,
                                           label="Confidence Threshold")  # 置信度阈值滑块
                yolov10_infer = gr.Button("Run Inference")  # 推理按钮

            with gr.Column():
                output_image = gr.Image(type="numpy", label="Annotated Image", visible=True)  # 输出图像组件
                output_video = gr.Video(label="Annotated Video", visible=False)  # 输出视频组件

        # 更新组件可见性
        def update_visibility(input_type):
            image_visibility = gr.update(visible=True) if input_type == "Image" else gr.update(visible=False)
            video_visibility = gr.update(visible=True) if input_type == "Video" else gr.update(visible=False)
            video_url_visibility = gr.update(visible=True) if input_type == "Video URL" else gr.update(visible=False)
            output_image_visibility = gr.update(visible=True) if input_type == "Image" else gr.update(visible=False)
            output_video_visibility = gr.update(visible=True) if input_type in ["Video", "Video URL"] else gr.update(
                visibleFalse)

            return image_visibility, video_visibility, video_url_visibility, output_image_visibility, output_video_visibility

        input_type.change(
            fn=update_visibility,
            inputs=[input_type],
            outputs=[image, video, video_url, output_image, output_video],
        )

        # 运行推理
        def run_inference(image, video, video_url, model_id, image_size, conf_threshold, input_type):
            if input_type == "Image":
                return yolov10_inference(image, None, None, model_id, image_size, conf_threshold)
            elif input_type == "Video":
                return yolov10_inference(None, video, None, model_id, image_size, conf_threshold)
            else:
                return yolov10_inference(None, None, video_url, model_id, image_size, conf_threshold)

        yolov10_infer.click(
            fn=run_inference,
            inputs=[image, video, video_url, model_id, image_size, conf_threshold, input_type],
            outputs=[output_image, output_video],
        )


