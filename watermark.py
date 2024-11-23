from moviepy.editor import CompositeVideoClip, VideoFileClip, ImageClip
import os

def process_video(video_path, watermark_path, output_dir, index):
    try:
        if not os.path.exists(video_path):
            print(f"[!] Video path not found: {video_path}")
            return

        if not os.path.exists(watermark_path):
            print(f"[!] Watermark path not found: {watermark_path}")

        video = VideoFileClip(video_path)
        watermark = ImageClip(watermark_path).set_duration(video.duration).set_opacity(0.5).set_position((0.5, 0.5), relative=True)

        final_video = CompositeVideoClip([video, watermark])
        output_path = os.path.join(output_dir, f"test_video_{index}.mp4")

        final_video.write_videofile(output_path, codec="libx264")

        video.close()
        final_video.close()

    except Exception as e:
        print(f"[!] Failed to process video: {str(e)}")


def main():
    video_dir = "./videos/"
    watermark_path = "./fvideos/Untitled4.png"
    output_dir = "./fvideos/"

    os.makedirs(output_dir, exist_ok=True)

    video_files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
    
    for i, video_file in enumerate(video_files, start=1):
        video_path = os.path.join(video_dir, video_file)
        process_video(video_path, watermark_path, output_dir, i)


if __name__ == "__main__":
    main()
