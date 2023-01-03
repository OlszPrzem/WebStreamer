import multiprocessing
import numpy as np
from flask import Flask,render_template,Response, request, send_from_directory
import cv2
import sys
import time
from datetime import datetime
from multiprocessing import Process
import threading




class Video_Streamer():

    def __init__(self, ip_number, port = 5000):
        '''
        #################################################################



        #################################################################

        '''
        self.ip_number = ip_number
        self.port = port
        self.send, self.rec = multiprocessing.Pipe()
        self.main_queue = multiprocessing.Queue()
        self.status_dict = None
        self.return_dict = None
        self.buttons = None

        self.process_queue = multiprocessing.Queue(maxsize=2)


    def start_server(self):
        proc = Process(target=self.process, args=(self.rec,self.ip_number, self.port, self.main_queue, self.process_queue,))
        proc.start() 


    def create_buttons(self, arr_butons):
        self.buttons = arr_butons
        self.status_dict = {}

        for button in self.buttons:
            self.status_dict[button] = False


    def create_status(self, dict_status):
        self.status_name = []
        self.status_add_inf = []
        self.return_dict = {}

        for obj in dict_status:
            self.status_name.append(obj)
            self.status_add_inf.append(dict_status[obj])
            self.return_dict[obj] = 0

        self.process_queue.put(self.return_dict)


    def update_status_info(self, status_dict):
        for key in status_dict:
            self.return_dict[key] = status_dict[key]

        if not self.process_queue.full():
            self.process_queue.put(self.return_dict)


    def get_result(self):
        if not self.main_queue.empty():
            self.dict_result = self.main_queue.get()

            if "status_dict" in self.dict_result.keys():
                self.status_dict = self.dict_result["status_dict"]

        return self.status_dict


    def process(self, rec, ip_number, port, main_queue, process_queue):

        app=Flask(__name__)
        app.logger.disabled = True

        __return_dict = {}

        camera_frame = np.zeros((300,300,3), dtype = np.uint8)

        @app.route('/', methods = ['GET', 'POST'])
        def index():
            if request.method == 'POST':
                control_commandas = self.buttons

                data = request.form
                for command in control_commandas:
                    if request.form.get(command+"/") == "OK":
                        print(command, file=sys.stderr)
                        self.status_dict[command] = not self.status_dict[command] 

                        send_dict = {"status_dict":self.status_dict}
                        main_queue.put(send_dict)
                else:
                    pass

            elif request.method == 'GET':
                if self.status_dict == None and self.return_dict == None:
                    clock = str(datetime.now())
                    return render_template('index_01.html', clock=clock)

                elif self.status_dict == None and self.return_dict != None:
                    clock = str(datetime.now())
                    status_name = self.status_name
                    status_add_inf = self.status_add_inf
                    len_obj = len(status_name)
                    return render_template('index_03.html', status_name=status_name, status_add_inf=status_add_inf, len_obj=len_obj, clock=clock)
                
                elif self.status_dict != None and self.return_dict == None:
                    clock = str(datetime.now())
                    control_commandas = self.buttons
                    status_dict = self.status_dict
                    return render_template('index_02.html', control_commandas = control_commandas, status_dict = status_dict, clock=clock)

                elif self.status_dict != None and self.return_dict != None:
                    clock = clock = str(datetime.now())
                    status_name = self.status_name
                    status_add_inf = self.status_add_inf
                    len_obj = len(status_name)
                    control_commandas = self.buttons
                    status_dict = self.status_dict
                    return render_template('index_04.html', control_commandas = control_commandas, status_dict = status_dict,  status_name=status_name, status_add_inf=status_add_inf, len_obj=len_obj, clock=clock)


            if self.status_dict == None:
                clock = str(datetime.now())
                status_name = self.status_name
                status_add_inf = self.status_add_inf
                len_obj = len(status_name)
                return render_template('index_03.html', status_name=status_name, status_add_inf=status_add_inf, len_obj=len_obj, clock=clock)

            elif  self.status_dict != None and self.return_dict == None:
                clock = str(datetime.now())
                control_commandas = self.buttons
                status_dict = self.status_dict
                return render_template('index_02.html', control_commandas = control_commandas, status_dict = status_dict, clock=clock)

            elif  self.status_dict != None and self.return_dict != None:
                clock = str(datetime.now())
                status_name = self.status_name
                status_add_inf = self.status_add_inf
                len_obj = len(status_name)
                control_commandas = self.buttons
                status_dict = self.status_dict
                return render_template('index_04.html', control_commandas = control_commandas, status_dict = status_dict,  status_name=status_name, status_add_inf=status_add_inf, len_obj=len_obj, clock=clock)


        @app.route('/read_status')
        def read_status():
            if not process_queue.empty():
                __return_dict = process_queue.get()
            return __return_dict


        @app.route('/clock')
        def clock():
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

            send_dict = {
                "time_actual": date_time
            }
            return send_dict


        @app.route('/video')
        def video():
            return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


        def generate_frames():
            global camera_frame
            camera_frame = np.zeros((300,300,3), dtype = np.uint8)
            frame = np.zeros((300,300,3), dtype = np.uint8)
            global fps
            while True:
                    ret ,buffer=cv2.imencode('.jpg',camera_frame)
                    frame=buffer.tobytes()

                    yield(b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


        def update_frame(reciever):
            global camera_frame
            global fps

            time_start = time.time()
            while True:
                try:
                    actual_time = time.time()

                    fps = int(1/(actual_time - time_start))
                    camera_frame = reciever.recv()
                    time_start = actual_time
                except:
                    pass

        @app.route('/time_feed')
        def time_feed():
            global fps
            def generate():
                global fps
                yield str(fps)
            return Response(generate(), mimetype='text') 

        thread1 = threading.Thread(target = update_frame, args = (rec,))
        thread1.start()


        app.run(host=ip_number, port = port)

    def update_video_frame(self, frame):
        self.send.send(frame)

    
if __name__=="__main__":

    test1 = Video_Streamer()