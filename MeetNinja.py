#!/usr/bin/env python3

from selenium import webdriver; import requests
from selenium.webdriver.support import expected_conditions as when
from selenium.webdriver.common.by import By as by
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
import pause; import os; import re
import time; from datetime import datetime, timedelta
import colorama; from termcolor import colored
import os, json, threading, random
import urllib
from art import *
import speech_recognition as sr
import wave, pyaudio
import traceback
import time, sys, trace

class KThread(threading.Thread):
  """A subclass of threading.Thread, with a kill()
method."""
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False
  def start(self):
    """Start the thread."""
    self.__run_backup = self.run
    self.run = self.__run     
    threading.Thread.start(self)
  def __run(self):
    """Hacked run function, which installs the
trace."""
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
  def globaltrace(self, frame, why, arg):
    if why == 'call':
      return self.localtrace
    else:
      return None
  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == 'line':
        raise Exception("This is normal - The thread was exited.")
    return self.localtrace
  def kill(self):
    self.killed = True

colorama.init()

'''
GOOGLE MEET JSON FILE:
With 2 being the example duration
{
"1970-01-01T00:00:00.000Z one": [
"https://meet.google.com/exampleLink1",
2
],
"1970-01-01T00:00:00.000Z two": [
"https://meet.google.com/exampleLink2",
2
]
}
LOGIN JSON FILE:
{
"accounts.google.com": {
"#identifierId": [
"example@example.com",
3,
"sendText"
],
"googleLogin": [
"0",
0,
"googleLogin"
]
}, 
"oauthWebsite": {
"#studentId": [
"SAMPLE_STUDENT_ID_IN_SAMPLE_FIELD",
0,
"sendText"
], "#username": [
"sample_username",
0,
"sendText"
], "#password": [
"password",
0,
"sendText"
], "input[type="submit"]": [
"0",
0,
"click"
]
}
}

SPEECH JSON FILE:
with alex being example name
{
    "['Alex', 'Alix', 'Alox']": [
        "present sir"
    ]
}
'''
MEETS = json.loads(open("timings.json", "r").read())
LOGIN_INFO = json.loads(open("login.json", "r").read())
SPEECH_RESPONSES = json.loads(open("speech.json", "r").read())
BROWSER_DRIVER = "ChromeDrivers/win32/chromedriver.exe"

#                   Google Chrome
#           Linux: "ChromeDrivers/linux64/chromedriver"
#             Mac: "ChromeDrivers/mac64/chromedriver"
#        Mac (M1): "ChromeDrivers/mac64_m1/chromedriver"
#         Windows: "ChromeDrivers/win32/chromedriver.exe"

#                   Mozilla Firefox
#     Linux (x32): "FirefoxDrivers/linux32/geckodriver"
#     Linux (x64): "FirefoxDrivers/linux64/geckodriver"
#             Mac: "FirefoxDrivers/mac64/geckodriver"
#   Windows (x32): "FirefoxDrivers/win32/geckodriver.exe"
#   Windows (x64): "FirefoxDrivers/win64/geckodriver.exe"
##################################################################

# All required interactive elements' locators (text fields, buttons, etc.)
joinButton1Path = "//span[contains(text(), 'Join')]"
joinButton2Path = "//span[contains(text(), 'Ask to join')]"
endButtonPath = "[aria-label='Leave call']"

currentVersionNumber = "v3.1.1"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/AutomationDerby/MeetNinja/master/versionfile.txt"
BANNER1 = colored(text2art("MEETHAX   V2"), 'blue')
BANNER2 = colored('''                    ------------------------------------------''', 'blue')
BANNER3 = colored('''                    ||    MeetHax V2: The Google Meet Bot   ||''', 'red')
BANNER4 = colored('''                    ------------------------------------------''', 'blue')


def printBanner():
    print(BANNER1), print(BANNER2), print(BANNER3), print(BANNER4)
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

def versionCheck():
    global currentVersionNumber

    print("\nChecking for MeetNinja updates...", end="")

    crawlVersionFile = requests.get(VERSION_CHECK_URL)
    crawlVersionFile = str(crawlVersionFile.content)
    crawlVersionFile = re.findall(r"([0-9]+)", crawlVersionFile)
    latestVersionNumber = int(''.join(crawlVersionFile))

    currentVersionNumber = re.findall(r"([0-9]+)", currentVersionNumber)
    currentVersionNumber = int(''.join(currentVersionNumber))

    if currentVersionNumber >= latestVersionNumber:
        print(colored(" You are using the latest version!\n", "green"))
    elif currentVersionNumber < latestVersionNumber:
        print(colored(" You are using an older version of MeetNinja.", "red"))
        print(colored("\nGet the latest version at https://github.com/AutomationDerby/MeetNinja", "yellow"))
        print(colored("Every new version comes with fixes, improvements, new features, etc..", "yellow"))
        print(colored("Please do not open an Issue if you see this message and have not yet tried the latest version.", "yellow"))


def fixTimeFormat(rawTime):
    rawTime = list(rawTime.split())
    times = list(map(int, rawTime[0].split(":")))
    dates = list(map(int, reversed(rawTime[1].split("/"))))
    startTime = dates + times
    return startTime


def timeStamp():
    timeNow = str(datetime.now())
    timeRegEx = re.findall(r"([0-9]+:[0-9]+:[0-9]+)", timeNow)
    return(timeRegEx[0])


def initBrowser():
    print("\nInitializing browser...", end="")
    if BROWSER_DRIVER.lower().startswith("chrome"):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--disable-infobars")
        chromeOptions.add_argument("--disable-gpu")
        chromeOptions.add_argument("--disable-extensions")
        chromeOptions.add_argument("--window-size=800,800")
        chromeOptions.add_argument("--incognito")
        chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
        chromeOptions.add_experimental_option("prefs", {"profile.default_content_setting_values.media_stream_mic": 2,
                                                        "profile.default_content_setting_values.media_stream_camera": 2,
                                                        "profile.default_content_setting_values.notifications": 2
                                                        })
        if BROWSER_DRIVER.lower().endswith(".exe"):
            driver = webdriver.Chrome(executable_path=BROWSER_DRIVER, options=chromeOptions)
        else:
            servicePath = Service(BROWSER_DRIVER)
            driver = webdriver.Chrome(service=servicePath, options=chromeOptions)

    elif BROWSER_DRIVER.lower().startswith("firefox"):
        firefoxOptions = webdriver.FirefoxOptions()
        firefoxOptions.add_argument("--width=800"), firefoxOptions.add_argument("--height=800")
        # firefoxOptions.headless = True
        firefoxOptions.set_preference("layers.acceleration.disabled", True)
        firefoxOptions.set_preference("browser.privatebrowsing.autostart", True)
        firefoxOptions.set_preference("permissions.default.microphone", 2)
        firefoxOptions.set_preference("permissions.default.camera", 2)
        if BROWSER_DRIVER.lower().endswith(".exe"):
            driver = webdriver.Firefox(executable_path=BROWSER_DRIVER, options=firefoxOptions)
        else:
            servicePath = Service(BROWSER_DRIVER)
            driver = webdriver.Firefox(service=servicePath, options=firefoxOptions)
    print(colored(" Success!", "green"))
    return(driver)


def login():
    print("Logging into Google account...", end="")
    driver.get('https://accounts.google.com/signin')
    for indexNo, (comName, divInfo) in enumerate(LOGIN_INFO.items(), start=1):
         while (not(driver.current_url.find(comName) != -1)):
            (1+1==3) # placeholder
         for indexNum, (divName, clickInfo) in enumerate(divInfo.items(), start=1):
            try:
               field = wait.until(when.element_to_be_clickable((by.CSS_SELECTOR,(divName if divName != "googleLogin" else "[jsname=\"LgbsSe\"]"))))
               time.sleep(clickInfo[1])
               if(clickInfo[2] == "click"):
                  field.click()
               elif(clickInfo[2] == "sendText"):
                  field.send_keys(clickInfo[0])
               elif(clickInfo[2] == "googleLogin" and divName == "googleLogin"):
                  field.click()
            except Exception as e:
                  (1+1==3) # placeholder
    time.sleep(3)
    print(colored(" Success!", "green"))

def leave_check():
    while endTime - datetime.now() > timedelta(seconds=0):
        try:
            while(not connect()):
                driver.refresh()
                time.sleep(1)
            time.sleep(1)
            while (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<p><b>429.</b> <ins>That\'s an error.</ins></p>') != -1):
                try:
                    during_meet.kill()
                    during_meet = None
                except Exception:
                    (1+1==3)
                time.sleep(1)
                driver.get(meetingInfo[0])
            while (((wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">Your meeting code has expired</div>') != -1 or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">There was a problem joining this video call</div>') != -1) or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div class="jtEd4b">You can\'t create a meeting yourself.') != -1 and not wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('your teacher to join and then refresh this page.</div>') != -1)) or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find("<div class=\"jtEd4b\">This call has ended</div>") != -1):
                try:
                    during_meet.kill()
                    during_meet = None
                except Exception:
                    (1+1==3)
                time.sleep(1)
                driver.get(meetingInfo[0])
                continue
            while (((((wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div class="jtEd4b">You can\'t create a meeting yourself.') != -1 and wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('your teacher to join and then refresh this page.</div>') != -1) or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">This meeting hasn\'t started yet</div>') != -1) or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">Someone has removed you from the meeting</div>') != -1 or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">The video call ended because the connection was lost</div>') != -1 or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">The video call ended because the computer went to sleep.</div>') != -1))) or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find("You can't join this video call</div>") != -1 or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find("You aren't allowed to join this video call</div>") != -1)) or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div class="jtEd4b">Sorry, we encountered a problem joining this video call.') != -1):
                try:
                    during_meet.kill()
                    during_meet = None
                except Exception:
                    (1+1==3)
                time.sleep(1)
                driver.refresh()    
            while (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">You left the meeting</div>') != -1):
                try:
                    during_meet.kill()
                    during_meet = None
                except Exception:
                    (1+1==3)
                driver.refresh()
                continue
            try:
                try:
                    joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton1Path)))
                except:
                    joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton2Path)))
                if BROWSER_DRIVER.lower().startswith("chrome"):
                    time.sleep(1)
                action.send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
                joinButton.click()
                during_meet = KThread(target=duringMeet)
                # print("\n Thread Started")
                during_meet.start()
                continue
            except Exception as err:
                #print(err)
                continue
        except Exception as err:
            continue
        

def attendMeet():
    print(f"\n\nNavigating to Google Meet #{meetIndex}...", end="")
    driver.get(meetingInfo[0])

    print(colored(" Success!", "green"))
    print(f"Entering Google Meet #{meetIndex}...", end="")
    while endTime - datetime.now() > timedelta(seconds=0):
        while (not connect()):
            driver.refresh()
            time.sleep(1)
        time.sleep(1)
        while (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<p><b>429.</b> <ins>That\'s an error.</ins></p>') != -1):
            try:
                during_meet.kill()
                during_meet = None
            except Exception:
                (1+1==3)
            time.sleep(1)
            # print("429 Error")
            driver.get(meetingInfo[0])
        while (((wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">Your meeting code has expired</div>') != -1 or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">There was a problem joining this video call</div>') != -1) or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div class="jtEd4b">You can\'t create a meeting yourself.') != -1 and not wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('your teacher to join and then refresh this page.</div>') != -1)) or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find("<div class=\"jtEd4b\">This call has ended</div>") != -1):
            try:
                during_meet.kill()
                during_meet = None
            except Exception:
                (1+1==3)
            time.sleep(1)
            # print("Expired Meeting")
            driver.get(meetingInfo[0])
        while (((((wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div class="jtEd4b">You can\'t create a meeting yourself.') != -1 and wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('your teacher to join and then refresh this page.</div>') != -1) or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">This meeting hasn\'t started yet</div>') != -1) or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">Someone has removed you from the meeting</div>') != -1 or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">The video call ended because the connection was lost</div>') != -1 or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div jsname="r4nke" class="CRFCdf">The video call ended because the computer went to sleep.</div>') != -1))) or (wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find("You can't join this video call</div>") != -1 or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find("You aren't allowed to join this video call</div>") != -1)) or wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, "body"))).get_attribute("innerHTML").find('<div class="jtEd4b">Sorry, we encountered a problem joining this video call.') != -1):
            try:
                during_meet.kill()
                during_meet = None
            except Exception:
                (1+1==3)
            time.sleep(1)
            # print("Meeting not yet created/started")
            driver.refresh()
        try:
            joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton1Path)))
        except:
            joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton2Path)))
        if BROWSER_DRIVER.lower().startswith("chrome"):
            time.sleep(1)
            action.send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
        joinButton.click()
        leave_checker = KThread(target=leave_check)
        leave_checker.start()
        during_meet = KThread(target=duringMeet)
        during_meet.start()
        break

    print(colored(" Success!", "green"))
    time.sleep(1)
    print(colored(f"Now attending Google Meet #{meetIndex} @{timeStamp()}", "green"), end="")

    try:
        joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton1Path)))   # For another prompt that pops up for Meets being recorded
        time.sleep(1)
        joinButton.click()
    except:
        pass


def endMeet():
    try:
        during_meet.kill()
        during_meet = None
    except Exception:
        (1+1==3)
    try:
        endButton = driver.find_element_by_css_selector(endButtonPath)
        endButton.click()
    except Exception:
        (1+1==3)
    time.sleep(1)
    driver.get("https://meet.google.com/")
    print(colored(f"\nSuccessfully ended Google Meet #{meetIndex} @{timeStamp()}\n", "red"), end="")

def sendMessage(message):
    print(colored("Sending Message.... ", "yellow"), end="")
    if(endTime - datetime.now() > timedelta(seconds=0)):
        wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, '[aria-label="Chat with everyone"]'))).click()
        time.sleep(1)
        wait.until(when.element_to_be_clickable((by.CSS_SELECTOR, 'textarea'))).send_keys(str(message))
        driver.execute_script('document.querySelector(\'div[data-tooltip="Send message"]\').removeAttribute("disabled");')
        driver.execute_script('document.querySelector(\'div[data-tooltip="Send message"]\').removeAttribute("aria-disabled");')
        driver.execute_script('document.querySelector(\'div[data-tooltip="Send message"]\').click();')
        driver.find_element_by_css_selector('[aria-label="Close"]').click()
        print(colored(" Sent!", "green"))
    else:
        print(colored(" Past time.", "red"))

def duringMeet():
    # print("\nRecording sequence initiated")
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    try:
        fileName = 10000
        while (endTime - datetime.now() > timedelta(seconds=0)):
            # Recording Audio
            p = pyaudio.PyAudio()
            WAVE_OUTPUT_FILENAME = "audio_"+str(fileName)+".wav"
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            # print("\n* recording")
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            # print("\n* done recording")
            stream.stop_stream()
            stream.close()
            p.terminate()
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            try:
                filename = WAVE_OUTPUT_FILENAME
                r = sr.Recognizer()
                with sr.AudioFile(filename) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data)
                    # print('I think they said: ' + text)
                os.remove(WAVE_OUTPUT_FILENAME)
                #In target_text give bunch of your name in different way
                #output=[ "what response you want"]
                for wordIndex, (jsonWords, responses) in enumerate(SPEECH_RESPONSES.items(), start=1):
                    # print(jsonWords)
                    target_text = json.loads(jsonWords)
                    # print(target_text)
                    choice = random.choice(responses)
                    for target in target_text:
                        # print(str(target))
                        if (target.lower() in text.lower()):
                            print(colored("\nKeyword detected!", "green"))
                            print("The following keyword was detected: " + target)
                            print("The folloing response will be generated: " + choice)
                            sendMessage(choice)
            except Exception as exception:
                # traceback.print_exc()
                continue

            fileName+=1
    except Exception as fatal_err:
        print(colored("\nFatal error occured during execution.\nMore details can be found below: ", "red"))
        traceback.print_exc()
        print(colored("Please restart the application for further use. ", "red"))

def genericError():
    # clrscr()
    print(colored(" Failed!", "red"), end="")
    print("\n\nPossible fixes:\n")
    print("1.1 Make sure you have downloaded the latest version of MeetNinja from the GitHub page (every new iteration brings fixes and new capabilities)")
    print("1.2 Make sure you have pip-installed all the required python packages mentioned in the README")
    print("1.3 UNIX-based systems (Linux / Mac): Make sure you have given all the contents of MeetNinja the correct permissions (eg: 'chmod 777 ./ -R')")
    print("2.1 Check your inputs and run MeetNinja again (make sure there are no leading zeros in the Meet start times)")
    print("2.2 And / Or make sure you have chosen the correct webdriver file respective of your web browser and operating system")
    print("3. Make sure the generated web browser is not \"Minimized\" while MeetNinja is working")
    print("4.1. Make sure the webdriver file is of the latest stable build (https://chromedriver.chromium.org/ or https://github.com/mozilla/geckodriver/releases)")
    print("4.2. And / Or make sure your chosen web browser is updated to the latest version")
    print("4.3. And / Or make sure the webdriver file is at least of the same version as your chosen web browser (or lower)")
    print("5. Make sure the small \"time.sleep()\" delays (in seconds) in the login() and attendMeet() functions are comfortable for your internet speed")
    print("6. Make sure your internet connection is stable throughout the process")
    print("\nPress Enter to exit.")
    input()
    try:
        driver.quit()
    except:
        pass


def clrscr():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')
    printBanner()


def hibernate():
    print("\nHibernating in 10 seconds. Press Ctrl + C to abort.")
    time.sleep(13)
    _ = os.system('shutdown /h /f')


############### Main ###############

if __name__ == "__main__":

    printBanner()

    versionCheck()

    try:
        driver = initBrowser()
        wait = webdriver.support.ui.WebDriverWait(driver, 7)
        action = ActionChains(driver)
        meetNo = 1
        for meetIndex, (jsonTime, meetingInfo) in enumerate(MEETS.items(), start=1):
            startTime = datetime.strptime(jsonTime[0:24], "%Y-%m-%dT%H:%M:%S.%fZ")
            if (meetIndex <= 1):
                print(colored(f"Waiting until first Meet start time [{jsonTime}]...", "yellow"), end="")
            else:
                print(colored(f"\n\nWaiting until next Meet start time [{jsonTime}]...", "yellow"), end="")
            utc_offset = datetime.fromtimestamp(10000) - datetime.utcfromtimestamp(10000)
            startTime = startTime + utc_offset
            endTime = startTime + timedelta(minutes=meetingInfo[1])
            if(datetime.now() - startTime < timedelta(seconds=0)):
                  pause.until(startTime)
            elif(datetime.now() - startTime >= timedelta(seconds=0) and endTime - datetime.now() > timedelta(seconds=0)):
                  (1+1==2) # And that's a fact
            elif(datetime.now() - endTime >= timedelta(seconds=0)):
                  print(colored(" Past time.","red"))
                  continue
            print(colored(" Started!", "green"))
            if (meetNo <= 1):
                login()
            attendMeet()
            time.sleep(0.5)
            driver.refresh()
            pause.until(endTime)
            endMeet()
            meetNo += 1
        print("\n\nAll Meets completed successfully.")
        # hibernate()
        # Uncomment above to hibernate after a 10 second countdown upon completion of all Meets (Ctrl + C to abort hibernation)
        print("Press Enter to exit.")
        input()
        print("\nCleaning up and exiting...", end="")
        driver.quit()

    except KeyboardInterrupt:
        # clrscr()
        print("\n\nCTRL ^C\n")
        print(colored("User interrupted execution of program.", "red"))
        print("Press Enter to exit.")
        input()
        print("\nCleaning up and exiting...", end="")
        driver.quit()
    except Exception as err:
        traceback.print_exc()
        # Uncomment above to display error traceback (use when reporting issues)
        genericError()
