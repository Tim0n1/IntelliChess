from config import config, res_x, res_y
import cv2
from hough_transform import hough
import time
videos_path = 'videos'
config = config['video']


def write_to_video(file):
    window_name = "Writing A Video"
    cv2.namedWindow(window_name)
    if file == 0:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(f'{videos_path}/{file}')  # 0 for webcam

    filename = f'{videos_path}/out.avi'
    codec = cv2.VideoWriter_fourcc(*config['codec'])
    framerate = config['framerate']
    resolution = (res_x, res_y)

    video_output = cv2.VideoWriter(filename, codec, framerate, resolution)

    if cap.isOpened():
        ret, frame = cap.read()

    else:
        ret = False

    while ret:
        #print(frame_n)
        ret, frame = cap.read()
        frame = cv2.resize(frame, (res_x, res_y))
        lines = hough(frame)
        if lines is None:
            continue
        if lines[1] == 1:
            for square in lines[0]:
                x, y = square.find_center()
                cv2.putText(frame,
                            str(square.square_name_str()),
                            (x, y),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            color=(0, 255, 0),
                            thickness=1,
                            fontScale=0.5)

        else:
            for dot in lines[0]:
                cv2.circle(frame, (dot.x, dot.y), radius=4, color=(0, 0, 255), thickness=-1)
                cv2.putText(frame,
                            str(dot.position),
                            (dot.x, dot.y),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            color=(0, 255, 0),
                            thickness=1,
                            fontScale=0.4)

            for line in lines[1]:
                cv2.line(frame, (line.x1, line.y1), (line.x2, line.y2), (0, 255, 0), 2)

        video_output.write(frame)

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) == 24:
            break
        if lines[1] == 1:
            time.sleep(0.2)
    cv2.destroyAllWindows()
    video_output.release()
    cap.release()


write_to_video('original.mp4')
#write_to_video(0)
