import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import re
import glob
from shutil import copyfile, move
import os, sys
from PIL import Image, ImageDraw, ImageFont

'''Copy media files from databse to a nclapp folder'''
def copyMediaFiles(root_path, root_path_exec):
	ncl_path_app = root_path +"nclapp"
	if(not os.path.isdir(ncl_path_app)):
		os.mkdir(ncl_path_app)

	videofile = glob.glob(root_path+"*.mp4")
	media_path = root_path+"nclapp/media/"
	if(not os.path.isdir(media_path)):
		os.mkdir(media_path)
	copyfile(videofile[0], media_path+"video.mp4" )
	slides = glob.glob(root_path_exec+"slides/*.png")
	slides = sorted(slides)
	count = 0
	for path in slides:
		copyfile(path, media_path+str(count)+".png")
		count = count + 1

'''extract the start time of each topic to use like a anchor in video'''
def find_times(file_path):
	file = open(file_path, 'r')
	f = file.read()
	times = []
	l = re.findall("\-\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("-","")
		i = i.replace("(","")
		i = i.replace(")","")
		times.append(float(i))

	return times


'''automatically generates the ncl application based on the obtained matching'''
def createNCLApplication(matching, scene_boundaries, root_path, root_path_exec):
	times = find_times(root_path+"seg.txt")
	#print(times)
	copyMediaFiles(root_path, root_path_exec)



	startTime = []
	media_path = root_path+"nclapp/media/"
	startTime.append(0)

	for t in times:
		startTime.append(t)

	startTime = sorted(list(set(startTime)))
	namespace = "{http://www.ncl.org.br/NCL3.0/EDTVProfile}"
	tree = ET.parse(root_path_exec+'main.ncl')
	root = tree.getroot()

	body = root.find("./"+namespace+"body")

	SubElement(body, "port", attrib={'id': 'entry','component':'media'})
	media = SubElement(body, "media", attrib={'id' : 'media', 'src' : 'media/video.mp4', 'descriptor' : 'main_video'})



	count = 0
	region = root.find("./"+namespace+"head/"+namespace+"regionBase")
	descriptor_base = root.find("./"+namespace+"head/"+namespace+"descriptorBase")

	dimensions = float(100/len(scene_boundaries))
	dimension_count = 0

	scene_boundaries = sorted(scene_boundaries)
	for scene in scene_boundaries:
		'''Create the regions of topic list'''
		SubElement(region, "region", attrib={'id': 'rgmenu'+str(count), 'left' :'0%', 'width' :  '20%',
		'top' : str(dimension_count) + "%", 'height' : str(dimensions) + "%", 'zIndex' : '3'})

		'''Create the descriptors for the topic list regions'''
		if count == 0:
			SubElement(descriptor_base, "descriptor", attrib={'id': 'dmenu'+str(count),
			'region' : 'rgmenu' + str(count), 'focusIndex': str(count + 1), 'moveDown' : str(count+2), 'moveUp' : str(len(scene_boundaries)),
			 'focusBorderWidth' : '-1', 'selBorderColor':'black'})
		elif count == len(scene_boundaries) - 1:
			SubElement(descriptor_base, "descriptor", attrib={'id': 'dmenu'+str(count),
			'region' : 'rgmenu' + str(count), 'focusIndex': str(count + 1), 'moveDown' : str(1), 'moveUp' : str(count),
			 'focusBorderWidth' : '-1', 'selBorderColor':'black'})
		else:
			SubElement(descriptor_base, "descriptor", attrib={'id': 'dmenu'+str(count),
			'region' : 'rgmenu' + str(count), 'focusIndex': str(count + 1), 'moveDown' : str(count+2), 'moveUp' : str(count),
			 'focusBorderWidth' : '-1', 'selBorderColor':'black'})

		SubElement(media, "area", attrib={'id': 'scene'+str(count), 'begin':''+str(startTime[scene[0]])+'s'+''})
		timeFile = Image.new('RGB', (100, 30), color = (0, 0, 0))
		d = ImageDraw.Draw(timeFile)
		d.text((10,10),str(int(startTime[scene[0]])) + " secs" , fill=(255,255,255))
		timeFile.save("time"+str(count)+".png")

		linkSelectionTimeProgress = SubElement(body, 'link', attrib={'id' : 'selectTimeProgress'+str(count),
		'xconnector' : 'onBeginSet_var'})
		SubElement(linkSelectionTimeProgress, 'bind', attrib={'role' : 'onBegin', 'component' : 'media',
		'interface' : 'scene'+str(count)})
		bind = SubElement(linkSelectionTimeProgress, "bind", attrib={'role': 'set', 'component' : 'globalVar',
		'interface' :'service.currentFocus'})
		SubElement(bind, "bindParam", attrib={'name': 'var', 'value' : str(count+1)})

		move(root_path_exec+"time"+str(count)+".png", media_path+"time"+str(count)+".png")
		SubElement(body, "port", attrib={'id': 'entryTime' +str(count),'component':'mMenuTime' + str(count)})

		mediaTime = SubElement(body, "media", attrib={'id' : 'mMenuTime' + str(count),'fit':'meetBest', 'src' : 'media/time'+str(count)+'.png', 'descriptor' : 'dmenu'+str(count)})
		

		link = SubElement(body, "link", attrib={'id':'linkTime'+str(count), 'xconnector':'onSelectionStopStart'})
		SubElement(link,"bind", attrib={'role': 'onSelection', 'component' : 'mMenuTime'+str(count)})

		SubElement(link, "bind", attrib={'role': 'stop', 'component' : 'media'})
		SubElement(link, "bind", attrib={'role': 'start', 'component' : 'media', 'interface' :'scene'+str(count)})
		count = count + 1
		dimension_count += dimensions

	count = 0

	for match in matching:
		SubElement(body,  "media", attrib={'id' : 'slide'+str(count),
		 'src' : 'media/'+str(match[1] - len(scene_boundaries))+".png", 'descriptor' : 'slide' })

		link  = SubElement(body, "link", attrib = {'id': 'link'+str(count), 'xconnector' : 'onBeginStart'})
		SubElement(link,"bind", attrib={'role': 'onBegin', 'component' : 'media', 'interface' : 'scene'+str(count)})
		SubElement(link, "bind", attrib={'role': 'start', 'component' : 'slide'+str(count)})
		link2   = SubElement(body, "link", attrib = {'id': 'linkStop'+str(count), 'xconnector' : 'onEndStop'})
		SubElement(link2,"bind", attrib={'role': 'onEnd', 'component' : 'media'})
		SubElement(link2, "bind", attrib={'role': 'stop', 'component' : 'slide'+str(count)})
		if(count > 0):
			link = SubElement(body, "link", attrib={'id': 'linkStop'+str(count), 'xconnector':'onBeginEnd'})
			SubElement(link, "bind", attrib={'role': 'onBegin', 'component' : 'slide'+str(count)})
			SubElement(link, "bind", attrib={'role': 'end', 'component' : 'slide'+str(count-1)})

		count = count + 1

	xml = tostring(root).decode()

	xml = xml.replace("ns0:","").replace(":ns0", "")
	root = ET.fromstring(xml)
	app_output = open(root_path + "nclapp/main.ncl", "w")
	app_output.write(xml)
	app_output.close()
