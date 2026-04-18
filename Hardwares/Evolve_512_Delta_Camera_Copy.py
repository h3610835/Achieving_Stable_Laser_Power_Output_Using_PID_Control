from pyvcam import pvc
from pyvcam.camera import Camera

class CCD():
    def __init__(self):
        pvc.init_pvcam()
        self.cam = next(Camera.detect_camera())
        self.cam.open()
        self.cam.speed_table_index = 0
        self.cam.exp_mode = "Timed"
        print('Camera has been turned on!')

    # trigger mode
    def Bulb(self):
        self.cam.exp_mode = 'Bulb'
    
    # trigger mode
    def Timed(self):
        self.cam.exp_mode = 'Timed'
    
    # This function is for taking photos in the sequence mode.
    def snapshot(self, *pargs):
        if len(pargs) == 0:
            frame = self.cam.get_frame()
        elif len(pargs) == 1:
            frame = self.cam.get_frame(exp_time=pargs[0])
        else:
            pass
        # print('ccd exp time:',self.cam.exp_time)
        # print('ccd readout time:',self.cam.readout_time)
        # print('ccd clear time:',self.cam.clear_mode)
        # print('ccd last exp time:',self.cam.last_exp_time)
        # print('ccd exp mode:',self.cam.exp_mode)
        # print('ccd exp res:',self.cam.exp_res)
        # self.cam.exp_res = 1
        # print('ccd exp res:',self.cam.exp_res)
        # print('ccd temp:',self.cam.temp)
        # print('ccd temp_setpoint:',self.cam.temp_setpoint)
        return frame
    '''
    def snapshot_seq(self, *pargs):
        pvc.init_pvcam()
        self.cam = next(Camera.detect_camera())
        self.cam.open()
        self.cam.speed_table_index = 0
        self.cam.exp_mode = "Bulb"
        print('Camera has been turned on!')
        num = pargs[0]
        if len(pargs) == 1:
            frame = self.cam.get_sequence(num)
        elif len(pargs) == 2:
            self.cam.exp_time = pargs[1]
            frame = self.cam.get_sequence(num)
        else:
            pass
        print('ccd readout time:',self.cam.readout_time)
        print('ccd exp time:',self.cam.exp_time)
        print('ccd speed table index:',self.cam.speed_table_index)
        print('ccd speed table:',self.cam.speed_table)
        print('ccd gain:',self.cam.gain)
        for image in frame:
            plt.imshow(image)
            plt.show()
        return frame
    '''
    # This function is for taking photos in the live mode.
    def live(self):
        frame = self.cam.get_live_frame()
        return frame
    
    # This function should be used at the beginning of the live mode.
    def start_live(self, exposure_time = []):
        self.cam.start_live(exp_time=exposure_time)

    # This function should be used at the end of the live mode.
    def stop_live(self):
        self.cam.stop_live()

    def uninit_camera(self):
        self.cam.close()
        pvc.uninit_pvcam()
        print('Camera has been turned off!')
    
    @staticmethod
    def snapshot_seq(*pargs):
        pvc.init_pvcam()
        cam = next(Camera.detect_camera())
        cam.open()
        cam.speed_table_index = 0
        cam.exp_mode = "Bulb"
        cam.exp_time = 10
        cam.clear_mode = 2
        print('Camera has been turned on!')
        num = pargs[0]
        if len(pargs) == 1:
            frame = cam.get_sequence(num)
        elif len(pargs) == 2:
            cam.exp_time = pargs[1]
            frame = cam.get_sequence(num)
        else:
            pass
        print('ccd readout time:',cam.readout_time)
        print('ccd exp mode:', cam.exp_mode)
        print('ccd exp time:',cam.exp_time)
        print('ccd speed table index:',cam.speed_table_index)
        print('ccd speed table:',cam.speed_table)
        print('ccd gain:',cam.gain)
        print('ccd last exp time:',cam.last_exp_time)
        print('ccd clear mode:', cam.clear_mode)
        cam.close()
        pvc.uninit_pvcam()
        print('Camera has been turned off!')

        return frame

if __name__ == '__main__':
    # ccd = CCD()
    # ccd.Bulb()
    # ccd.uninit_camera()
    #ccd.snapshot(50)
    import matplotlib.pyplot as plt
    import time
    import threading
    from concurrent.futures import ThreadPoolExecutor
    import tifffile as tif
    from PIL import Image

    pool = ThreadPoolExecutor(max_workers=1)
    p1 = pool.submit(snapshot_seq,3)
    # t = Process(target = snapshot_seq, args = (3,))
    # t.start()
    print('p1 down?',p1.done())
    print('hahahah')
    # t.join()
    # images = ccd.snapshot_seq(3)
    
    frame = p1.result()
    for image in frame:
        plt.imshow(image)
        plt.show()
    pool.shutdown()
    print(type(frame))
    print(frame.shape)
    tif.imwrite('E:\\3\\Images.tif', frame, photometric = 'minisblack')