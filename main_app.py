import streamer
import cv2
import random


if __name__ == "__main__":

    my_ip = "127.0.0.1"
    my_port = 5001
    Stream_server = streamer.Video_Streamer(ip_number = my_ip, port = my_port)

    cap = cv2.VideoCapture(0)

    Stream_server.create_buttons(["Camera", "Light", "Action", "Record"])

    Stream_server.create_status({
                                    "Status1": "FPS",
                                    "Status2": " ", 
                                    "Status3": " ",
                                    "Status4": "[comment]",
                                    "Status5": "[m/s]",
                                    "Status6": "[s]",
                                    "Status7": "FPS", 
                                    "Status8": " ",
                                    "Status9": "[comment]",
                                    "Status10": "<- important"
                                })

    Stream_server.start_server()
    old_status = Stream_server.get_result()

    while True:
        ret, frame = cap.read()
        Stream_server.update_video_frame(frame)

        status_dict = {
            "Status1": str(random.choice(range(1,400))),
            "Status2": str(random.choice(range(1,400))), 
            "Status3": str(random.choice(range(1,400))),
            "Status4": str(random.choice(range(1,400))),
            "Status5": str(random.choice(range(1,50))),
            "Status6": str(random.choice(range(1,50))),
            "Status7": str(random.choice(range(1,50))), 
            "Status8": str(random.choice(range(1,50))),
            "Status9": str(random.choice(range(1,50))),
            "Status10": str(random.choice(range(1,50)))
        }

        Stream_server.update_status_info(status_dict)
        new_status = Stream_server.get_result()

        if old_status != new_status:
            print(new_status)
            old_status = new_status
