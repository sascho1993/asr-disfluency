from pydub import AudioSegment
import os
import math

out_path = "audio/switchboard_data_trim/"

dirlist = os.listdir("audio/wav")
for f in dirlist:
  if f != ".git":
    wav = AudioSegment.from_wav("wav/"+f)
    dur = wav.duration_seconds
    if dur > 2:
      count = int(math.ceil(dur/2))
      basename = f.replace(".wav", "")
      for i in range(count):
        beginning = i * 2000
        if i == count:
          new_file = wav[beginning:]
          new_file.export(out_path+basename+'_'+str(i)+'.wav', format='wav')
        else:
          end = (i+1) * 2000
          new_file = wav[beginning:end]
          new_file.export(out_path+basename+'_'+str(i)+'.wav', format='wav')
    else:
      wav.export(out_path+f, format='wav')
