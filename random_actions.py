import win32com.client as wincom
import random
import threading

walk_actions = [
    "順時針繞圈走",
    "逆時針繞圈走",
    "8字走",
    "隨意走動",
    "直線來回走",
    "原地 走"
]

walk_speeds = [
    "用一般速度",
    "慢速",
    "用一般速度拿手機",
    "慢速拿手機"
]

static_actions = [
    "站立不動",
    "左右揮手",
    "前後伸手",
    "手畫8字",
    "手畫圈",
    "手隨意揮動"
]

static_speeds = [
     "用一般速度",
     "快速",
     "慢速"
]

start_walk = ""
stop_walk = "停下來，"




class RandomActions():    
    def __init__(self,time=300):
        self.speak = wincom.Dispatch("SAPI.SpVoice")
        self.time = time
        self.action_list = []
        self.current_action = 1
        

    def randomize_action(self):
        total_time = 0
        walking = True
        action = 1
        speed = 0

        # first action: walk normally
        action_time = random.randint(2,6)*10
        self.action_list.append([total_time, walking, action, speed, "用一般速度逆時針繞圈走", action_time])
        total_time += action_time

        while total_time < (self.time - 20):
            action_added = False
            while not action_added:
                action_time = random.randint(2,6)*10
                new_walking = random.random() < 0.5
                action_text = ""
                change_walk = False

                if new_walking != walking:
                    change_walk = True
                    if new_walking:
                        action_text += start_walk
                    else:
                        action_text += stop_walk

                walking = new_walking

                if new_walking:
                    # walk actions
                    new_action = action
                    new_speed = speed

                    if not change_walk:
                        while new_action == action and new_speed == speed:
                            new_action =  random.randint(0,len(walk_actions)-1)
                            new_speed =  random.randint(0,len(walk_speeds)-1)
                    else:
                            new_action =  random.randint(0,len(walk_actions)-1)
                            new_speed =  random.randint(0,len(walk_speeds)-1)


                    action = new_action
                    speed = new_speed

                    action_text += walk_speeds[new_speed]
                    action_text += walk_actions[new_action]

                else:
                    # static actions
                    new_action = action
                    new_speed = speed

                    if not change_walk:
                        while new_action == action and new_speed == speed:
                            new_action =  random.randint(0,len(static_actions)-1)
                            if new_action == 0:
                                 new_speed = 0
                            else:
                                new_speed =  random.randint(0,len(static_speeds)-1)
                    else:
                            new_action =  random.randint(0,len(static_actions)-1)
                            if new_action == 0:
                                 new_speed = 0
                            else:
                                new_speed =  random.randint(0,len(static_speeds)-1)

                    action = new_action
                    speed = new_speed

                    if new_action != 0:
                        action_text += static_speeds[new_speed]
                    action_text += static_actions[new_action]

                # check if consective 3 walk/static actions
                if len(self.action_list) >= 2:
                    if self.action_list[-1][1] == self.action_list[-2][1] == walking:
                        continue

                # check if duplicate
                last = self.action_list[-1]
                if last[1] == walking and last[2] == action and last[3] == speed:
                    continue

                # consecutive hand actions should not exceed 100s
                if last[1] == False and last[2] != 0:
                    if last[5] + action_time > 100:
                        continue

                action_added = True

            self.action_list.append([total_time, walking, action, speed, action_text, action_time])
            total_time += action_time

    def generate_csv(self,file_path=""):
        csv_str = "Time,Walking,Action,Speed,Text\n"
        for a in self.action_list:
            csv_str += f"{a[0]},{a[1]},{a[2]},{a[3]},{a[4]}\n"

        if file_path != "":
            with open(file_path,"w") as f:
                f.write(csv_str)  

        return csv_str
    
    def voice_action(self, write_time):
        def voice(text):
            self.speak.Speak(text)
    
        if self.current_action < len(self.action_list):
            action = self.action_list[self.current_action]
            action_time = action[0]
            if write_time >= action_time:
                threading.Thread(target=voice,args=(action[4],)).start()
                self.current_action += 1