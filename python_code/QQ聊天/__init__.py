import ctypes
from time import sleep
from handle import msg_csv_eq
import pyautogui
import uiautomation as auto

# qq类
qq_main_window = auto.PaneControl(
    ClassName="Chrome_WidgetWin_1",
    searchDepth=1
)


message_txt = "智能汽车竞赛创意组"

class Message:
    time = ""
    name = ""
    text = ""

def parse_message(nodes):
    """
    解析每一条
    :return:
    """
    msg_list = []
    for node_data in nodes:
        msg = Message()
        # 无时间节点获取
        if len(node_data) != 2:
            # 获取姓名节点
            msg.name = node_data[0].GetChildren()[0].Name
             # 获取文本节点
            try:
                for txt_node in node_data[0].GetChildren()[1].GetChildren()[0].GetChildren():
                    if txt_node != "":
                        msg.text += txt_node.Name
            except IndexError:
                continue
        # 有时间节点获取
        else:
            # 获取时间节点
            msg.time = node_data[0].GetChildren()[0].Name
            # 获取姓名节点
            msg.name = node_data[1].GetChildren()[0].Name
            # 获取文本节点
            try:
                for txt_node in node_data[1].GetChildren()[1].GetChildren()[0].GetChildren():
                    if txt_node != "":
                        msg.text += txt_node.Name
            except IndexError:
                continue
        msg_list.append(msg)
    return msg_list


def find_node():
    """
    查找全部子节点
    :return:
    """
    list = []
    pyautogui.scroll(120 * 5)
    sleep(1)
    messages_Node = qq_main_window.DocumentControl(searchDepth=4).WindowControl(
        Name="消息列表"
    ).GroupControl(
        AutomationId="ml-root"
    )
    # 获取消息节点
    rootNode = messages_Node.GetChildren()
    # 获得消息节点第一个节点中的10个节点
    chatNode = rootNode[0].GetChildren()
    # 遍历每个消息节点
    for node in chatNode:
        # 每个消息节点中的中间节点
        for child in node.GetChildren():
            # child节点中的节点就是数据节点
            list.append(child.GetChildren())
    return list

 # 数据去重
def msg_eq(message):
    seen = set()
    result = []
    for msg_list in message:
        key = tuple((msg.name,msg.text,msg.time) for msg in msg_list)
        if key not in seen:
            seen.add(key)
            result.append(msg_list)
    return result

# 保存到txt文本中
def save_msg(filepath,result):
    message_data = []
    for msg_list in result:
        for msg in msg_list:
            temp_str = msg.time+","+msg.name+","+msg.text
            message_data.append(temp_str)

    seen = set()
    unique_list = []
    for item in message_data:
        if item not in seen:
            seen.add(item)
            unique_list.append(item)
    # 插入数据
    with open(filepath,"a",encoding="utf-8") as f:
        for item in unique_list:
            f.write(f"{item}\n")
    print("数据保存完成")

def show_qq():
    # 在底部窗口栏中找到QQ
    down_click = auto.PaneControl(
        ClassName="Shell_TrayWnd"
    ).PaneControl(
        ClassName="Taskbar.TaskbarFrameAutomationPeer"
    ).GroupControl(
        AutomationId="TaskbarFrameRepeater"
    ).ButtonControl(
        AutomationId="Appid: QQ"
    )
    down_click.Click()

    # 遍历所有窗口，匹配ProcessId和ClassName

    # 搜索框
    target_combo = qq_main_window.DocumentControl().GroupControl(searchDepth=3).ComboBoxControl()
    target_combo.Click()
    target_combo.SendKeys("{Ctrl}A{Delete}")
    target_combo.SendKeys(message_txt, interval=0.1)

    sleep(1)

    messages_Node = (qq_main_window.DocumentControl(searchDepth=2)
                     .WindowControl(Name="会话列表"))
    # 获取搜索到的第一个，这里可以后续进行验证是否是搜索的联系人
    messages_Node = messages_Node.GetChildren()
    messages_Node[0].Click()
    up_data = qq_main_window.DocumentControl(searchDepth=2).WindowControl(
        Name="消息列表"
    )
    up_data.Click()


if __name__ == '__main__':


    # 找到qq窗口
    show_qq()
    
    SW_HIDE = 0
    SW_SHOW = 5
    ShowWindow = ctypes.windll.user32.ShowWindow

    # 获取顶层 PaneControl
    qq_main_window = auto.PaneControl(ClassName="Chrome_WidgetWin_1", searchDepth=1)

    # 获取窗口句柄
    hwnd = qq_main_window.NativeWindowHandle

    ShowWindow(hwnd, SW_HIDE)

    # 存放数据列表
    message = []
    for i in range(200):
        message_node = find_node()
        message.insert(0,parse_message(message_node))
    # 数据去重
    result = msg_eq(message)
    # 保存数据
    save_msg(f"{message_txt}.csv", result)
    # 二次去重
    msg_csv_eq(f"{message_txt}.csv")


