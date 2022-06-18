# https://github.com/Quattro04
# 05/13/2022

import subprocess
from cv2 import log
import pyautogui
import pydirectinput
import os
import time
import random
import sys

# Settings:
# Stay signed in
# Borderless
# HUD Scale: 0
# Shop Scale: 44
# Minimap Scale: 100
# Minimap on right
# Auto Attack: Enabled
# Default keybindings
# Quick Cast All (no indicator)
# Colorblind mode off

# customizable:
client_dir = "C:/Riot Games/League of Legends/LeagueClient.exe"

# only change if broken
client_process = "LeagueClient.exe"
game_process = "League of Legends.exe"
states = ["queue", "champ select", "loading", "game", "post"]
state = states[0]
nexus = [1860, 720]
images = {
    "accept": "images/accept button.png",
    "addBot": "images/add_bot.png",
    "again": "images/play again button.png",
    "beginner": "images/beginner.png",
    "choose": "images/choose.png",
    "clash": "images/got it.png",
    "coop": "images/coop.png",
    "confirm": "images/confirm.png",
    "custom": "images/custom.png",
    "death": "images/game/death.png",
    "free": "images/free champ.png",
    "honor": "images/honor.png",
    "midlane": "images/game/midlane.png",
    "missions": "images/missions.png",
    "nexus": "images/nexus.png",
    "ok": "images/ok.png",
    "play": "images/play button.png",
    "pick": "images/lock in.png",
    "qing": "images/in q.png",
    "queue": "images/find match.png",
    "select": "images/select.png",
    "startGame": "images/start_game.png",
    "win": "images/continue.png",
}


# https://stackoverflow.com/questions/7787120/check-if-a-process-is-running-or-not-on-windows-with-python
def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


def click(loc, delay=0.2, button="left"):
    pyautogui.moveTo(x=loc[0], y=loc[1], duration=delay, tween=pyautogui.easeInSine)
    pydirectinput.mouseDown(None, None, button)
    time.sleep(0.05)
    pydirectinput.mouseUp(None, None, button)

def click_button(image, delay=0.2, timeout=5, button="left", confidence=0.8):
    start_time = time.time()
    loc = None
    while time.time() - start_time < timeout:
        loc = pyautogui.locateCenterOnScreen(image=image, confidence=confidence, grayscale=True)
        if loc is not None:
            break
    if loc is None:
        print("No button matching image " + image + " was found. Continuing...")
        return False
    click(loc, delay, button)
    print("Button matching image " + image + " was found.")
    return True


def open_client():
    global state
    if process_exists(client_process):
        print('da')
        # os.system(str("taskkill /IM " + client_process + " /F"))
    if process_exists(game_process):
        state = "game"
        return
        # os.system(str("taskkill /IM " + game_process + " /F"))
    os.startfile(client_dir)


def make_lobby():
    print("Making lobby.")
    global state
    if (click_button(images.get("play")) and click_button(images.get("coop"))
            and click_button(images.get("beginner")) and click_button(images.get("confirm"))):
        state = states[0]
        return True
    else:
        pyautogui.click()
        if (click_button(images.get("coop"))
                and click_button(images.get("beginner")) and click_button(images.get("confirm"))):
            state = states[1]
            return True
    print("Unable to make lobby.")
    return False

def make_lobby_custom():
    print("Making custom lobby.")
    global state
    if (click_button(images.get("play")) and click_button(images.get("custom"))
        and click_button(images.get("confirm")) and click_button(images.get("startGame"))):
        state = states[0]
        return True
    else:
        pyautogui.click()
        if (click_button(images.get("coop"))
                and click_button(images.get("beginner")) and click_button(images.get("confirm"))):
            state = states[0]
            return True
    print("Unable to make lobby.")
    return False

def queue(timeout=120):
    while click_button(images.get("queue")):
        print("Attempting to start queue.")
    start_time = time.time()
    print("Queue successfully started at: " + str(start_time))
    global state
    while time.time() - start_time < timeout:
        if click_button(images.get("accept")):
            start_time = time.time()
            while time.time() - start_time < 15:
                if pyautogui.locateOnScreen(image=images.get("free"), confidence=0.8, grayscale=True) is not None:
                    state = states[1]
                    return True
                if pyautogui.locateOnScreen(image=images.get("choose"), confidence=0.8, grayscale=True) is not None:
                    state = states[1]
                    return True
        if pyautogui.locateOnScreen(image=images.get("choose"), confidence=0.8, grayscale=True) is not None:
            state = states[1]
            return True
    if pyautogui.locateOnScreen(image=images.get("choose"), confidence=0.8, grayscale=True) is not None or \
            process_exists(game_process):
        state = states[1]
        return True
    print("Queue timed out.")
    return False


def champ_select():
    print("Selecting champion.")
    time.sleep(1)
    global state
    free_champs = pyautogui.locateAllOnScreen(image=images.get("free"), confidence=0.8, grayscale=True)
    for champ in free_champs:
        champ = [champ[0] - 20, champ[1] + 20]
        click(champ, 0.25)
        if click_button(image=images.get("pick"), delay=0):
            state = states[2]
            return True
    click(loc=[700, 350])
    if click_button(image=images.get("pick"), delay=0):
        state = states[2]
        return True
    print("No champions found in champ select.")
    return False


def loading_screen(timeout=420):
    print("Waiting for game to start.")
    start_time = time.time()
    while time.time() - start_time < timeout:
        nexus_loc = pyautogui.locateOnScreen(image=images.get("nexus"), confidence=0.8, grayscale=True)
        if nexus_loc is not None:
            global nexus, state
            # if abs(nexus_loc[0] - nexus[0]) > 100 or abs(nexus_loc[1] - nexus[1]) > 100:
            #     nexus = [nexus_loc[0], nexus_loc[1]]
            state = states[3]
            return True
    print("Loading screen timed out.")
    return False

def buyDoranShieldAndPotion():
    pydirectinput.press("p")
    pydirectinput.keyDown("ctrl")
    pydirectinput.press("l")
    pydirectinput.keyUp("ctrl")
    pydirectinput.write("dor")
    pydirectinput.press("enter")
    pydirectinput.keyDown("ctrl")
    pydirectinput.press("l")
    pydirectinput.keyUp("ctrl")
    pydirectinput.write("potion")
    pydirectinput.press("enter")
    pydirectinput.press("p")

def gotoMidLane():
    # counter = 5
    # pyautogui.mouseDown(button='right')
    # while counter > 0:
    #     pyautogui.moveTo(x=1920 * (0.55 + (random.random()*0.05)), y=1080 * (0.3 + (random.random()*0.05)), duration=0.2)
    #     counter -= 1
    #     time.sleep(3)
    # pyautogui.mouseUp(button='right')

    click_button(images.get("midlane"), button="right")
    time.sleep(10)
    return

def useAbilities():
    pydirectinput.keyDown("ctrl")
    pydirectinput.press("q")
    pydirectinput.press("w")
    pydirectinput.press("e")
    pydirectinput.press("r")
    pydirectinput.keyUp("ctrl")
    time.sleep(1)
    pydirectinput.press("q")
    time.sleep(1)
    pydirectinput.press("w")
    time.sleep(1)
    pydirectinput.press("e")
    time.sleep(1)
    return

def game():
    time.sleep(1)
    pydirectinput.press("y")

    print("BUYING ITEMS")
    buyDoranShieldAndPotion()

    print("WATING FOR BARRIERS TO GO DOWN")
    time.sleep(10)

    print("GOING TO TOP LANE")
    click([1436, 775], 0.2, "right")

    print("WAITING FOR MINIONS")

    time.sleep(60)

    lane = 0
    idleCounter = 0
    first = True
    while not click_button(image=images.get("win")):
        
        if first:
            first = False
        else:
            lane = random.randint(0, 6)

        if lane == 0:
            print("ATTACKING TOP LANE")
            pydirectinput.press("a")
            click([1457, 742])
        elif lane == 1:
            print("ATTACKING MID LANE")
            pydirectinput.press("a")
            click([1514, 803])
        elif lane == 2:
            print("ATTACKING BOT LANE")
            pydirectinput.press("a")
            click([1570, 870])
        elif lane == 3:
            print("ATTACKING WOLVES")
            pydirectinput.press("a")
            click([1468, 817])
        elif lane == 4:
            print("ATTACKING WRAITHS")
            pydirectinput.press("a")
            click([1502, 829])
        elif lane == 5:
            print("ATTACKING GOLEMS")
            pydirectinput.press("a")
            click([1518, 860])
        elif lane == 6:
            print("ATTACKING FROG")
            pydirectinput.press("a")
            click([1447, 796])

        print("WAITING TO DIE")
        while not pyautogui.locateOnScreen(image=images.get("death"), confidence=0.8, grayscale=True):
            time.sleep(1)
            idleCounter += 1
            if idleCounter == 10 or idleCounter == 20:
                print("USING ABILITIES")
                useAbilities()
            if idleCounter > 30:
                break
        
        if idleCounter > 30:
            print("IDLE COUNTER, RESETTING")
            idleCounter = 0
            continue

        idleCounter = 0
        print("DETECTED DEATH, WAITING TO RES")
        while pyautogui.locateOnScreen(image=images.get("death"), confidence=0.8, grayscale=True):
            time.sleep(1)

        print("RESURECTED, RESTARTING")

        # pyautogui.click(x=1920 * (0.55 + (random.random()*0.1)), y=1080 * (0.15 + (random.random()*0.3)), duration=0.2)

        # pyautogui.rightClick(x=1920 * (0.25 + (random.random()*0.1)), y=1080 * (0.65 + (random.random()*0.1)), duration=0.2, tween=pyautogui.easeInSine)

        # if time.time() - start_time < 600:
        #     click(loc=[nexus[0] + 10 * random.random() - 150, nexus[1] + 10 * random.random() + 150])
        # else:
        #     click(loc=[nexus[0] + 10 * random.random(), nexus[1] + 10 * random.random()])
        # time.sleep(random.random())
        # if random.random() > 0.75:
        #     pyautogui.moveTo(x=1160, y=300, duration=0.05, tween=pyautogui.easeInSine)
        #     pydirectinput.press("e")
        #     pydirectinput.press("w")
        #     pydirectinput.press("q")
        # if random.random() > 0.95:
        #     pyautogui.moveTo(x=1160, y=300, duration=0.05, tween=pyautogui.easeInSine)
        #     pydirectinput.press("r")
        #     pydirectinput.press("d")
        #     pydirectinput.press("f")
        # pydirectinput.keyDown("ctrl")
        # pydirectinput.press("r")
        # pydirectinput.press("q")
        # pydirectinput.press("w")
        # pydirectinput.press("e")
        # pydirectinput.keyUp("ctrl")
        # if time.time() - timer > 3:
        #     pydirectinput.press("p")
        #     pydirectinput.keyDown("ctrl")
        #     pydirectinput.press("l")
        #     pydirectinput.keyUp("ctrl")
        #     pydirectinput.press("enter")
        #     pydirectinput.press("p")
        #     timer = time.time()
    global state
    state = states[4]
    return True


def post_game():
    start_time = time.time()
    honor_loc = None
    while time.time() - start_time < 10:
        pyautogui.click()
        honor_loc = pyautogui.locateCenterOnScreen(image=images.get("honor"), confidence=0.8, grayscale=True)
        if honor_loc is not None:
            click(loc=honor_loc)
            break
    if honor_loc is None:
        pyautogui.click()
    start_time = time.time()
    while not click_button(image=images.get("again"), timeout=1):
        click_button(image=images.get("ok"), timeout=10)
        if time.time() - start_time > 60:
            print("Post game lobby timed out.")
            return False
    global state
    state = states[0]
    return True


# restarts the game if there is an erroropen_client
def fail_safe(tries=5, timeout=90):
    print("Starting game...")
    global state
    state = None
    open_client()
    start_time = time.time()
    while tries > 0:
        if process_exists(client_process):
            if pyautogui.locateOnScreen(image=images.get("play"), confidence=0.8, grayscale=True) is not None:
                if len(sys.argv) > 1 and sys.argv[1] == "custom":
                    make_lobby_custom()
                else:
                    make_lobby()
            return
        else:
            if pyautogui.locateOnScreen(image=images.get("nexus"), confidence=0.8, grayscale=True) is not None:
                state = "game"
                return
            missions = pyautogui.locateOnScreen(image=images.get("missions"), confidence=0.8, grayscale=True)
            if missions is not None:
                pyautogui.moveTo(x=missions[0], y=missions[1] + 300)
                click_button(image=images.get("select"))
                time.sleep(1)
                click_button(image=images.get("ok"))
            else:
                click_button(image=images.get("clash"))
        if time.time() - start_time > timeout:
            start_time = time.time()
            tries -= 1
            open_client()
            print("Failed to load client. Retrying...")
    exit("Failed to load client (patching?).")


def read_config():
    config = open("config.txt")
    if config.readline().lower()[8:].strip() != "true":
        config.close()
        return
    print("Loading config...")
    global client_dir
    client_dir = config.readline()[14:].strip()
    config.close()


read_config()
if pyautogui.locateOnScreen(image=images.get("nexus"), confidence=0.8, grayscale=True) is not None:
    state = "game"
else:
    fail_safe()
while True:
    worked = True
    if state == "queue":
        worked = queue()
    elif state == "champ select":
        worked = champ_select()
    elif state == "loading":
        worked = loading_screen()
    elif state == "game":
        worked = game()
    elif state == "post":
        worked = post_game()
    else:
        worked = False
    if not worked:
        print("FATAL ERROR! Attempting fail safe measures...")
        fail_safe()
