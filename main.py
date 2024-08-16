from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.layout import Layout
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.material_resources  import DEVICE_TYPE
from pathlib import Path
from pytube import YouTube
from threading import Thread


try:
    from android.permissions import request_permissions, Permission

    request_permissions(
        [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ]
    )
except:
    pass
else:
    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()

path_storage = '/' if DEVICE_TYPE == 'desktop' else primary_ext_storage

class Video(Thread):
    def __init__(self, video):
        Thread.__init__(self)
        self.video = video
        self.start()

    def run(self):
        '''my_streams = yt.streams.filter(progressive=True)
        for streams in my_streams:
            print(f'Video itag: {streams.itag} Resolution: {streams.resolution}')
        input_itig = input('Enter itig value:')
        video = yt.streams.get_by_itag(input_itig)'''
        yt = self.video["video"]
        path = self.video["path"]
        video = yt.streams.filter(progressive=True).get_highest_resolution()
        global file_size
        file_size = video.filesize
        video.download(output_path=path)
        toast('Video descargado')


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ratio_card = 294/536
        self.video = {
            "video":None,
            "image": "",
            "path": str(Path(".").absolute())
        }
        self.kv = ''
        self.path_to_kv_file = 'main.kv'
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.kv = Builder.load_file("main.kv")
        return Builder.load_file('live/live.kv') if DEVICE_TYPE == 'desktop' else self.kv
    
    def update_kv_file(self, text):
        with open(self.path_to_kv_file, "w") as kv_file:
            kv_file.write(text)


    def file_manager_open(self):
        #self.file_manager.show(primary_ext_storage)
        self.file_manager.show(path_storage)
        self.manager_open = True

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        """

        self.exit_manager()
        self.video["path"] = str(Path(path).absolute())
        toast(path)

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def download(self):
        hilo = Thread(
            target=Video, args=(self.video,)
        )
        hilo.start()
        
    
    def progress_Check(self, stream = None, chunk = None, remaining = None, file_handle = None):
       

        #Gets the percentage of the file that has been downloaded.
        try:
            percent = (100*(file_size-remaining))//file_size
            self.kv.ids.progress_bar.value = percent
            self.kv.ids.text_download.text=f'Descargado {percent}%'
        except:
            pass

    def insert_video(self, url):
        hilo = Thread(target=self.get_info, args=(url, ))
        hilo.start()
    
    def get_info(self, url):
        hilo = Thread(target=self.video_info, args=(url, ))
        hilo.start()
    
    def video_info(self,url):
        self.kv.ids.image.source = ''
        print(self.kv.ids.principal_layout.size)
        self.video["video"]=YouTube(url, on_progress_callback=self.progress_Check)
        print('Video insertado con exito', self.video["video"].title)
        self.video["image"] = self.video["video"].thumbnail_url
        print(self.video["image"])
        self.kv.ids.image.source=self.video["image"]
        self.kv.ids.title.text=self.video["video"].title
        duration = str(self.video["video"].length/60).split('.')
        self.kv.ids.duration.text=f'Duración: {duration[0]}:{duration[1]}'
        
        


MainApp().run()
