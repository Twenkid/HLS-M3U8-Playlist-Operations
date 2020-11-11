import m3u8
import copy
import glob
import os
import argparse
from os.path import dirname, abspath, join

#m3u8: https://github.com/globocom/m3u8
#python -m pip install m3u8
#Author: Todor Arnaudov
#http://artificial-mind.blogspot.com
#Experimental code

LINUX = 0; WINDOWS = 1
PLATFORM = WINDOWS
Resolutions = [(960,540), (640,360), (1920,1080)]
Bitrates = [2000, 365, 6000]
Framerates = [30, 30, 30]
RootDir = "E:\\Task\\" #Root Dir for the project. Video .ts segmens are stored in directores with their individual playlists

IsIndependentSegment = True #ffmpeg cmds, needed for the master playlists tags MUST 7.4, SHOULD 9.11 

print(RootDir)

#TBD -- Construct an FFMPEG command with the proper parameters, see the end of the file;
#sample also frame rate, to compute frame rate = 2*fps (each 2 sec, HLS standard)
def ParseInput(): 
  
  ap = argparse.ArgumentParser()
  ap.add_argument("-i", "--in", help = "Path to the input directory with all videos C:\\Source\\")
  ap.add_argument("-o", "--out", help = "Output path E:\\Stream\\")
  ap.add_argument("-b", "--bitrates", help = "video bitrate in kbits: 2000,365,6000")
  ap.add_argument("-r", "--resize", help = "Resize scale for each Bitrate: 960x540,640x480,1920x1080")  
  #may add also config  
  args = vars(ap.parse_args())
  print(args)
  return ap

def GetVideos(dir=".", filter=None): 
  if filter == None:
                    filter ="*.mp4"
  return glob.glob(abspath(join(dir, "*.mp4"))) 

def PrepareCommand():     
 '''Build ffmpeg command line'''
 pass

#ParseInput()
#Split bitrates, resolutions
#Get framerates
#Sources = ["ad1.mp4", "ad2.mp4", "v1.mp4", "v2.mp4", "v3.mp4"]
AbsPaths = GetVideos(RootDir)
print(AbsPaths)
Files = [os.path.basename(p) for p in AbsPaths];
Names = [n.rsplit('.', 1)[0] for n in Files]
print(Files)
print(Names)

Ext = ".m3u8"
Ast = "*"
DefaultResolution = "540"
MasterPrefix = "master"
DefaultMaster = MasterPrefix + DefaultResolution
DefaultVariant = DefaultResolution

PlaylistLibrary = {}
MasterPlaylistArrayM3U8 = {}  #title: m3u8 obj
OtherPlaylistsArrayM3U8 = {} 
#MasterPlaylistArrayM3U8
Sequence = [] #title, title, ... --> for the Concatenated sequence e.g. v1,v2,v3 or v1, a1, v2, a2, v3


for n in Names:
  folder = abspath(join(RootDir, n))
  print(folder)
  playlistTemplate = abspath(join(folder,Ast+Ext))
  playlistFiles = glob.glob( playlistTemplate)
  print(playlistFiles)
  PlaylistLibrary[n] = (folder, playlistFiles)
  
print(PlaylistLibrary)


#It could not search, but sample directly with predefined filenames, but that adds some flexibility



print("k,v in Play... ===============")

for title in PlaylistLibrary:
  print(title, "[title]")
  variants = PlaylistLibrary[title]
  print(variants, "[variants]")
  BaseDir, Lists = variants #BaseDir per stream
  print(BaseDir, Lists)
  OtherPlaylistsM3U8 = []
  OtherMasterPlaylistsM3U8 = []
  for v in Lists:
    print(v)  
    print(DefaultMaster)
    if (v.find(MasterPrefix)>-1): #master...
      if v.find(DefaultMaster)>-1: #master540
                                  print("Default Master Stream at " + DefaultResolution + "p", DefaultMaster, v)
                                  DefaultMasterPlaylist = v
                                  MasterPlaylistM3U8 = m3u8.load(v) 
      else:
           OtherMasterPlaylistsM3U8.append(m3u8.load(v)) #other resolutions
    elif v.find(DefaultVariant)>-1: #540
                                   print("Default Variant Stream at " + DefaultResolution + "p", v)
                                   DefaultVariantPlaylist = v
                                   VariantPlaylistM3U8 = m3u8.load(v)
    else: OtherPlaylistsM3U8.append(m3u8.load(v)) #other media playlists
    #mark also path etc or just use it from that structure?
    
                                   
    #Their beginning, as defined, is the same - comparing the longer one first: master540.m3u8, master.m3u8;  
  print("#### MASTER:")
  print("SEGMENTS:\n", MasterPlaylistM3U8.segments)
  print("TARGET DURATION: ",MasterPlaylistM3U8.target_duration)
  print("DUMPS: ", MasterPlaylistM3U8.dumps())
  print("==== DEFAULT VARIANT:")
  print(VariantPlaylistM3U8.segments)
  print(VariantPlaylistM3U8.target_duration)
  print(VariantPlaylistM3U8.dumps())
  print(MasterPlaylistM3U8.playlists)
  #MasterPlaylistM3U8.add_playlist(i) #no
  #   print(MasterPlaylistM3U8.playlists)
  
  #MasterPlaylistM3U8.playlists[0].is_independent_segments = IsIndependentSegment #should be controlled from a parameter that generates the ffmpeg commands
  MasterPlaylistM3U8.is_independent_segments = IsIndependentSegment #should be controlled from a parameter
  print("======== OTHER MASTER PLAYLISTS")
  for i in OtherMasterPlaylistsM3U8: #all are expected to have one media playlist; in another case they should be iterated
     #i.playlists[0].is_independent_segments = IsIndependentSegment -- no, that's for the M3U8 object
     i.is_independent_segments = IsIndependentSegment     
     print(i.playlists[0])      
     MasterPlaylistM3U8.add_playlist(i.playlists[0]) #no         
     print("SEGMENTS: \n", i.segments)
     print("TARGET DURATION: \n", i.target_duration)
     print("DUMPS:\n", i.dumps())  
     #join title/360p.m3u etc. - save the master playlist one level up from the folders
  
  for i in MasterPlaylistM3U8.playlists:
    print("title, i.uri:", title, i.uri)     
    #i.uri = join(join(BaseDir, title), i.uri)
    #i.base_uri = join(
    i.uri = title + i.uri
    print(i.uri)    
    #lines = i.dumps().splitlines() 
     
  #MasterPlaylistM3U8.dump('C:\\Temp\\newMaster.m3u8')
  MasterPlaylistM3U8.dump(RootDir + title + Ext)
  MasterPlaylistArrayM3U8[title] = MasterPlaylistM3U8
  OtherPlaylistsArrayM3U8[title] = OtherPlaylistsM3U8

SequenceInput = "v1,v2,v3"
SequenceList = SequenceInput.split(",")
print(SequenceList)

for k in MasterPlaylistArrayM3U8:
  print(k, MasterPlaylistArrayM3U8[k].playlists[0].uri)
  
#iterate playlists ... 

PathDelimiter="/"
if PLATFORM == WINDOWS: PathDelimiter = "\\"

k = 'v1'
#MasterPlaylistFinal = copy.deepcopy(MasterPlaylistArrayM3U8[k])
#print(MasterPlaylistFinal.dumps())

#firstItem = MasterPlaylistFinal.playlists[0]
#print(firstItem)

###Load all streams

print("@@@ First Item @@@@")
#print(firstItem)
v1 = m3u8.load((RootDir + MasterPlaylistArrayM3U8['v1'].playlists[0].uri).replace("/", PathDelimiter))
print(v1)
print(v1.dumps())

#item = m3u8.load(RootDir + MasterPlaylistArrayM3U8[p].playlists[0].uri) #first media list
print( (RootDir + MasterPlaylistArrayM3U8['v2'].playlists[0].uri).replace("/", PathDelimiter))
loadPath = (RootDir + MasterPlaylistArrayM3U8['v2'].playlists[0].uri).replace("/", PathDelimiter)
v2 = m3u8.load(loadPath) #RootDir + MasterPlaylistArrayM3U8['v2'].playlists[0].uri) #first media list

print("@@@ Item v2 @@@@")
print(v2.dumps())

print("@@@ Item v3 @@@@")
v3 = m3u8.load((RootDir + MasterPlaylistArrayM3U8['v3'].playlists[0].uri).replace("/", PathDelimiter))
print(v3.dumps())

ad1 = m3u8.load((RootDir + MasterPlaylistArrayM3U8['ad1'].playlists[0].uri).replace("/", PathDelimiter)) #RootDir + MasterPlaylistArrayM3U8['v2'].playlists[0].uri) #first media list
ad2 = m3u8.load((RootDir + MasterPlaylistArrayM3U8['ad2'].playlists[0].uri).replace("/", PathDelimiter))

''' #OK
d = m3u8.load("E:\\disc.m3u8")
d.dumps()
v1.segments[-1].discontinuity = True
for s in d.segments:
  print(s)
  v1.add_segment(s)
v1.dumps()
'''

def AddSegments(dest, src, id):
  #print("AddSegents To [" + dest. + " From " + src.uri + id + "]")
  print("AddSegents [" + id + "]") # dest.base_path + " From " + src.base_path + "[" + 
  CueOut = len(dest.segments)
  print("CueOut=",CueOut)
  #v1.segments[-1].is_endlist = False
  for s in src.segments:
                      print(s)
                      #s.base_path = ("..\\" + 'ad1').replace("/", PathDelimiter)
                      s.base_path = ("..\\" + id).replace("/", PathDelimiter)
                      s.uri = s.uri.replace("/", PathDelimiter)
                      #s = copy.deepcopy(s)
                      dest.add_segment(s); 
  dest.segments[CueOut].discontinuity = True        

AddSegments(v1, ad1, 'ad1')
AddSegments(v1, v2, 'v2')
AddSegments(v1, ad2, 'ad2')
AddSegments(v1, v3, 'v3')

print("\n### NEW LIST ###\n")
for s in v1.segments:
  print(s)
print("#EXT-X-ENDLIST\n")

v1Path = ((RootDir + MasterPlaylistArrayM3U8['v1'].playlists[0].uri).replace("/", PathDelimiter))
with open(v1Path) as f:
  content = f.read()
lines = content.split("\n")

#Normal dump() messes up after insertion of the segments, possibly something about getter/setters?; debug

v1NewPath = os.path.join(os.path.dirname(v1Path), "MergedList.m3u8")
with open(v1NewPath, "wt") as f:    
  for line in lines:
    if line.startswith("#EXTINF"): break
    f.write(line + "\n") 
  for s in v1.segments:
    f.write(str(s)+"\n")
  f.write("#EXT-X-ENDLIST\n")
  
  
 
def MergeAll(seq): #, nVariants): #should be the same for all 
    items = []    
    #Load all
    for n,i in enumerate(seq): #master playlists, directories
      print("MERGE READ: @@@ Item ["+i+"]"+"seq[n]=" + seq[n] + " @@@@")
      p = (RootDir + MasterPlaylistArrayM3U8[seq[n]].playlists[0].uri).replace("/", PathDelimiter)
      print(p)
      item = m3u8.load((RootDir + MasterPlaylistArrayM3U8[seq[n]].playlists[0].uri).replace("/", PathDelimiter))        
      item.dumps()
      items.append(item)      
      for s in item.segments:
        print(s)
        
      #n = 0
      #for v in MasterPlaylistArrayM3U8[i].playlists:
      #  items.append(m3u8.load((RootDir + v.uri).replace("/", PathDelimiter)))
      #item 0 is the root  
    root = copy.copy(items[0])
    print("====== ROOT COPY?")
    for s in root.segments: print(s)
    #root.dumps() #doesnt work
    #Adds the first/root twice even if starting fro m1?
    
    print("ITEMS[0] ?")
    #items[0].dumps()
    for n,i in enumerate(items[1:],1):    
      print(n, i)
      AddSegments(root, i, seq[n]) #dest item, src item, title
      
    #"../" + seq[0] + "/" +
    #newPath = ((RootDir + MasterPlaylistArrayM3U8[seq[n]].playlists[0].uri).replace("/", PathDelimiter))
    path = ((RootDir + MasterPlaylistArrayM3U8[seq[0]].playlists[0].uri).replace("/", PathDelimiter))
    print(path)
    with open(path) as f:
      content = f.read()
    lines = content.split("\n")
    #Normal dump() messes up after insertion of the segments, possibly something about getter/setters?; debug

    #It is in the directory of the initial segment. Should be one level up.
    newPath = os.path.join(os.path.dirname(path), "MergedListNEW.m3u8") #should have another iterator per resolution
    print(newPath)
    with open(newPath, "wt") as f:    
      for line in lines:
        if line.startswith("#EXTINF"): break
        f.write(line + "\n") 
      for s in root.segments:
        f.write(str(s)+"\n")
      f.write("#EXT-X-ENDLIST\n")
    
                
sequence = ['ad1', 'v1', 'ad2', 'v2', 'ad1', 'v3'] # 'ad1', 'v3'] 
MergeAll(sequence)

#Normal dump() messes up after insertion of the segments, possibly something about getter/setters?; debug
'''
v1NewPaths = []
v1NewPathNext = os.path.join(os.path.dirname(v1Path), "MergedList2.m3u8")
with open(v1NewPath, "wt") as f:    
  for line in lines:
    if line.startswith("#EXTINF"): break
    f.write(line + "\n") 
  for s in v1.segments:
    f.write(str(s)+"\n")
  f.write("#EXT-X-ENDLIST\n")
'''  

'''
#v1.segments[-1].discontinuity = True
CueOut = len(v1.segments)
#v1.segments[-1].is_endlist = False
for s in ad1.segments:
                      print(i)
                      s.base_path = ("..\\" + 'ad1').replace("/", PathDelimiter)
                      s.uri = s.uri.replace("/", PathDelimiter)
                      #s = copy.deepcopy(s)
                      v1.add_segment(s); 
v1.segments[CueOut].discontinuity = True                      
v1.dumps()
                      
                     
#v1.segments[-1].is_endlist = False
for s in v2.segments:
                      print(i)
                      s.base_path = ("..\\" + 'v2').replace("/", PathDelimiter)
                      s.uri = s.uri.replace("/", PathDelimiter)
                      #s = copy.deepcopy(s)
                      v1.add_segment(s); 
                      
#v1.segments[CueOut].is_endlist = False
v1.segments[CueOut].discontinuity = True
v1Dump = v1.dumps()
print("If v1.dumps Nothing, something is messed up with the structure?")

#print("Connected Lists")
#for i in v1.segments: print(i)

CueOut = len(v1.segments)
#v1.segments[-1].is_endlist = False
for s in ad2.segments:
                      print(s)
                      s.base_path = ("..\\" + 'ad2').replace("/", PathDelimiter)
                      s.uri = s.uri.replace("/", PathDelimiter)
                      #s = copy.deepcopy(s)
                      v1.add_segment(s); 
v1.segments[CueOut].discontinuity = True     
v1.dumps()

CueOut = len(v1.segments)
for s in v3.segments: 
                    print(s)
                    s.base_path = ("..\\" + 'v3').replace("/", PathDelimiter)
                    s.uri = s.uri.replace("/", PathDelimiter)
                    #s = copy.deepcopy(s);
                    v1.add_segment(s); 
v1.segments[CueOut].discontinuity = True
print("v1.dumps()")
v1.dumps()

print("\n##### Concatenated #####\n")
for s in v1.segments:
  print(s)
print("#EXT-X-ENDLIST\n")
'''

#print("Dumps#######")
##v1.segments[-1].discontinuity = True
#v1.segments.dump() #Type changed?
#print(v1)
#
#for s in v2.segments:
#  print(s)
#  v1.add_segment(s)
  
#v1.dumps()


'''

for s in d.data.get('segments')[0]:


v1.segments[-2].discontinuity = True
v1.segments[-1].discontinuity = True
v1.dumps()
v1.segments.append(v2.segments)
v1.segments[-1].discontinuity = True
v1.segments.append(v3.segments)
'''
#print(v1) #.dumps())


#MasterPlaylistFinal.dumps()
#MasterPlaylistFinal.playlists[0].append(item.playlists[0].segments) 
#MasterPlaylistFinal.data.playlists[0].append(item.playlists[0].segments) 

'''
for p in SequenceList[1:]:
  item = m3u8.load(RootDir + MasterPlaylistArrayM3U8[p].playlists[0].uri)
  for s in item.segments:
    PlaylistFinal.playlists[0].add_segment(s)  #should iterate
  print(PlaylistFinal)
'''
  #E:/Task/v2/540p.m3u8  #not valid
  #E:\Task\v2/540p.m3u8  #n  
  #"E:\Task\v2\540p.m3u8"

#for p in OtherPlaylistArrayM3U8:
  #print(k, OtherPlaylistArrayM3U8[k])
  
  
'''   
print("OTHER MEDIA PLAYLISTS")
for i in OtherPlaylistsM3U8:   
 print("SEGMENTS: \n", i.segments)
 print("TARGET DURATION: \n", i.target_duration)
 print("DUMPS: \n", i.dumps())    
'''

#filename = "e:\\newMaster.m3u8"
#with open(filename, 'w') as fileobj:
#  fileobj.write(MasterPlaylistM3U8.dumps())
#print(MasterPlaylistM3U8)
#print("Press enter...")
#inp = input()

#CONCATENATE Three Video Streams

#for p in MasterPlaylistM3U8.playlists:   
#  print(p)
#  print(str(p))
#print(MasterPlaylistM3U8.dumps())#'e:\\newMaster.m3u8')

#OtherVariants  ... add them also ...


#Should load 

# DefaultResolution in v



#Names = Path().stem
#os.path.basename(your_path)
#os.path.basename(your_path)
#regimentNamesCapitalized_l = [x.upper() for x in regimentNames]; regimentNamesCapitalized_l
#os.chdir(...)
#from pathlib import Path #Py 3.4

'''
Template command:

E:\

cd Task\


ffmpeg -loglevel debug -i ad1.mp4 -vf scale=w=960:h=540:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60 -keyint_min 60 -hls_time 4 -hls_playlist_type vod  -b:v 2000k -maxrate 2140k -bufsize 3000k -b:a 128k  -hls_flags independent_segments  -master_pl_name master540.m3u8  -hls_segment_filename ad1/540p_%03d.ts ad1/540p.m3u8 ^
 -vf scale=w=640:h=360:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60 -keyint_min 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master360.m3u8 -b:v 365k -maxrate 392k -bufsize 600k -b:a 96k -hls_segment_filename ad1/360p_%03d.ts ad1/360p.m3u8 ^
  -vf scale=w=1920:h=1080:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60 -keyint_min 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master1920.m3u8 -b:v 6000k -maxrate 6420k -bufsize 9000k -b:a 192k -hls_segment_filename ad1/1080p_%03d.ts ad1/1080p.m3u8
'''
#no -keyint_min 60
'''
ffmpeg -loglevel error -i ad1.mp4 -vf scale=w=960:h=540:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod  -b:v 2000k -maxrate 2140k -bufsize 3000k -b:a 128k  -hls_flags independent_segments  -master_pl_name master540.m3u8  -hls_segment_filename ad1/540p_%03d.ts ad1/540p.m3u8 ^
 -vf scale=w=640:h=360:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master360.m3u8 -b:v 365k -maxrate 392k -bufsize 600k -b:a 96k -hls_segment_filename ad1/360p_%03d.ts ad1/360p.m3u8 ^
 -vf scale=w=1920:h=1080:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master1920.m3u8 -b:v 6000k -maxrate 6420k -bufsize 9000k -b:a 192k -hls_segment_filename ad1/1080p_%03d.ts ad1/1080p.m3u8
#Each variant has its own master playlist. Another master playlist will be merged from all of them.

ffmpeg -loglevel error -i ad2.mp4 -vf scale=w=960:h=540:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod  -b:v 2000k -maxrate 2140k -bufsize 3000k -b:a 128k  -hls_flags independent_segments  -master_pl_name master540.m3u8  -hls_segment_filename ad2/540p_%03d.ts ad2/540p.m3u8 ^
 -vf scale=w=640:h=360:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master360.m3u8 -b:v 365k -maxrate 392k -bufsize 600k -b:a 96k -hls_segment_filename ad2/360p_%03d.ts ad2/360p.m3u8 ^
 -vf scale=w=1920:h=1080:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master1920.m3u8 -b:v 6000k -maxrate 6420k -bufsize 9000k -b:a 192k -hls_segment_filename ad2/1080p_%03d.ts ad2/1080p.m3u8
 
 
 ffmpeg -loglevel error -i v1.mp4 -vf scale=w=960:h=540:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod  -b:v 2000k -maxrate 2140k -bufsize 3000k -b:a 128k  -hls_flags independent_segments  -master_pl_name master540.m3u8  -hls_segment_filename v1/540p_%03d.ts v1/540p.m3u8 ^
 -vf scale=w=640:h=360:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master360.m3u8 -b:v 365k -maxrate 392k -bufsize 600k -b:a 96k -hls_segment_filename v1/360p_%03d.ts v1/360p.m3u8 ^
 -vf scale=w=1920:h=1080:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master1920.m3u8 -b:v 6000k -maxrate 6420k -bufsize 9000k -b:a 192k -hls_segment_filename v1/1080p_%03d.ts v1/1080p.m3u8
 
  ffmpeg -loglevel error -i v2.mp4 -vf scale=w=960:h=540:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod  -b:v 2000k -maxrate 2140k -bufsize 3000k -b:a 128k  -hls_flags independent_segments  -master_pl_name master540.m3u8  -hls_segment_filename v2/540p_%03d.ts v2/540p.m3u8 ^
 -vf scale=w=640:h=360:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master360.m3u8 -b:v 365k -maxrate 392k -bufsize 600k -b:a 96k -hls_segment_filename v2/360p_%03d.ts v2/360p.m3u8 ^
 -vf scale=w=1920:h=1080:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master1920.m3u8 -b:v 6000k -maxrate 6420k -bufsize 9000k -b:a 192k -hls_segment_filename v2/1080p_%03d.ts v2/1080p.m3u8
 
 
 ffmpeg -loglevel error -i v3.mp4 -vf scale=w=960:h=540:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod  -b:v 2000k -maxrate 2140k -bufsize 3000k -b:a 128k  -hls_flags independent_segments  -master_pl_name master540.m3u8  -hls_segment_filename v3/540p_%03d.ts v3/540p.m3u8 ^
 -vf scale=w=640:h=360:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264  -sc_threshold 0 -g 60  -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master360.m3u8 -b:v 365k -maxrate 392k -bufsize 600k -b:a 96k -hls_segment_filename v3/360p_%03d.ts v3/360p.m3u8 ^
 -vf scale=w=1920:h=1080:force_original_aspect_ratio=decrease -c:a aac -ar 48000 -c:v h264 -sc_threshold 0 -g 60 -hls_time 4 -hls_playlist_type vod   -hls_flags independent_segments  -master_pl_name master1920.m3u8 -b:v 6000k -maxrate 6420k -bufsize 9000k -b:a 192k -hls_segment_filename v3/1080p_%03d.ts v3/1080p.m3u8
 
 
 '''
 
 
#Each variant has its own master playlist. Another master playlist will be merged from all of them.

#python convert.py -i P:\Contra12-22\Contra16\ -o P:\Edit\ -r 1280:720 -b 10M 
#python convert.py -i P:\Legria\7-7-2018_All\ -o D:\Legria\ -r 1280:720 -b 15M0
#print("no resize")
#os.chdir(Dir)       



'''

#ffmpeg

#path = "E:\s\master.m3u8"
path = "E:\s\stream_0.m3u8"
path = r"E:\miko_730000.m3u8"
#playlist = m3u8.loads(path)  # this could also be an absolute filename
playlist = m3u8.load(path)  # this could also be an absolute filename
print(playlist.segments)
print(playlist.target_duration)
print(playlist.dumps())

B = m3u8.load(path)  # this could also be an absolute filename

print("copying")
C = copy.copy(playlist)

# if you want to write a file from its content

playlist.dump('playlist_Dump.m3u8')


print(C.dumps())

'''
