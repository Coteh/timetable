#Timetable Helper
#By James Cote
#Load in a timetable file and find out the classes and times within it

from os import listdir, getcwd
from os.path import isfile, join
from datetime import datetime
from configparser import ConfigParser

#configs
CONFIG_FILE = getcwd() + "\\config.ini"
config = ConfigParser()
config.read(CONFIG_FILE)
#preferences set from config files
use12HrFomat = config["Main"]["12HrTimeFormat"]

#the main commands we are processing
cmdList = ["times", "classes", "change_timetable", "exit"]
#list of days of the week
dayOfWeekList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#grabs the current day of the week
todayNum = datetime.today().weekday()
#commands for times, and the int that it passes in to the query
timesDic = {
	"today" : todayNum,
	"tomorrow" : todayNum + 1,
	"yesterday" : todayNum - 1,
}
#appending days of the week to timesDic
for i in range(len(dayOfWeekList)):
	timesDic[dayOfWeekList[i].lower()] = i
#strings
cmdBarStr = "-----------------------------"
courseBarStr = "----------"
classStartStr = "--CLASS START--"
classEndStr = "--CLASS END--"
dateStr = "-DATE-"
codeStr = "Code:"
roomStr = "Room:"
dateInfoStrs = ["Day:", "TimeStart:", "TimeEnd:", "Room:"]
#a timetable list stores all the courses and their times
#here's a dictionary of all timetables loaded
#-contains timetable name (filename) as key and timetable contents as value
timetableDic = {}
#..and here's the current timetable
currTimetable = []
currTimetableName = ""
#list of all course codes
currCourseCodesList = []
#set of different kinds of course codes
courseCodeTypeSet = []
#are we done processing commands?
isDone = False

class Course:
	"""Contains information about a course"""
	def __init__(self, infoList):
		self.dateList = []
		for line in infoList:
			if line == dateStr:
				self.dateList.append([])
			elif line.startswith(codeStr):
				self.courseCode = line[len(codeStr) + 1:]
			for infoStr in dateInfoStrs:
				if line.startswith(infoStr):
					self.dateList[len(self.dateList) - 1].append(line[len(infoStr) + 1:])
		#if using 12 hour time format, convert the time for each time entry in datelist's entries
		if use12HrFomat == "True":
			for item in self.dateList:
				for i in range(1,len(item)-1):
					item[i] = convertTo12Hr(item[i])

def convertTo12Hr(_timeStr):
	try:
		#taking the first digits of the _timeStr
		splitStr = _timeStr.split(":")
		numba = int(splitStr[0])
		endTagStr = "PM"           #will be either AM or PM
		if numba == 0:
			numba = 12
			endTagStr = "AM"
		elif numba > 12:
			numba -= 12
		else:
			endTagStr = "AM"
		return str(numba) + ":" + splitStr[1] + " " + endTagStr
	except ValueError:
		return _timeStr
def loadTimetable(_file,_name):
	#clear out the current timetable before loading in new one
	global currTimetable
	currTimetable = []
	#open text file that was passed in
	txtFile = open(_file)
	lines = [line.rstrip() for line in txtFile.readlines()]
	isPlacing = False 		#are there lines currently being placed into a new list?
	infoStuff = []
	for line in lines:
		if isPlacing:
			infoStuff.append(line)
			if line == classEndStr:
				c = Course(infoStuff)
				isPlacing = False
				currTimetable.append(c)
		else:
			if line == classStartStr:
				isPlacing = True
				infoStuff = []
	global currCourseCodesList
	currCourseCodesList = [courseItem.courseCode.upper() for courseItem in currTimetable]
	global courseCodeTypeSet
	courseCodeTypeSet = set(courseCodeItem.split(" ")[0] for courseCodeItem in currCourseCodesList)
	#assigning name as the current timetable's name
	global currTimetableName
	currTimetableName = _name
	#append the current timetable to timetable dic when done
	timetableDic[currTimetableName] = currTimetable
	txtFile.close()
def changeCurrTimetable(_name):
	global currTimetable
	global currTimetableName
	currTimetable = timetableDic[_name]
	currTimetableName = _name
	global currCourseCodesList
	currCourseCodesList = [courseItem.courseCode.upper() for courseItem in currTimetable]
	global courseCodeTypeSet
	courseCodeTypeSet = set(courseCodeItem.split(" ")[0] for courseCodeItem in currCourseCodesList)
	print(cmdBarStr)
	print("Timetable changed!")
	print(cmdBarStr)
def printClasses(_dayInt):
	for classItem in currTimetable:
		for dateListItem in classItem.dateList:
			if (dateListItem[0] == dayOfWeekList[_dayInt]):
				#printing a course item
				print(courseBarStr)
				print(classItem.courseCode)
				print(dateListItem[1] + " to " + dateListItem[2])
				print(dateListItem[3])
				print(courseBarStr)
def printTimes(_courseStr):
	for classItem in currTimetable:
		if _courseStr == classItem.courseCode:
			print(classItem.courseCode)
			#printing all times and corresponding room for course
			for dateListItem in classItem.dateList:
				print(dateListItem[0] + ": " + dateListItem[1] + " to " + dateListItem[2])
				print(dateListItem[3])
def processCommand(_cmdStr):
	print(cmdBarStr)
	cmdLines = _cmdStr.split()
	if len(cmdLines) > 1:
		if cmdLines[1] in courseCodeTypeSet:
			cmdLines[1] += " " + cmdLines[2]
	if cmdLines[0] == cmdList[0]:
		try:
			printClasses(timesDic[cmdLines[1].lower()])
		except Exception:
			print("Error: Please enter a valid secondary command following \"" + cmdList[0] + "\"")
	elif cmdLines[0] == cmdList[1]:
		try:
			printTimes(cmdLines[1])
		except Exception:
			print("Error: Please enter a valid secondary command following \"" + cmdList[1] + "\"")
	elif cmdLines[0] == cmdList[2]:
		try:
			changeCurrTimetable(cmdLines[1])
		except Exception:
			print("Error: Please enter a valid secondary command following \"" + cmdList[2] + "\"")
	elif cmdLines[0] == cmdList[3]:
		print("Thank you for using Timetable Helper!")
		global isDone
		isDone = True
	else:
		print("Error: Please enter a valid command")
	print(cmdBarStr)
def main():
	thePath = getcwd() + "\\schedules\\"
	listOfFiles = [f for f in listdir(thePath) if isfile(join(thePath,f))]
	for i in range(len(listOfFiles)):
		loadTimetable(join(thePath,listOfFiles[i]),listOfFiles[i].split(".")[0])
	print(cmdBarStr)
	print("Welcome to Timetable Helper!")
	print(cmdBarStr)
	while not(isDone):
		print(cmdBarStr)
		print("Current timetable: " + currTimetableName)
		print(cmdBarStr)
		print("What would you like to see?")
		print(cmdBarStr)
		for menuOption in cmdList:
			if menuOption == "times" or menuOption == "classes" or menuOption == "change_timetable":
				print(menuOption + " (",end="",flush=True)
				iterI = 0
				iterCollection = []
				if menuOption == "times":
					iterCollection = timesDic
				elif menuOption == "classes":
					iterCollection = currCourseCodesList
				elif menuOption == "change_timetable":
					iterCollection = timetableDic
				for item in iterCollection:
					print(item,end="",flush=True)
					if iterI < len(iterCollection) - 1:
						print(", ",end="",flush=True)
					iterI+=1
				print(")")
			else:
				print(menuOption)
		commandStr = input()
		if len(commandStr) > 1000:
			print("I don't think you would be putting in these many characters, would you? Now try again.")
		else:
			try:
				processCommand(commandStr)
			except Exception:
				print("Error: Couldn't process command! Please try again.")
				print(cmdBarStr)
			

if __name__ == '__main__':
	main()