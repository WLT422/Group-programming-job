
import simpleguitk as simplegui
import random
from PIL import Image

baymax = simplegui.load_image('https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1602050173377&di=6fb74868d6f2ec503bd70084569db8f3&imgtype=0&src=http%3A%2F%2Fpn.gexing.com%2Fqqpifu%2F20120815%2F1822%2F502b78514260b.jpg')
#print(baymax)
width = 600
height = 770
# 定义图像块的边长
image_size = width / 3
# 定义图像块的坐标列表
all_coordinates = [[image_size * 0.5, image_size * 0.5], [image_size * 1.5, image_size * 0.5],
                   [image_size * 2.5, image_size * 0.5], [image_size * 0.5, image_size * 1.5],
                   [image_size * 1.5, image_size * 1.5], [image_size * 2.5, image_size * 1.5],
                   [image_size * 0.5, image_size * 2.5], [image_size * 1.5, image_size * 2.5],
                   None
                   ]

# 棋盘的行列
ROWS = 3
COLS = 3

# 棋盘步数
steps = 0

# 保存所以图像块的列表
board = [[None, None, None], [None, None, None], [None, None, None]]


# 定义一个图像块的类
class Square:

    def __init__(self, coordinate):
        self.center = coordinate

    def draw(self, canvas, board_pos):
        canvas.draw_image(baymax, self.center, [image_size, image_size],
                          [(board_pos[1] + 0.5) * image_size, (board_pos[0] + 0.5) * image_size]
                          , [image_size, image_size])


def init_board():
    """对每个小方格，创建方块对象"""

    # 随机打乱列表
    random.shuffle(all_coordinates)

    # 填充并且拼接图版
    for i in range(ROWS):
        for j in range(COLS):
            idx = i * ROWS + j
            square_center = all_coordinates[idx]
            if square_center is None:
                board[i][j] = None
            else:
                board[i][j] = Square(square_center)


def play_game():
    """重置游戏"""
    global steps
    steps = 0
    init_board()


def draw(canvas):
    """画界面上的元素"""

    # 画下方图片
    canvas.draw_image(baymax, [width / 2, height / 2], [width, height], [50, width + 50], [98, 98])
    # 画下方步数
    canvas.draw_text("步数: " + str(steps), [400, 680], 22, 'white')
    # 绘制游戏界面各元素
    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] is not None:
                board[i][j].draw(canvas, [i, j])


def mouse_click(pos):
    """鼠标点击事件"""
    global steps
    # r为行数，c为列数
    r = int(pos[1] // image_size)
    c = int(pos[0] // image_size)

    if r < 3 and c < 3:
        # 点击到空白位置
        if board[r][c] is None:
            return
        else:
            # 依次检查当前图像位置的上下左右是否有空位置
            current_square = board[r][c]
            # 判断上面
            if r - 1 >= 0 and board[r - 1][c] is None:
                board[r][c] = None
                board[r - 1][c] = current_square
                steps += 1
            # 判断下面
            elif r + 1 <= 2 and board[r + 1][c] is None:
                board[r][c] = None
                board[r + 1][c] = current_square
                steps += 1
            # 判断在左边
            elif c - 1 >= 0 and board[r][c - 1] is None:
                board[r][c] = None
                board[r][c - 1] = current_square
                steps += 1
            # 判断在右边
            elif c + 1 <= 2 and board[r][c + 1] is None:
                board[r][c] = None
                board[r][c + 1] = current_square
                steps += 1


frame = simplegui.create_frame('拼图', width, height)
frame.set_canvas_background('black')
# 绘制界面
frame.set_draw_handler(draw)
# 创建窗口，绑定事件，设置大小
frame.add_button('重新开始', play_game, 60)
# 注册鼠标事件
frame.set_mouseclick_handler(mouse_click)
# 初始化游戏
play_game()
# 启动框架
frame.start()
