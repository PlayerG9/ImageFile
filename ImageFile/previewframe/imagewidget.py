r"""
class GifPlayer:
    def __init__(self, widget: tk.Widget, fp: Union[str, io.FileIO], *, autoplay=True, size: Tuple[int, int] = None):
        self.widget = widget
        self.__is_playing = False
        image: Image.Image = Image.open(fp)
        if not image.is_animated:
            raise ValueError('image is not animated')

        self.frames = []
        self.frame = 0
        for frame in range(0, image.n_frames):
            image.seek(frame)
            img = image
            if size:
                img = image.resize(size)
            self.frames.append([
                image.info['duration'],
                ImageTk.PhotoImage(img)
            ])

        if autoplay:
            self.play()

    @property
    def is_playing(self):
        return self.__is_playing  # this method to made read-only

    def play(self):
        if self.__is_playing: return
        self.__is_playing = True
        self.__play_frame()

    def stop(self):
        self.__is_playing = False

    def __play_frame(self):
        if not self.__is_playing: return
        if self.frame >= len(self.frames):
            self.frame = 0
        duration, image = self.frames[self.frame]
        self.widget.configure(image=image)
        self.frame += 1
        self.widget.after(duration, self.__play_frame)
"""
from imports import *


class ImageWidget(tk.Label):
    # if image.is_animated
    # frames: T.Dict[int, T.Tuple[int, ImageTk.PhotoImage]]  # {frame: (duration, image)} decapitated because it uses to much ram with bigger images
    # else
    imagetk: ImageTk.PhotoImage = None

    def __init__(self, master: tk.Widget, image: Image.Image, **kwargs):
        super().__init__(master, **kwargs)
        self.image: Image.Image = image
        self.size = image.size
        self.orig: T.Tuple[int, int] = image.size
        self.imagetk: ImageTk.PhotoImage = None
        # self.frames = {}
        if getattr(self.image, 'is_animated', False):
            # self.after(20, self.generate_frames)  # non-blocking
            self.n = 0
            self.bind('<Visibility>', lambda e: self.update_image())
            self.after(50, self.update_image)
        else:
            self.imagetk = self['image'] = ImageTk.PhotoImage(self.image)

    def destroy(self):
        del self.image
        del self.imagetk
        super().destroy()

    """def clear_frames(self):
        # not self.frames.clear() because this doesn't free ram
        for _, imagetk in self.frames.values():
            del imagetk
        self.frames.clear()"""

    """def generate_frames(self):
        self.frames.clear()
        image = self.image
        for frame in range(0, image.n_frames):
            image.seek(frame)
            img = image.resize(self.size)
            self.frames.append((
                image.info['duration'],
                ImageTk.PhotoImage(img)
            ))
            self.update()"""

    def resize(self, width: int, height: int):
        self.size = int(width), int(height)
        if getattr(self.image, 'is_animated', False):
            # self.clear_frames()
            pass
        else:
            image = self.image.resize(self.size)
            self.imagetk = self['image'] = ImageTk.PhotoImage(image)

    def update_image(self):
        if not self.winfo_viewable(): return
        self.n += 1
        if self.n >= self.image.n_frames:
            self.n = 0
        image = self.image
        image.seek(self.n)
        img = image.resize(self.size, Image.NEAREST)
        duration = image.info['duration']
        self.imagetk = imagetk = ImageTk.PhotoImage(img)
        # del img
        self['image'] = imagetk
        self.after(duration, self.update_image)
