import dearpygui.dearpygui as dpg # to create GUI
import ntpath # to get basename, means name of music
import json # database
from mutagen.mp3 import MP3 # to get info of length 
from tkinter import Tk,filedialog # to add system .mp3 file
import threading # to simultaneously change slider
import pygame # to play - pause -stop - set_volume  music
import time # to sleep slider for 0.7s to prevent crashing
import random # to play random music, if 'play' is clicked without selecting one
import os
import atexit # to close the program safely

#The sender argument represents the object that triggered the event that called this function 
#App_data is additional data that is passed to the function when the event is triggered.

dpg.create_context() #Context reffers to state of the user interface
dpg.create_viewport(title="Music Library", small_icon="music_5261.ico")
pygame.mixer.init() #By initializing the mixer module, you can start using it to load and play audio files.

global state
state=None

pygame.mixer.music.set_volume(0.5)

def update_volume(sender, app_data):
	pygame.mixer.music.set_volume(app_data / 100.0)

def load_database():
	songs = json.load(open("data/songs.json", "r+"))["songs"]
	for filename in songs:
		print(filename)

		dpg.add_button(label=f"{ntpath.basename(filename)}", callback=play, width=-1,
		               height=40, user_data=filename.replace("\\", "/"), parent="list")
		dpg.add_spacer(height=2, parent="list")


def update_database(filename: str):
	data = json.load(open("data/songs.json", "r+"))
	if filename not in data["songs"]:
		data["songs"] += [filename]
	json.dump(data, open("data/songs.json", "r+"))

def update_slider():
	global state
	while pygame.mixer.music.get_busy() or state == 'paused':
		dpg.configure_item(item="pos",default_value=pygame.mixer.music.get_pos()/1000)
		while state == 'paused':
			pass
		time.sleep(0.7)
	state=None
	dpg.configure_item("dstate",default_value=f"State: None")
	dpg.configure_item("psong",default_value="Now Playing : ")
	dpg.configure_item("play",label="Play")
	dpg.configure_item(item="pos",max_value=100)
	dpg.configure_item(item="pos",default_value=0)

def play(sender, app_data, user_data): #user_data gets path of song
	global state
	if user_data:
		pygame.mixer.music.load(user_data)
		audio = MP3(user_data) #to get info of length
		dpg.configure_item(item="pos",max_value=audio.info.length)
		pygame.mixer.music.play()
		thread=threading.Thread(target=update_slider,daemon=False).start()
		if pygame.mixer.music.get_busy():
			dpg.configure_item("play",label="Pause")
			state="playing"
			dpg.configure_item("dstate",default_value=f"State: Playing")
			dpg.configure_item("psong",default_value=f"Now Playing : {ntpath.basename(user_data)}")

def play_pause():
	global state
	if state=="playing":
		state="paused"
		pygame.mixer.music.pause()
		dpg.configure_item("play",label="Play")
		dpg.configure_item("dstate",default_value=f"State: Paused")
	elif state=="paused":
		state="playing"
		pygame.mixer.music.unpause()
		dpg.configure_item("play",label="Pause")
		dpg.configure_item("dstate",default_value=f"State: Playing")
	else:
		song = json.load(open("data/songs.json", "r"))["songs"]
		if song:
			song=random.choice(song)
			pygame.mixer.music.load(song)
			pygame.mixer.music.play()
			thread=threading.Thread(target=update_slider,daemon=False).start()	
			dpg.configure_item("play",label="Pause")
			if pygame.mixer.music.get_busy():
				audio = MP3(song)
				dpg.configure_item(item="pos",max_value=audio.info.length)
				state="playing"
				dpg.configure_item("dstate",default_value=f"State: Playing")
				dpg.configure_item("psong",default_value=f"Now Playing : {ntpath.basename(song)}")

def stop():
	global state
	pygame.mixer.music.stop()
	state=None

def add_files():
	data=json.load(open("data/songs.json","r"))
	root=Tk()
	root.withdraw()
	filename=filedialog.askopenfilename(filetypes=[("Music Files", ("*.mp3"))])
	root.quit()
	if filename.endswith(".mp3"):
		if filename not in data["songs"]:
			update_database(filename)
			dpg.add_button(label=f"{ntpath.basename(filename)}",callback=play,width=-1,height=40,user_data=filename.replace("\\","/"),parent="list")
			dpg.add_spacer(height=2,parent="list")

def add_folder():
	data=json.load(open("data/songs.json","r"))
	root=Tk()
	root.withdraw()
	folder=filedialog.askdirectory()
	root.quit()
	for filename in os.listdir(folder):
		if filename.endswith(".mp3"):
			if filename not in data["songs"]:
				update_database(os.path.join(folder,filename).replace("\\","/"))
				dpg.add_button(label=f"{ntpath.basename(filename)}",callback=play,width=-1,height=40,user_data=os.path.join(folder,filename).replace("\\","/"),parent="list")
				dpg.add_spacer(height=2,parent="list")

def search(sender, app_data):
	songs = json.load(open("data/songs.json", "r"))["songs"]
	dpg.delete_item("list", children_only=True)
	for song in songs:
		if app_data.lower() in song.lower():
			dpg.add_button(label=f"{ntpath.basename(song)}", callback=play,width=-1, height=25, user_data=song, parent="list")
			dpg.add_spacer(height=2,parent="list")

def removeall():
	songs = json.load(open("data/songs.json", "r"))
	songs["songs"].clear()
	json.dump(songs,open("data/songs.json", "w"))
	dpg.delete_item("list", children_only=True)
	load_database()

with dpg.theme(tag="slider"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (127,255,212,99))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (127,255,212,99))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (240, 240, 240))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (127,255,212,99))
		dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 10)
		dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.window(tag="main",label="window title"):
	with dpg.child_window(autosize_x=True,height=45,no_scrollbar=True):
		dpg.add_text(f"Now Playing : ",tag="psong")
	dpg.add_spacer(height=2)

	with dpg.group(horizontal=True):

		with dpg.child_window(width = 1000,border=True):
			with dpg.child_window(autosize_x=True,height=50,no_scrollbar=True):
				with dpg.group(horizontal=True):
					dpg.add_button(label="Play",width=65,height=30,tag="play",callback=play_pause)
					dpg.add_button(label="Stop",callback=stop,width=65,height=30)
					dpg.add_slider_float(tag="volume", width=120,height=15,pos=(160,15),format="%.0f%.0%",default_value=50 ,callback=update_volume)
					dpg.add_slider_float(tag="pos",width=-1,pos=(295,15),format="")

			with dpg.child_window(autosize_x=True,delay_search=True):
				with dpg.group(horizontal=True):
					dpg.add_input_text(hint="Search for a song",width=-1,callback=search)
				dpg.add_spacer(height=5)
				with dpg.child_window(autosize_x=True,delay_search=True,tag="list"):
					load_database()

		with dpg.child_window(autosize_x = True,tag="sidebar"):
			dpg.add_button(label="Add File",width=-1,height=40,callback=add_files)
			dpg.add_button(label="Add Folder",width=-1,height=40,callback=add_folder)
			dpg.add_button(label="Remove All Songs",width=-1,height=40,callback=removeall)
			dpg.add_spacer(height=5)
			dpg.add_separator()
			dpg.add_spacer(height=5)
			dpg.add_text(f"State: {state}",tag="dstate")
			dpg.add_spacer(height=5)
			dpg.add_separator()

	dpg.bind_item_theme("volume","slider")
	dpg.bind_item_theme("pos","slider")

def safe_exit():
	pygame.mixer.music.stop()
	pygame.quit()

atexit.register(safe_exit)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main",True)
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
