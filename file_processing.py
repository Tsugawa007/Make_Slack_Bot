#Not compatible the indent behind class block
#So, I handle it using comment


#Module
import json
import datetime

'''
#To Do
Change environment variable(Path) after upload to lambda
'''
path = "/Users/harupurin/Desktop/response.json"
response_file = open(path,'r')
response_content = json.load(response_file)
#print(response_content["textAnnotations"]["description"])
datalist = response_content["textAnnotations"][0]["description"]

symbol_cnt = lambda x: datalist.index(x) if datalist.count(x) != 0 else -1

class_cnt = symbol_cnt('class')
def_cnt = symbol_cnt('def')
for_cnt = symbol_cnt('for')
if_cnt = symbol_cnt('if')
elif_cnt = symbol_cnt('elif')
else_cnt = symbol_cnt('else')

symbol_list  = ["def","for","if","elif","else"]
#f = open('test0628.py', 'w')
#f.writelines(datalist)
#f.close()


def judge_back_symbol(symbol):
    flag = False
    if "class" in symbol:
        flag = True
        symbol = "class"
    if "def" in symbol:
        flag = True
        symbol = "def"
    if "for" in symbol:
        flag = True
        symbol = "for"
    if "if" in symbol:
        flag = True
        symbol = "if"
    if "elif" in symbol:
        flag = True
        symbol = "elif"
    if "else" in symbol:
        flag = True
        symbol = "else"
    return flag,symbol

def judge_front_symbol(symbol):
    if ':' in symbol: return True
    else: return False

def judge_indent(symbol,symbols,symbol_nums):
    if symbol == "elif" and symbols[-2] == "if":
        return  symbol_nums[-1]
    if symbol == "else" and symbols[-2] == "if":
        return  symbol_nums[-1]
    if symbol == "else" and symbols[-2] == "elif":
        return  symbol_nums[-1]
    if symbol == "if" and symbols[-2] == "else":
        return symbol_nums[-1] -1
    if symbol == "def":
        if len(symbol_nums) > symbols.index("def"):
            #print(symbol,symbols)
            return symbol_nums[symbols.index("def")]
    return -1

def content_process(datalist,new_content = ""):
    indent_cnt = 0
    symbols = []
    symbol_nums = []
    front_flag = False
    flag_2 = False
    flag,symbol = judge_back_symbol(datalist[:5])
    if flag:
        symbols.append(symbol)
        symbol_nums.append(1)
        #indent_cnt = 1
    for i in range(len(datalist)):
        new_content += datalist[i]
        if datalist[i] == '\n':
            former_cnt = indent_cnt
            front_symbol = datalist[i-6:i]
            back_symbol = datalist[i+1:i+5]
            flag,symbol = judge_back_symbol(back_symbol)
            if flag :
                symbols.append(symbol)

                tmp_cnt = judge_indent(symbol,symbols,symbol_nums)
                if tmp_cnt != -1:
                    indent_cnt = tmp_cnt
                else:
                    if len(symbol_nums) == 0:
                        indent_cnt = 0
                    else:
                        indent_cnt += 1
                symbol_nums.append(indent_cnt)
                '''
                if judge_front_symbol(front_symbol):
                    #indent_cnt += 1
                    front_flag = True
                    if flag == False:
                        #new_content += "    "
                        indent_cnt += 1
                else:
                    if front_flag:
                        front_flag = False
                        #indent_cnt -= 1

                if flag_2:
                    new_content += "    "
                    flag_2 = False
                '''
            else:
                if judge_front_symbol(front_symbol):
                    flag_2 = True
                if flag_2:
                    new_content += "    "

            #else:
                #if judge_front_symbol(front_symbol):
                    #if len(symbol_nums) != 1:
                        #indent_cnt -= 1
            #print(back_symbol,indent_cnt)
            new_content += "    " * indent_cnt


            #if judge_front_symbol(front_symbol) == False and flag == True:
                #if len(symbols) != 0 and symbols[-1] == "def":
                    #indent_cnt = 2
                #else:
                    #indent_cnt -= 1
        #if datalist[i] == ':':
            #indent_cnt += 1

            #datalist.insert(i+1,'\s\s\s\s')


        #print(row)
    return new_content
new_content = content_process(datalist)

print(new_content)
create_file_name = "test" + str(datetime.datetime.now()) + ".py"
f = open(create_file_name, 'w')
f.writelines(new_content)
f.close()
#before 96
