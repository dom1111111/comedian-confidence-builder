import pyaudio
import wave, os, random
from time import sleep
from statistics import mean


# first take stream and change it into stream
def bytes_to_sample_array(bytes_data:bytes, bytes_per_sample:int):
    bps = bytes_per_sample
    chunk = []
    for x in range(0, len(bytes_data), bps):
        # get x number of bytes for each sample, where x is bytes_per_sample, on each loop
        sample_bytes = bytes_data[x : x+bps]    # index slice
        sample = 0
        # combine each byte in the sample into a single binary number
        for y in range(bps):
            if y < bps - 1:
                sample |= sample_bytes[y] << 8  # bitwise operations: OR (|) and shift (<<)
            else:
                sample |= sample_bytes[y]
        chunk.append(sample)
    return chunk


class MeasureMicPlayAudio:
    def __init__(self, wav_folder_path:str):
        self.rec_pa = pyaudio.PyAudio()
        self.play_pa = pyaudio.PyAudio()
        self.last_chunk_sums = []
        self.audio_state = 0
        self.stream_allowed = False

        self.wav_folder_path = wav_folder_path
        self.last_wav_choice = None

        self.CHUNK_SUM_RANGE = 20
        self.CHUNK_LIST_LENGTH = self.CHUNK_SUM_RANGE * 3
        self.PERCENTAGE_DIFFERENCE_THRESHOLD = 50

        self.CHUNK = 1024                                   # aka buffer size
        self.FORMAT = pyaudio.paInt16                       # 16 bit depth
        self.CHANNELS = 1
        self.SAMPLE_RATE = 44100

    def start(self):
        self.stream_allowed = True
        self.__load_random_audio_file(self.wav_folder_path)
        self.__start_rec_stream()

    def stop(self):
        self.stream_allowed = False
        self.__close_rec_stream()
        self.__close_play_stream()

    #--------
    # audio analysis functions

    def __add_chunk_sum(self, chunk_sum):
        self.last_chunk_sums.append(chunk_sum)
        if len(self.last_chunk_sums) > self.CHUNK_LIST_LENGTH:
            self.last_chunk_sums.pop(0)

    def __detect_level_changes(self):
        n = self.CHUNK_SUM_RANGE
        x = n * 2
        # most recent 1/3rd of last_chunk_sums:
        recent_chunk_range_mean = mean(self.last_chunk_sums[-n:])       # `[-n:]` is last n items in the array
        # older 2/3rds of last_chunk_sums:
        older_chunk_range_mean = mean(self.last_chunk_sums[:x])    

        # basically, see if the recent chunk sums were significantly greater or lesser than the older ones 
        if len(self.last_chunk_sums) >= self.CHUNK_LIST_LENGTH:
            chunk_dif = (recent_chunk_range_mean/older_chunk_range_mean * 100) - 100   
            if chunk_dif > self.PERCENTAGE_DIFFERENCE_THRESHOLD:
                self.audio_state = 1
            elif chunk_dif < -self.PERCENTAGE_DIFFERENCE_THRESHOLD:
                self.audio_state = -1
            else:
                self.audio_state = 0
            print('audio state:', self.audio_state)
        else:
            self.audio_state = 0

    def __pause_rec_play(self):
        self.__start_play_stream()

        # once audio is done playing, resume rec stream
        try:                                        # this try/excpet is needed because stopping the stream while checking is_active returns an error
            while self.play_stream.is_active():
                sleep(0.1)
        except:
            pass
        self.__start_rec_stream()
        self.__load_random_audio_file(self.wav_folder_path)

    def __play_after_talking(self):
        # only play laugh track if there after sound (talking) was happening
        # in other words: only play sound if the current moment of audio is quieter than the previous
        if self.audio_state == -1:
            self.__pause_rec_play()

    def __macaulay_callback(self, in_data, frame_count, time_info, status):
        chunk_sum = sum(bytes_to_sample_array(in_data, 2))      # `in_data` is the bytes returned by the pa stream
        self.__add_chunk_sum(chunk_sum)
        self.__detect_level_changes()
        self.__play_after_talking()
        return (in_data, pyaudio.paContinue)                    # this is needed by PyAudio, so the callback works

    #--------
    # Functions related to PA stream

    def __start_rec_stream(self):
        self.__close_rec_stream()
        self.last_chunk_sums.clear()                            # reset chunk sum list!
        self.__stop_play_stream()
        if not self.stream_allowed:
            return

        print("starting rec stream")

        self.rec_stream = self.rec_pa.open(
        format=self.FORMAT, 
        channels=self.CHANNELS,
        rate=self.SAMPLE_RATE, 
        input=True,
        frames_per_buffer=self.CHUNK,
        stream_callback=self.__macaulay_callback
        )
    
    def __load_random_audio_file(self, folder_path):
        self.__close_play_stream
        if not self.stream_allowed:
            return

        file_list = os.listdir(folder_path)                     # generate a list of all files in folder path
        if self.last_wav_choice:                                # remove last loaded file so that it isn't chosen twice in a row
            file_list.remove(self.last_wav_choice)
        random_file = random.choice(file_list)                  # randomly choose one of the files from file_list
        audio_path = os.path.join(folder_path, random_file)
        self.last_wav_choice = random_file                      # set the last loaded file

        file = wave.open(audio_path, 'rb')

        def callback(in_data, frame_count, time_info, status):
            data = file.readframes(frame_count)
            return (data, pyaudio.paContinue)

        print(f'loading audio file: "{random_file}"')

        self.play_stream = self.play_pa.open(
            format = self.play_pa.get_format_from_width(file.getsampwidth()),
            channels = file.getnchannels(),
            rate = file.getframerate(),
            output = True,
            stream_callback = callback
            )

        self.play_stream.stop_stream()                          # this pauses the stream
    
    def __start_play_stream(self):
        self.__stop_play_stream()
        if not self.stream_allowed:
            return
        
        print("starting play stream")
        self.play_stream.start_stream()

    def __stop_play_stream(self):
        print('stopping play stream')
        try:
            self.play_stream.stop_stream()
        except:
            pass  

    def __close_rec_stream(self):
        print("closing rec stream")
        if hasattr(self, 'rec_stream'):
            self.rec_stream.close()

    def __close_play_stream(self):
        print("closing play stream")
        if hasattr(self, 'play_stream'):
            self.play_stream.close()
