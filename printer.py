import tkinter
import hbcvt
import numpy as np
import math
import serial
import time
import queue
import turtle
import pyautogui
import pytesseract
import cv2
from PIL import Image

###점자 관련

R = 1.5 / 2
R_TO_R = 2.5
B_TO_B_X = 4.5
B_TO_B_Y = 5
Z_AXIS = 0.6
PAPER_X = 210
PAPER_Y = 297
X_TOL = 10
Y_TOL = 10
B_SIZE = np.array([R_TO_R + B_TO_B_X, 2 * R_TO_R + B_TO_B_Y])
MAX_X_LINE = math.floor((PAPER_X - 2 * X_TOL) / B_SIZE[0]) - 2
MAX_Y_LINE = math.floor((PAPER_Y - 2 * Y_TOL) / B_SIZE[1])
l = 3
INIT_LOC = np.array([2 * MAX_X_LINE - 1, 0])

spec_coin = 0
alphabet_coin = 0
st_coin = 0

mac_list1 = ['것', '을', '은', '인', '옹']
mac_br1 = [[[0, 0, 0, 1, 1, 1], [0, 1, 1, 1, 0, 0]],
          [[0, 1, 1, 1, 0, 1]],
          [[1, 0, 1, 0, 1, 1]],
          [[1, 1, 1, 1, 1, 0]],
          [[1, 1, 1, 1, 1, 1]]]
mac_list2 = ['그래서', '그러나', '그러면', '그러므로', '그런데', '그리고', '그리하여']
mac_br2 = [[[1, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0]],
          [[1, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0]],
          [[1, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 0]],
          [[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1]],
          [[1, 0, 0, 0, 0, 0], [1, 0, 1, 1, 1, 0]],
          [[1, 0, 0, 0, 0, 0], [1, 0, 1, 0, 0, 1]],
          [[1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 1]]]

spec_list = ['(', ')', '-', '~']
spec_br = [[[0, 0, 1, 0, 0, 1]],
           [[0, 0, 1, 0, 0, 1]],
           [[0, 0, 1, 0, 0, 1]],
           [[0, 0, 1, 0, 0, 1], [0, 0, 1, 0, 0, 1]]]
st_list = ['ㅃ', 'ㅉ', 'ㄸ', 'ㄲ', 'ㅆ']

def find_specific_str(s, ss):
    i = 0
    return_list1 = []
    while True:
        k = s.find(ss, i)
        if  k != -1:
            return_list1.append(s[i: k])
            return_list1.append(ss)
            i = k + len(ss)
        if s.find(ss, i) == -1:
            return_list1.append(s[i:])
            break
    return_list2 = []
    for i in return_list1:
        if i != '':
            return_list2.append(i)
    return return_list2

def refine_str(input_str):
    vol_result = []
    
    """공백문자 처리"""
    
    result = find_specific_str(input_str, ' ')
    
    """숫자 처리"""
    
    for i in range(len(result)):
        number_coin = 0    # 상태 숫자 = 1 , 문자 = 0
        number_state = False
        for j in range(len(result[i])):
            if j == 0:
                number_state = result[i][j].isdigit()
            if number_state != result[i][j].isdigit():
                vol_result.append(result[i][number_coin: j])
                number_state = result[i][j].isdigit()
                number_coin = j
            if j == len(result[i]) - 1:
                vol_result.append(result[i][number_coin: j + 1])
                
    result = vol_result
    vol_result = []
    
    """엔터 처리"""
    
    for i in range(len(result)):
        vol_list = find_specific_str(result[i], '\n')
        for j in range(len(vol_list)):
            vol_result.append(vol_list[j])
            
    result = vol_result
    vol_result = []
    
    """매크로1 처리"""
    
    for k1 in range(len(mac_list1)):
        vol_result = []
        for i in range(len(result)):
            vol_list = find_specific_str(result[i], mac_list1[k1])
            for j in range(len(vol_list)):
                vol_result.append(vol_list[j])
        result = vol_result
    
    result = vol_result
    vol_result = []
    
    """매크로2 처리"""
    
    for k2 in range(len(mac_list2)):
        vol_result = []
        for i in range(len(result)):
            vol_list = find_specific_str(result[i], mac_list2[k2])
            for j in range(len(vol_list)):
                vol_result.append(vol_list[j])
        result = vol_result
    
    result = vol_result
    vol_result = []
    
    """특수문자 처리"""
    
    for k3 in range(len(spec_list)):
        vol_result = []
        for i in range(len(result)):
            vol_list = find_specific_str(result[i], spec_list[k3])
            for j in range(len(vol_list)):
                vol_result.append(vol_list[j])
        result = vol_result
    
    result = vol_result
    vol_result = []
    
    return result

def interpreter(input_str):
    result = []
    vol_result = []
    
    if input_str == ' ':
        vol_result.append([0, 0, 0, 0, 0, 0])
    
    elif input_str in mac_list1:
        for i in mac_br1[mac_list1.index(input_str)]:
            vol_result.append(i)
    
    elif input_str in mac_list2:
        for i in mac_br2[mac_list2.index(input_str)]:
            vol_result.append(i)
        
    elif input_str[0].isdigit():
        vol_hbcvt = hbcvt.h2b.text(input_str)
        vol_result.append([0, 0, 1, 1, 1, 1])
        for i in range(len(vol_hbcvt)):
            for j in range(len(vol_hbcvt[i][1])):
                vol_result.append(vol_hbcvt[i][1][j][1][1])
            
    elif input_str[0].isalpha():
        vol_hbcvt = hbcvt.h2b.text(input_str)
        for i in range(len(vol_hbcvt)):
            for j in range(len(vol_hbcvt[i][1])):
                for k in range(len(vol_hbcvt[i][1][j][1])):
                    vol_result.append(vol_hbcvt[i][1][j][1][k])
                    
    elif input_str in spec_list:
        for i in spec_br[spec_list.index(input_str)]:
            vol_result.append(i)
    
    elif input_str[0] == '\n':
        vol_result.append(['#1'])
    
    else:
        vol_hbcvt = hbcvt.h2b.text(input_str)
        for i in range(len(vol_hbcvt)):
            for j in range(len(vol_hbcvt[i][1])):
                for k in range(len(vol_hbcvt[i][1][j][1])):
                    vol_result.append(vol_hbcvt[i][1][j][1][k])
    
    result = vol_result
    vol_result = []
    
    return result

def interpreter_to_a4(br_result, input_set, cursor):
    vol_br_paper = br_result
    vol_cursor = cursor
    max_y, max_x = vol_br_paper.shape
    for i in range(len(input_set)):
        for j in range(len(input_set[i])):
            if input_set[i][j][0] == '#1':
                vol_cursor = [0, vol_cursor[1] + 3]
            else:
                if vol_cursor[0] == max_x:
                    vol_cursor = [0, vol_cursor[1] + 3]

                vol_br_paper[vol_cursor[1]][vol_cursor[0]] = input_set[i][j][0]
                vol_cursor = [vol_cursor[0], vol_cursor[1] + 1]
                vol_br_paper[vol_cursor[1]][vol_cursor[0]] = input_set[i][j][1]
                vol_cursor = [vol_cursor[0], vol_cursor[1] + 1]
                vol_br_paper[vol_cursor[1]][vol_cursor[0]] = input_set[i][j][2]
                vol_cursor = [vol_cursor[0] + 1, vol_cursor[1] - 2]
                vol_br_paper[vol_cursor[1]][vol_cursor[0]] = input_set[i][j][3]
                vol_cursor = [vol_cursor[0], vol_cursor[1] + 1]
                vol_br_paper[vol_cursor[1]][vol_cursor[0]] = input_set[i][j][4]
                vol_cursor = [vol_cursor[0], vol_cursor[1] + 1]
                vol_br_paper[vol_cursor[1]][vol_cursor[0]] = input_set[i][j][5]
                vol_cursor = [vol_cursor[0] + 1, vol_cursor[1] - 2]
    return cursor, br_result

def a4_to_block(br_result):
    return_list = np.zeros((MAX_Y_LINE, MAX_X_LINE))
    for i in range(MAX_Y_LINE):
        for j in range(MAX_X_LINE):
            if not br_result[3 * i: 3 * i + 3, 2 * j: 2 * j + 2].any():
                return_list[i][j] = 0
            else:
                return_list[i][j] = 1
    return return_list

def return_two_end_points(input_list):
    st_point = 0
    end_point = len(input_list)
    st_token = 0
    end_token = 0
    for i in range(end_point):
        if input_list[i] != 0 and st_token == 0:
            st_point = i
            st_token = 1
        if input_list[len(input_list) - 1 - i] != 0 and end_token == 0:
            end_point = len(input_list) - 1 - i
            end_token = 1
    if st_token == 0 and end_token == 0:
        return -1, -1
    else:
        return st_point, end_point

def find_edge(input_list):
    return_list = []
    for i in range(len(input_list)):
        vol_list = []
        st_point, end_point = return_two_end_points(input_list[i])
        if st_point != -1 and end_point != - 1:
            vol_list.append(i)
            vol_list.append(st_point)
            vol_list.append(end_point)
            return_list.append(vol_list)
    return_list = np.array(return_list)
    return return_list

def direction_mov(init_block, next_block):
    init_block = np.array(init_block)
    next_block = np.array(next_block)
    if init_block[0] + 1 == next_block[0] and init_block[0] % 2 == 0:
        return 'r'
    elif init_block[0] + 1 == next_block[0] and init_block[0] % 2 == 1:
        return 'R'
    elif init_block[0] - 1 == next_block[0] and init_block[0] % 2 == 0:
        return 'L'
    elif init_block[0] - 1 == next_block[0] and init_block[0] % 2 == 1:
        return 'l'
    elif init_block[1] + 1 == next_block[1] and init_block[1] % 3 == 0:
        return 'd'
    elif init_block[1] + 1 == next_block[1] and init_block[1] % 3 == 1:
        return 'd'
    elif init_block[1] + 1 == next_block[1] and init_block[1] % 3 == 2:
        return 'D'

def a4_to_serial(input_a4, cursor=np.array([0, 0])):
    return_serial = []
    vol_cursor = np.array(cursor)
    edge = find_edge(input_a4)
    y_num = 0
    state_token1 = 0

    """try start"""
    """initialize state"""
    if vol_cursor[1] == edge[y_num][0] and vol_cursor[0] == edge[y_num][1]:
        state_token1 = 1
    elif vol_cursor[1] == edge[y_num][0] and vol_cursor[0] == edge[y_num][2]:
        state_token1 = -1
    elif vol_cursor[1] == edge[y_num][0]:
        state_token1 = 3
    else:
        state_token1 = 4
    """initialize end"""

    while y_num < len(edge):

        if vol_cursor[1] == edge[y_num][0] and vol_cursor[0] == edge[y_num][1] and state_token1 == 0:
            state_token1 = 1

        elif vol_cursor[1] == edge[y_num][0] and vol_cursor[0] == edge[y_num][2] and state_token1 == 0:
            state_token1 = -1

        if state_token1 == 1:
            if input_a4[vol_cursor[1]][vol_cursor[0]] == 1:
                return_serial.append('p')
            if vol_cursor[0] < edge[y_num][2]:
                init_loc = vol_cursor
                new_loc = [vol_cursor[0] + 1, vol_cursor[1]]
                return_serial.append(direction_mov(vol_cursor, new_loc))
                vol_cursor = new_loc
            elif vol_cursor[0] == edge[y_num][2]:
                state_token1 = 4

        elif state_token1 == -1:
            if input_a4[vol_cursor[1]][vol_cursor[0]] == 1:
                return_serial.append('p')
            if vol_cursor[0] > edge[y_num][1]:
                init_loc = vol_cursor
                new_loc = [vol_cursor[0] - 1, vol_cursor[1]]
                return_serial.append(direction_mov(vol_cursor, new_loc))
                vol_cursor = new_loc
            elif vol_cursor[0] == edge[y_num][1]:
                state_token1 = 4

        elif state_token1 == 2:
            if vol_cursor[1] != edge[y_num][0]:
                init_loc = vol_cursor
                new_loc = [vol_cursor[0], vol_cursor[1] + 1]
                return_serial.append(direction_mov(vol_cursor, new_loc))
                vol_cursor = new_loc
            else:
                state_token1 = 3

        elif state_token1 == 3:
            if vol_cursor[0] - edge[y_num][1] < edge[y_num][2] - vol_cursor[0]:
                while vol_cursor[0] != edge[y_num][1]:
                    if vol_cursor[0] > edge[y_num][1]:
                        init_loc = vol_cursor
                        new_loc = [vol_cursor[0] - 1, vol_cursor[1]]
                        return_serial.append(direction_mov(vol_cursor, new_loc))
                        vol_cursor = new_loc
                    else:
                        init_loc = vol_cursor
                        new_loc = [vol_cursor[0] + 1, vol_cursor[1]]
                        return_serial.append(direction_mov(vol_cursor, new_loc))
                        vol_cursor = new_loc
            else:
                while vol_cursor[0] != edge[y_num][2]:
                    if vol_cursor[0] < edge[y_num][2]:
                        init_loc = vol_cursor
                        new_loc = [vol_cursor[0] + 1, vol_cursor[1]]
                        return_serial.append(direction_mov(vol_cursor, new_loc))
                        vol_cursor = new_loc
                    else:
                        init_loc = vol_cursor
                        new_loc = [vol_cursor[0] - 1, vol_cursor[1]]
                        return_serial.append(direction_mov(vol_cursor, new_loc))
                        vol_cursor = new_loc
            if vol_cursor[0] == edge[y_num][1] or vol_cursor[0] == edge[y_num][2]:
                state_token1 = 0

        elif state_token1 == 4:
            y_num += 1
            state_token1 = 2

        else:
            break
    """try end"""
    
    """except start"""
    """except end"""
    return return_serial

def draw(roman, direction):
    t.color('black')
    if roman == 'r':
        if direction == 0:
            t.forward(2.5 * l)
        elif direction == 1:
            t.right(180)
            t.forward(2.5 * l)
        elif direction == 2:
            t.right(90)
            t.forward(2.5 * l)
        elif direction == 3:
            t.left(90)
            t.forward(2.5 * l)
        return 1, 0, 0

    elif roman == 'R':
        if direction == 0:
            t.forward(4.5 * l)
        elif direction == 1:
            t.right(180)
            t.forward(4.5 * l)
        elif direction == 2:
            t.right(90)
            t.forward(4.5 * l)
        elif direction == 3:
            t.left(90)
            t.forward(4.5 * l)
        return 1, 0, 0

    elif roman == 'l':
        if direction == 0:
            t.right(180)
            t.forward(2.5 * l)
        elif direction == 1:
            t.forward(2.5 * l)
        elif direction == 2:
            t.left(90)
            t.forward(2.5 * l)
        elif direction == 3:
            t.right(90)
            t.forward(2.5 * l)
        return -1, 0, 1

    elif roman == 'L':
        if direction == 0:
            t.right(180)
            t.forward(4.5 * l)
        elif direction == 1:
            t.forward(4.5 * l)
        elif direction == 2:
            t.left(90)
            t.forward(4.5 * l)
        elif direction == 3:
            t.right(90)
            t.forward(4.5 * l)
        return -1, 0, 1

    elif roman == 'd':
        if direction == 0:
            t.right(90)
            t.forward(2.5 * l)
        elif direction == 1:
            t.left(90)
            t.forward(2.5 * l)
        elif direction == 2:
            t.right(180)
            t.forward(2.5 * l)
        elif direction == 3:
            t.forward(2.5 * l)
        return 0, 1, 3

    elif roman == 'D':
        if direction == 0:
            t.right(90)
            t.forward(5 * l)
        elif direction == 1:
            t.left(90)
            t.forward(5 * l)
        elif direction == 2:
            t.right(180)
            t.forward(5 * l)
        elif direction == 3:
            t.forward(5 * l)
        return 0, 1, 3
    
    elif roman == 'p':
        t.dot(1.5 * l, 'red')
        return 0, 0, -1

def ser(al, ard):
    ard.write(al.encode())
    y = ard.readline()
    print(y.decode())

########################################################################
#####GUI 관련

input_text = ''

root = tkinter.Tk()
root.title("Braille Printer")
root.geometry("1400x750")

#GUI용 글로벌 변수

gui_state = 0
text = ''
br_arr = np.zeros((3 * MAX_Y_LINE, 2 *MAX_X_LINE))
cursor = INIT_LOC
result_serial = []
port = 'COM4'
ard = serial.Serial(port, 9600)

#아두이노 최초동작
x = ard.readline()
print(x.decode())

#GUI 관련 함수

def initialize_global_var():
    global gui_state
    global text
    global br_arr
    global cursor
    global result_serial
    global port
    global ard
    text = ''
    br_arr = np.zeros((3 * MAX_Y_LINE, 2 *MAX_X_LINE))
    cursor = INIT_LOC
    result_serial = []

    cursor_txt.delete("1.0","end")
    cursor_txt.insert(tkinter.END, f"x:{cursor[0]}, y:{cursor[1]}")

def OCR():
    global gui_state
    global text
    global br_arr
    global cursor
    global result_serial
    global port
    global ard
    if gui_state == 0:
        main_txt.delete("1.0","end")
        gui_state = -1
        state_txt.insert(tkinter.END, "OCR reading...\n")
        
        pyautogui.click(x=1027, y=1059)
        time.sleep(5)
        pyautogui.screenshot('sc.jpg', region=(70, 50, 1700, 850))

        img = cv2.imread('sc.jpg')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
        cv2.imwrite('sc.jpg', img)

        pyautogui.click(x=1893, y=18)
        text = pytesseract.image_to_string(Image.open('sc.jpg'), lang='kor')

        OCR_box = pyautogui.locateCenterOnScreen('OCR.png')
        time.sleep(0.5)
        pyautogui.moveTo(x=OCR_box[0], y=OCR_box[1])
        pyautogui.moveTo()
        print(text)

        main_txt.insert(tkinter.END, text)

        state_txt.insert(tkinter.END, "OCR reading end...\n")
        gui_state = 0

def start_print():
    global gui_state
    global text
    global br_arr
    global cursor
    global result_serial
    global port
    global ard
    if gui_state == 0:
        gui_state = 1
        state_txt.insert(tkinter.END, "Print starting...\n")
        state_txt.insert(tkinter.END, "Initializing...\n")
        ser('h', ard)
        state_txt.insert(tkinter.END, "Initializing end...\n")
        text = main_txt.get("1.0", "300.300")
        print(text)
        state_txt.insert(tkinter.END, "Receive complete...\n")
        state_txt.insert(tkinter.END, "Data processing...\n")
        
        cursor = INIT_LOC
        cursor_txt.delete("1.0","end")
        cursor_txt.insert(tkinter.END, f"x:{cursor[0]}, y:{cursor[1]}")
        
        refine_text = refine_str(text)
        result_set = []
        for i in range(len(refine_text)):
            try:
                vol_interpreter = interpreter(refine_text[i])
                _ = vol_interpreter[0][0]
                result_set.append(vol_interpreter)
            except:
                _ = 0
        _, a4 = interpreter_to_a4(br_arr, result_set, [0, 0])
        a4 = np.flip(a4, axis=1)
        result_serial = a4_to_serial(a4, cursor)
        state_txt.insert(tkinter.END, "Data processing end...\n")
        state_txt.insert(tkinter.END, "Print on...\n")

        t.speed(10)
        t.pensize(0.5)
        direction = 0
        t.penup()
        t.goto(8 * cursor[0], MAX_Y_LINE * 3 - cursor[1])
        t.pendown()

        for i in range(len(result_serial)):
            if gui_state == 2:
                print('stop')
                break
            else:
                ser(result_serial[i], ard)
                dx, dy, k = draw(result_serial[i], direction)
                cursor = [cursor[0] + dx, cursor[1] + dy]
                cursor_txt.delete("1.0","end")
                cursor_txt.insert(tkinter.END, f"x:{cursor[0]}, y:{cursor[1]}")
                print(cursor)
                if k != -1:
                    direction = k

        if gui_state == 1:
            ser('o', ard)
            initialize_global_var()
            gui_state = 0
            state_txt.insert(tkinter.END, "Print end...\n")
    

def stop():
    global gui_state
    global text
    global br_arr
    global cursor
    global result_serial
    global port
    global ard
    if gui_state == 1:
        gui_state = 2
        state_txt.delete("1.0","end")
        state_txt.insert(tkinter.END, "Force quit...\n")
        initialize_global_var()
    
def front_print_out():
    global gui_state
    global text
    global br_arr
    global cursor
    global result_serial
    global port
    global ard
    if gui_state == 2:
        state_txt.insert(tkinter.END, "Front printing...\n")
        t.reset()
        t.pensize(0.5)
        t.penup()
        t.goto(8 * cursor[0], MAX_Y_LINE * 3 - cursor[1])
        t.pendown()
        ser('o', ard)
        gui_state = 0

def back_print_out():
    global gui_state
    global text
    global br_arr
    global cursor
    global result_serial
    global port
    global ard
    if gui_state == 2:
        state_txt.insert(tkinter.END, "Front printing...\n")
        t.reset()
        t.pensize(0.5)
        t.penup()
        t.goto(8 * cursor[0], MAX_Y_LINE * 3 - cursor[1])
        t.pendown()
        ser('O', ard)
        gui_state = 0

#버튼 위치 & 기능
OCR_btn = tkinter.Button(root, text="OCR", command=OCR)
OCR_btn.place(x=0, y=0, width=100, height=40)

print_btn = tkinter.Button(root, text="print", command=start_print)
print_btn.place(x=0, y=40, width=100, height=40)

stop_btn = tkinter.Button(root, fg='red', text="stop", command=stop)
stop_btn.place(x=0, y=80, width=100, height=80)

front_prt_btn = tkinter.Button(root, text="front prt", command=front_print_out)
front_prt_btn.place(x=0, y=160, width=50, height=20)

back_prt_btn = tkinter.Button(root, text="back prt", command=back_print_out)
back_prt_btn.place(x=50, y=160, width=50, height=20)

#텍스트 상자 위치 & 기능
main_txt = tkinter.Text(root)
main_txt.pack()
main_txt.place(x=100, y=0, width=400, height=750)

cursor_txt = tkinter.Text(root)
cursor_txt.pack()
cursor_txt.place(x=0, y=180, width=100, height=20)

state_txt = tkinter.Text(root)
state_txt.pack()
state_txt.place(x=0, y=200, width=100, height=550)

#터틀 위치 & 기능
canvas = tkinter.Canvas(root)
canvas.pack()
canvas.place(x=500, y=0, width=900, height=750)

#터틀 최초 실행
t = turtle.RawTurtle(canvas)
t.pensize(0.5)
t.penup()
t.goto(8 * cursor[0], MAX_Y_LINE * 3 - cursor[1])
t.pendown()
if __name__ == "__main__":
    root.mainloop()
    ard.close()