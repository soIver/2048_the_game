from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import random
import math
import pandas
import os.path
import pyreadstat

class Timer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_window.grid.removeWidget(settings_panel)
        main_window.grid.addWidget(self)
        self.xsize = main_window.xsize
        self.ysize = main_window.ysize
        self.interval = main_window.timer_interval
        self.move_timer = QTimer()
        self.move_timer.setInterval(1000)
        self.move_timer.timeout.connect(self.move_tile)
        self.color_timer = QTimer()
        self.color_timer.setInterval(350)
        self.color_timer.timeout.connect(self.change_tile_color)
        self.shifty = round(162.5 * (self.ysize - 1)) // (self.interval - 1)
        if main_window.isMenuActive and main_window.isGameEnded and main_window.curwin == 0:
            self.shiftx = 175
        else:
            self.shiftx = 0
        self.timer_tile = QLabel(str(self.interval), self)
        self.timer_tile.setGeometry(935 + 100 * self.xsize + self.shiftx, round(1200 - 162.5 * self.ysize) // 2 + 10, 150, 0)
        self.tile_font = self.timer_tile.font()
        self.tile_font.setPointSize(40)
        self.tile_font.setBold(True)
        self.timer_tile.setFont(self.tile_font)
        self.timer_tile.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.timer_tile.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (main_window.tile_color8, main_window.text_color2))

    def change_tile_color(self):
        self.color_timer_times += 1
        self.color_timer.stop()
        self.timer_tile.setText(str(self.interval - self.color_timer_times))
        if self.color_timer_times >= self.interval // 3:
            self.timer_tile.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (main_window.tile_color16, main_window.text_color2))
        if self.color_timer_times >= self.interval // 3 * 2:
            self.timer_tile.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (main_window.tile_color32, main_window.text_color2))

    def move_tile(self):
        self.move_timer.setInterval(1000)
        self.move_timer_times += 1
        if self.move_timer_times == self.interval:
            self.stop()
            main_window.show_winlose_msg('end')
            return
        pos_anim = QPropertyAnimation(self.timer_tile, b'pos', self)
        pos_anim.setDuration(500)
        pos_anim.setEasingCurve(QEasingCurve.InOutCubic)
        pos_anim.setEndValue(QPoint(self.timer_tile.x(), self.timer_tile.y() + self.shifty))
        pos_anim.start()
        self.color_timer.start()

    def start(self):
        self.move_timer_times = 0
        self.color_timer_times = 0
        self.move_timer.start()
        self.appear()

    def stop(self):
        self.move_timer.stop()
        self.color_timer.stop()
        self.disappear()

    def restart(self):
        self.move_timer.stop()
        self.color_timer.stop()
        self.move_timer_times = 0
        self.color_timer_times = 0
        self.timer_tile.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (main_window.tile_color8, main_window.text_color2))
        self.timer_tile.setText(str(self.interval))
        anim = QPropertyAnimation(self.timer_tile, b'pos', self)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.setEndValue(QPoint(935 + 100 * self.xsize + self.shiftx, round(1200 - 162.5 * self.ysize) // 2 + 10))
        anim.start()
        self.move_timer.setInterval(200)
        self.move_timer.start()

    def disappear(self):
        anim = QPropertyAnimation(self.timer_tile, b'geometry', self)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.setEndValue(QRect(self.timer_tile.geometry().adjusted(0, 150, 0, -150)))
        anim.finished.connect(lambda: main_window.grid.removeWidget(main_window.timer_tile))
        anim.start()

    def appear(self):
        anim = QPropertyAnimation(self.timer_tile, b'geometry', self)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.setEndValue(QRect(self.timer_tile.geometry().adjusted(0, 0, 0, 150)))
        anim.start()
    
class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.focusNextPrevChild(True)
        main_window.grid.addWidget(self)
        self.move_timer = QTimer()
        self.move_timer.setInterval(400)
        self.move_timer.timeout.connect(self.move_with_window_step2)
        self.isOnScreen = False
        self.isAnimEnded = True
        self.pad = QWidget(self)
        self.pad.setGeometry(QRect(610, 200, 1220, 705))
        self.title = QLabel('параметры новой игры', self)
        self.title.setFont(main_window.font_35)
        self.title.setGeometry(QRect(610, 210, 1220, 100))
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.pad_mini1 = QLabel('номиналы\nновых плиток', self)
        self.pad_mini1.setFont(main_window.font_15)
        self.pad_mini1.setGeometry(QRect(670, 325, 250, 300))
        self.pad_mini1.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.pad_mini2 = QLabel('шансы\nпоявления', self)
        self.pad_mini2.setFont(main_window.font_15)
        self.pad_mini2.setGeometry(QRect(970, 325, 250, 300))
        self.pad_mini2.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.pad_mini3 = QLabel('цель:', self)
        self.pad_mini3.setFont(main_window.font_25)
        self.pad_mini3.setGeometry(QRect(670, 650, 550, 100))
        self.pad_mini4 = QLabel('настройка таймера', self)
        self.pad_mini4.setFont(main_window.font_20)
        self.pad_mini4.setGeometry(QRect(1275, 325, 515, 300))
        self.pad_mini4.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.pad_mini4_2 = QLabel('секунд:',self)
        self.pad_mini4_2.setFont(main_window.font_25)
        self.pad_mini4_2.setGeometry(QRect(1275, 530, 515, 75))
        self.pad_mini5 = QLabel('высота поля:', self)
        self.pad_mini5.setFont(main_window.font_20)
        self.pad_mini5.setGeometry(QRect(1275, 650, 515, 100))
        self.pad_mini6 = QLabel('ширина поля:', self)
        self.pad_mini6.setFont(main_window.font_20)
        self.pad_mini6.setGeometry(QRect(1275, 780, 515, 100))
        self.line_nom1 = QLineEdit('2', self)
        self.line_nom1.setMaxLength(4)
        self.line_nom1.setFont(main_window.font_25)
        self.line_nom1.setGeometry(QRect(690, 425, 210, 75))
        self.line_nom2 = QLineEdit('4', self)
        self.line_nom2.setMaxLength(4)
        self.line_nom2.setFont(main_window.font_25)
        self.line_nom2.setGeometry(QRect(690, 530, 210, 75))
        self.line_chance1 = QLineEdit('90', self)
        self.line_chance1.setMaxLength(2)
        self.line_chance1.setFont(main_window.font_25)
        self.line_chance1.setGeometry(QRect(990, 425, 210, 75))
        self.line_chance2 = QLineEdit('10', self)
        self.line_chance2.setMaxLength(2)
        self.line_chance2.setFont(main_window.font_25)
        self.line_chance2.setGeometry(QRect(990, 530, 210, 75))
        self.line_winnomin = QLineEdit('2048', self)
        self.line_winnomin.setMaxLength(6)
        self.line_winnomin.setFont(main_window.font_25)
        self.line_winnomin.setGeometry(QRect(880, 662, 320, 75))
        self.line_interval = QLineEdit('3', self)
        self.line_interval.setMaxLength(2)
        self.line_interval.setFont(main_window.font_25)
        self.line_interval.setGeometry(QRect(1550, 530, 210, 75))
        self.line_ysize = QLineEdit('4', self)
        self.line_ysize.setMaxLength(1)
        self.line_ysize.setFont(main_window.font_25)
        self.line_ysize.setGeometry(QRect(1630, 662, 130, 75))
        self.line_xsize = QLineEdit('4', self)
        self.line_xsize.setMaxLength(1)
        self.line_xsize.setFont(main_window.font_25)
        self.line_xsize.setGeometry(QRect(1630, 792, 130, 75))
        validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        for line in (self.line_nom1, self.line_nom2, self.line_chance1, self.line_chance2, self.line_interval, self.line_winnomin, self.line_xsize, self.line_ysize):
            line.setValidator(validator)
        self.start_btn = QPushButton('начать', self)
        self.start_btn.setFont(main_window.font_25)
        self.start_btn.setGeometry(QRect(670, 780, 250, 100))
        self.start_btn.clicked.connect(lambda: main_window.new_mode_start(3))
        self.back_btn = QPushButton('назад',self)
        self.back_btn.setFont(main_window.font_25)
        self.back_btn.setGeometry(QRect(970, 780, 250, 100))
        self.back_btn.clicked.connect(self.move)
        main_window.mode_btn4.clicked.connect(self.move)
        [widget.move(QPoint(widget.x() - 1920, widget.y())) for widget in self.findChildren(QWidget)]
        self.lines_tpl = (self.line_nom1, self.line_nom2, self.line_chance1, self.line_chance2, self.line_interval, self.line_winnomin, self.line_xsize, self.line_ysize)
        for btn in self.lines_tpl:
            btn.setFocusPolicy(Qt.ClickFocus)

    def event(self, event):
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Enter, Qt.Key_Return):
                self.check_input()
        return super().event(event)
    
    def check_input(self):
        for line in self.lines_tpl:
            num = int(line.text())
            match line:
                case self.line_interval:
                    if num < 1:
                        line.setText('1')
                    elif num > 60:
                        line.setText('60')
                case self.line_xsize | self.line_ysize:
                    if num < 3:
                        line.setText('3')
                    elif num > 6:
                        line.setText('6')
                case self.line_chance1 | self.line_chance2:
                    if num < 0:
                        line.setText('0')
                    elif num > 100:
                        line.setText('100')
                    num = int(line.text())
                    if line == self.line_chance1:
                        self.line_chance2.setText(str(100 - num))
                    else:
                        self.line_chance1.setText(str(100 - num))
                case self.line_nom1 | self.line_nom2:
                    if num < 2:
                        line.setText('2')
                    elif num > 4096:
                        line.setText('4096')
                    else:
                        line.setText(self.power_of_two(num))
                    num = int(line.text())
                    if num > int(self.line_winnomin.text()):
                        self.line_winnomin.setText(str(pow(2, int(math.log(num, 2) + 1))))
                case self.line_winnomin:
                    if num < 4:
                        line.setText('4')
                    elif num > 131072:
                        line.setText('131072')
                    else:
                        line.setText(self.power_of_two(num))
                    num = int(line.text())
                    if num < int(self.line_nom1.text()):
                        self.line_nom1.setText(str(pow(2, int(math.log(num, 2) - 1))))
                    if num < int(self.line_nom2.text()):
                        self.line_nom2.setText(str(pow(2, int(math.log(num, 2) - 1))))
        self.setFocus()
                
    def power_of_two(self, num) -> str:
        return (str(pow(2, round(math.log(num, 2)))))

    def clr_change(self):
        self.pad.setStyleSheet('background-color: %s; border-radius: 10px' % main_window.pad_color)
        self.title.setStyleSheet('background-color: %s; color: %s' % (main_window.pad_color, main_window.text_color1))
        for widget in (self.pad_mini1, self.pad_mini2, self.pad_mini3, self.pad_mini4, self.pad_mini4_2, self.pad_mini5, self.pad_mini6):
            widget.setStyleSheet("background-color: %s; color: %s; border-radius: 10px; padding: 10px" % (main_window.hollow_color, main_window.text_color1))
        for widget in (self.line_nom1, self.line_nom2, self.line_chance1, self.line_chance2, self.line_winnomin, self.line_xsize, self.line_ysize, self.line_interval):
            widget.setStyleSheet('background-color: %s; color: %s; border-radius: 10px; padding: 10px' % (main_window.text_color1, main_window.text_color2))
        self.pad.setStyleSheet('background-color: %s; border-radius: 10px' % main_window.pad_color)
        self.start_btn.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (main_window.tile_color16, main_window.text_color2))
        self.back_btn.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (main_window.tile_color32, main_window.text_color2))
    
    def move_with_menu(self):
        if main_window.curwin == 1:
            if main_window.isMenuActive:
                shiftx = -175
            else:
                shiftx = 175
            anim_group = QParallelAnimationGroup(self)
            for widget in self.findChildren(QWidget):
                anim = QPropertyAnimation(widget, b'pos')
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setDuration(400)
                anim.setEndValue(QPoint(widget.x() + shiftx, widget.y()))
                anim_group.addAnimation(anim)
            anim_group.start()

    def move_with_window_step1(self):
        if self.isOnScreen and (main_window.newwin == 1 or main_window.curwin == 1):
            anim_group = QParallelAnimationGroup(self)
            for widget in self.findChildren(QWidget):
                anim = QPropertyAnimation(widget, b'pos')
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setDuration(400)
                anim.setEndValue(QPoint(widget.x(), widget.y() + 1920))
                anim_group.addAnimation(anim)
            anim_group.start()
            if main_window.curwin == 1:
                self.move_timer.start()
            
    def move_with_window_step2(self):
        self.move_timer.stop()
        anim_group = QParallelAnimationGroup(self)
        for widget in self.findChildren(QWidget):
            anim = QPropertyAnimation(widget, b'pos')
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setDuration(0)
            anim.setEndValue(QPoint(widget.x(), widget.y() - 3840))
            anim_group.addAnimation(anim)
        anim_group.start()

    def move(self):
        if self.isAnimEnded:
            self.isAnimEnded = False
            if self.isOnScreen:
                shiftx = -1920
            else:
                shiftx = 1920
            anim_group = QParallelAnimationGroup(self)
            for widget in main_window.mode_widgets[1:]:
                anim = QPropertyAnimation(widget, b'pos')
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setDuration(600)
                anim.setEndValue(QPoint(widget.x() + shiftx, widget.y()))
                anim_group.addAnimation(anim)
            for widget in self.findChildren(QWidget):
                anim = QPropertyAnimation(widget, b'pos')
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setDuration(600)
                anim.setEndValue(QPoint(widget.x() + shiftx, widget.y()))
                anim_group.addAnimation(anim)
            anim_group.finished.connect(self.setAnimEnded)
            anim_group.start()
            self.isOnScreen = not self.isOnScreen

    def setAnimEnded(self):
        self.isAnimEnded = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.curwin = 0
        self.newwin = 0
        self.isWindowAnimEnd = True
        self.isMenuActive = False
        self.changes = False
        self.opacity = QGraphicsOpacityEffect()
        self.opacity.setOpacity(0)
        fonts_parent = QLabel()
        parent_font = fonts_parent.font()
        parent_font.setBold(True)
        fonts_parent.setFont(parent_font)
        self.font_var = fonts_parent.font()
        self.font_50 = fonts_parent.font()
        self.font_50.setPointSize(50)
        self.font_40 = fonts_parent.font()
        self.font_40.setPointSize(40)
        self.font_25 = fonts_parent.font()
        self.font_25.setPointSize(25)
        self.font_20 = fonts_parent.font()
        self.font_20.setPointSize(20)
        self.font_35 = fonts_parent.font()
        self.font_35.setPointSize(35)
        self.font_30 = fonts_parent.font()
        self.font_30.setPointSize(30)
        self.font_25 = fonts_parent.font()
        self.font_25.setPointSize(25)
        self.font_18 = fonts_parent.font()
        self.font_18.setPointSize(18)
        self.font_16 = fonts_parent.font()
        self.font_16.setPointSize(16)
        self.font_15 = fonts_parent.font()
        self.font_15.setPointSize(15)
        self.font_14 = fonts_parent.font()
        self.font_14.setPointSize(14)
        self.font_10 = fonts_parent.font()
        self.font_10.setPointSize(10)
        self.move_timer = QTimer()
        self.move_timer.setInterval(100)
        self.move_timer.timeout.connect(self.enable_moving)
        self.action_timer = QTimer()
        self.action_timer.setInterval(100)
        self.action_timer.timeout.connect(self.after_action)
        self.menu_timer = QTimer()
        self.menu_timer.setInterval(300)
        self.menu_timer.timeout.connect(self.enable_menu_moving)
        self.window_timer = QTimer()
        self.window_timer.setInterval(600)
        self.window_timer.timeout.connect(self.move_window)
        self.msg_timer = QTimer()
        self.msg_timer.setInterval(3000)
        self.msg_timer.timeout.connect(self.show_new_achievment_msg)
        self.new_game_timer = QTimer()
        self.new_game_timer.setInterval(600)
        self.new_game_timer.timeout.connect(self.new_game_tiles)
        self.change_mode_timer = QTimer()
        self.change_mode_timer.setInterval(600)
        self.change_mode_timer.timeout.connect(self.change_mode_timer_action)
        self.setWindowTitle('2048')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.desk_w = 1920
        self.desk_h = 1200
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.grid = QGridLayout(self.centralWidget)
        self.achievments_window_init()
        self.read_save_file()
        self.choose_mode(self.curmode)
        self.menu_init()
        self.game_window_init()
        self.mode_window_init()
        self.theme_window_init()
        self.rules_window_init()
        self.stats_window_init()
        self.windows = [self.game_widgets, self.mode_widgets, self.theme_widgets, self.achievments_widgets, self.rules_widgets, self.stats_widgets]
        self.windows_btns = [self.menu_game, self.menu_mode, self.menu_theme, self.menu_achievments, self.menu_rules, self.menu_stats]
    
    def read_save_file(self):
        if os.path.exists(save_path):
            self.isSaveExists = True
            df = pandas.read_spss(save_path)
            self.df_val = df['value']
            self.clrtheme = str(self.df_val[0])
            self.curmode = int(self.df_val[1])
            self.ysize = int(self.df_val[2])
            self.xsize = int(self.df_val[3])
            self.winnomin = int(self.df_val[4])
            self.new_tile_nomin1 = int(self.df_val[5])
            self.new_tile_nomin2 = int(self.df_val[6])
            self.chance = int(self.df_val[7])
            self.score = int(self.df_val[8])
            self.timer_interval = int(self.df_val[9])
            self.merge_cnt = int(self.df_val[10])
            self.isTimerEnable = self.df_val[11]
            self.isGameEnded = self.df_val[12]
            self.isWinner = self.df_val[13]
            best_scores_lst = self.df_val[14].split()
            best_tiles_lst = self.df_val[15].split()
            for i in range(4):
                best_scores_lst[i] = int(best_scores_lst[i])
                best_tiles_lst[i] = int(best_tiles_lst[i])
            self.best_scores_lst = best_scores_lst 
            self.best_tiles_lst = best_tiles_lst
            achievments_state = self.df_val[16].split()
            self.achievments_cnt = int(achievments_state[8])
            i = 0
            for key in self.achievments_dict.keys():
                self.achievments_dict[key] = bool(int(achievments_state[i]))
                i += 1
            game_area_config = self.df_val[17].split()
            game_area_config[-1] = int(game_area_config[-1])
            for i in range(game_area_config[-1]):
                newel = game_area_config[i].split(',')
                for j in range(3):
                    newel[j] = int(newel[j])
                game_area_config[i] = newel
            self.game_area_config = game_area_config
            
        else:
            self.isSaveExists = False
            self.curmode = 0
            self.ysize = 0
            self.xsize = 0
            self.winnomin = 0
            self.new_tile_nomin1 = 0
            self.new_tile_nomin2 = 0
            self.chance = 0
            self.score = 0
            self.isTimerEnable = False
            self.timer_interval = 0
            self.best_scores_lst = [0, 0, 0, 0]
            self.best_tiles_lst = [0, 0, 0, 0]
            self.merge_cnt = 0
            self.clrtheme = 'classic'
            self.achievments_cnt = 0
            self.isGameEnded = False
            self.isWinner = False

    def write_save_file(self):
        cnt = 0
        game_area_config = ''
        achievments_state = ''
        best_scores = ''
        best_tiles = ''
        for i in range(self.ysize):
            for j in range(self.xsize):
                if not self.game_area[i][j][0] == None:
                    cnt += 1
                    game_area_config += str(i) + ',' + str(j) + ',' + str(self.game_area[i][j][2]) + ' '
        game_area_config += str(cnt)
        for state in self.achievments_dict.values():
            if state:
                achievments_state += '1' + ' '
            else:
                achievments_state += '0' + ' '
        achievments_state += str(self.achievments_cnt)
        for i in range(4):
            best_scores += str(self.best_scores_lst[i])
            best_tiles += str(self.best_tiles_lst[i])
            if not i == 3:
                best_scores += ' '
                best_tiles += ' '
        var_lst = [self.clrtheme, self.curmode, self.ysize, self.xsize, self.winnomin,
                   self.new_tile_nomin1, self.new_tile_nomin2, 
                   self.chance, self.score, self.timer_interval, self.merge_cnt, 
                   self.isTimerEnable, self.isGameEnded, self.isWinner,
                   best_scores, best_tiles, achievments_state, game_area_config]
        data = {'value': var_lst}
        df = pandas.DataFrame(data=data)
        pyreadstat.write_sav(df, save_path)

    def choose_mode(self, mode: int):
        self.curmode = mode
        match mode:
            case 0:
                self.ysize = 4
                self.xsize = 4
                self.winnomin = 2048
                self.new_tile_nomin1 = 2
                self.new_tile_nomin2 = 4
                self.chance = 10
                self.isTimerEnable = False
            case 1:
                self.ysize = 3
                self.xsize = 3
                self.winnomin = 512
                self.new_tile_nomin1 = 2
                self.new_tile_nomin2 = 4
                self.chance = 10
                self.isTimerEnable = False
            case 2:
                self.ysize = 4
                self.xsize = 4
                self.winnomin = 2048
                self.new_tile_nomin1 = 2
                self.new_tile_nomin2 = 4
                self.timer_interval = 3
                self.chance = 10
                self.isTimerEnable = True
            case 3:
                settings_panel.check_input()
                self.ysize = int(settings_panel.line_ysize.text())
                self.xsize = int(settings_panel.line_xsize.text())
                self.winnomin = int(settings_panel.line_winnomin.text())
                self.new_tile_nomin1 = int(settings_panel.line_nom1.text())
                self.new_tile_nomin2 = int(settings_panel.line_nom2.text())
                self.chance = int(settings_panel.line_chance2.text())
                self.timer_interval = int(settings_panel.line_interval.text())
                self.isTimerEnable = True
            
    def achievments_check(self):
        cnt = 0
        for i in range(self.ysize):
            for j in range(self.xsize):
                match self.curmode:
                    case 0:
                        if self.game_area[i][j][2] == 8 and not self.achievments_dict[self.achiev1_ico]:
                            self.achievments_dict[self.achiev1_ico] = True
                            self.achievments_cnt += 1
                            self.show_new_achievment_msg()
                        if self.game_area[i][j][2] == 128 and not self.achievments_dict[self.achiev2_ico]:
                            self.achievments_dict[self.achiev2_ico] = True
                            self.achievments_cnt += 1
                            self.show_new_achievment_msg()
                        if self.game_area[i][j][2] == 2048 and not self.achievments_dict[self.achiev3_ico]:
                            self.achievments_dict[self.achiev3_ico] = True
                            self.achievments_cnt += 1
                            self.show_new_achievment_msg()
                        if self.game_area[i][j][2] == 4096 and not self.achievments_dict[self.achiev4_ico]:
                            self.achievments_dict[self.achiev4_ico] = True
                            self.achievments_cnt += 1
                            self.show_new_achievment_msg()
                    case 1:
                        if self.game_area[i][j][2] == 512 and not self.achievments_dict[self.achiev5_ico]:
                            self.achievments_dict[self.achiev5_ico] = True
                            self.achievments_cnt += 1
                            self.show_new_achievment_msg()
                    case 2:
                        if self.game_area[i][j][2] == 2048 and not self.achievments_dict[self.achiev6_ico]:
                            self.achievments_dict[self.achiev6_ico] = True
                            self.achievments_cnt += 1
                            self.show_new_achievment_msg()
                    case 3:
                        return
        if self.merge_cnt == 100000 and not self.achievments_dict[self.achiev7_ico]:
            self.achievments_dict[self.achiev7_ico] = True
            self.achievments_cnt += 1
            self.show_new_achievment_msg()
        if self.score == 1000000 and not self.achievments_dict[self.achiev8_ico]:
            self.achievments_dict[self.achiev8_ico] = True
            self.achievments_cnt += 1
            self.show_new_achievment_msg()
        for key, value in self.achievments_dict.items():
            cnt += 1
            if value:
                if cnt < 5:
                    colors = (self.tile_color2, self.text_color1)
                else:
                    colors = (self.text_color1, self.tile_color2)
                key.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % colors)
    
    def show_new_achievment_msg(self):
        msg_anim_group = QParallelAnimationGroup(self)
        if self.msg_timer.isActive():
            self.msg_timer.stop()
            shift = 430
        else:
            self.msg_timer.start()
            shift = -430
        for el in self.achievment_msg:
                anim = QPropertyAnimation(el, b'pos')
                anim.setDuration(500)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.setEndValue(QPoint(el.x(), el.y() + shift))
                msg_anim_group.addAnimation(anim)
        msg_anim_group.start()

    def show_winlose_msg(self, state: str):
        match state:
            case 'win':
                if self.isWinner:
                    return
                else:
                    btn1 = self.new_game_btn
                    btn2 = self.continue_game_btn
                    btn1_panel = self.new_game_btn_panel
                    btn2_panel = self.continue_game_btn_panel
                    self.isWinner = True
                    text = 'ПОБЕДА'
            case 'end':
                btn1 = self.new_game_btn
                btn2 = self.change_mode_btn
                btn1_panel = self.new_game_btn_panel
                btn2_panel = self.change_mode_btn_panel
                text = 'ИГРА\nЗАКОНЧЕНА'
            case 'continue':
                return
        if self.isTimerEnable:
            self.timer_tile.stop()
        self.isGameEnded = True
        self.winlose_msg_text.setText(text)
        btn1.setGeometry(QRect(btn1.geometry().adjusted(0, 0, 270, 80)))
        btn2.setGeometry(QRect(btn2.geometry().adjusted(0, 0, 270, 80)))
        opacity_anim = QPropertyAnimation(self.opacity, b'opacity', self)
        opacity_anim.setStartValue(0)
        opacity_anim.setEndValue(0.7)
        opacity_anim.setDuration(200)
        opacity_anim.start()
        size_anim_group = QParallelAnimationGroup(self)
        size_anim = QPropertyAnimation(btn1_panel, b'geometry')
        size_anim.setDuration(200)
        size_anim.setEndValue(QRect(btn1.geometry()))
        size_anim_group.addAnimation(size_anim)
        size_anim = QPropertyAnimation(btn2_panel, b'geometry')
        size_anim.setDuration(200)
        size_anim.setEndValue(QRect(btn2.geometry()))
        size_anim_group.addAnimation(size_anim)
        size_anim_group.start()

    def stats_update(self):
        self.stats_bs1_val.setText(str(self.best_scores_lst[0]))
        self.stats_bs2_val.setText(str(self.best_scores_lst[1]))
        self.stats_bs3_val.setText(str(self.best_scores_lst[2]))
        self.stats_bt1_val.setText(str(self.best_tiles_lst[0]))
        self.stats_bt2_val.setText(str(self.best_tiles_lst[1]))
        self.stats_bt3_val.setText(str(self.best_tiles_lst[2]))
        self.stats_ttm_val.setText(str(self.merge_cnt))
        self.stats_ac_val.setText(str(self.achievments_cnt))

    def clr_change(self, clrtheme: str):
        self.clrtheme = clrtheme
        match clrtheme:
            case 'classic':
                self.tile_color2 = '#eee4da'
                self.tile_color4 = '#eee1c9'
                self.tile_color8 = '#f3b27a'
                self.tile_color16 = '#f69664'
                self.tile_color32 = '#f77c5f'
                self.tile_color64 = '#f75f3b'
                self.tile_color128 = '#f8d669'
                self.tile_color256 = '#f8df5a'
                self.tile_color512 = '#ffe03e'
                self.tile_color1024 = '#ffda18'
                self.tile_color2048 = '#ffd600'
                self.pad_color = '#bbada0'
                self.text_color1 = '#776e65'
                self.text_color2 = '#f9f6f2'
                self.hollow_color = '#cdc1b4'
            case 'cold':
                self.tile_color2 = '#DAEEEA'
                self.tile_color4 = '#D1DDE4'
                self.tile_color8 = '#80DBED'
                self.tile_color16 = '#5AB3CB'
                self.tile_color32 = '#5696AB'
                self.tile_color64 = '#04597C'
                self.tile_color128 = '#52A499'
                self.tile_color256 = '#458D83'
                self.tile_color512 = '#48746E'
                self.tile_color1024 = '#4D6E69'
                self.tile_color2048 = '#38544A'
                self.pad_color = '#A0B3BB'
                self.text_color1 = '#657477'
                self.text_color2 = '#F2F7F9'
                self.hollow_color = '#BED1D6'
            case 'gray':
                self.tile_color2 = '#E2E2E2'
                self.tile_color4 = '#CECECE'
                self.tile_color8 = '#BEBEBE'
                self.tile_color16 = '#959595'
                self.tile_color32 = '#7B7B7B'
                self.tile_color64 = '#6E6E6E'
                self.tile_color128 = '#525252'
                self.tile_color256 = '#434343'
                self.tile_color512 = '#383838'
                self.tile_color1024 = '#323232'
                self.tile_color2048 = '#2D2D2D'
                self.pad_color = '#5B5B5B'
                self.text_color1 = '#464646'
                self.text_color2 = '#FAFAFA'
                self.hollow_color = '#676767'
        self.mode1_png = QPixmap(f'sprites\{clrtheme}\mode1.png')
        self.mode1_png.setMask(self.mode1_png.createHeuristicMask(Qt.transparent))
        self.mode2_png = QPixmap(f'sprites\{clrtheme}\mode2.png')
        self.mode2_png.setMask(self.mode2_png.createHeuristicMask(Qt.transparent))
        self.mode3_png = QPixmap(f'sprites\{clrtheme}\mode3.png')
        self.mode3_png.setMask(self.mode3_png.createHeuristicMask(Qt.transparent))
        self.mode4_png = QPixmap(f'sprites\{clrtheme}\mode4.png')
        self.mode4_png.setMask(self.mode4_png.createHeuristicMask(Qt.transparent))
        self.menu_btn_png = QPixmap(f'sprites\{clrtheme}\menu_btn.png')
        self.menu_btn_png = self.menu_btn_png.scaled(120, 120)
        self.menu_btn_png.setMask(self.menu_btn_png.createHeuristicMask(Qt.transparent))
        self.theme1_png = QPixmap(r'sprites\theme1.png')
        self.theme1_png.setMask(self.theme1_png.createHeuristicMask(Qt.transparent))
        self.theme2_png = QPixmap(r'sprites\theme2.png')
        self.theme2_png.setMask(self.theme2_png.createHeuristicMask(Qt.transparent))
        self.theme3_png = QPixmap(r'sprites\theme3.png')
        self.theme3_png.setMask(self.theme3_png.createHeuristicMask(Qt.transparent))
        self.color_dict = {2: self.tile_color2,
                        4: self.tile_color4,
                        8: self.tile_color8,
                        16: self.tile_color16,
                        32: self.tile_color32,
                        64: self.tile_color64,
                        128: self.tile_color128,
                        256: self.tile_color256,
                        512: self.tile_color512,
                        1024: self.tile_color1024,
                        2048: self.tile_color2048
                        }
        self.mode_img1.setPixmap(self.mode1_png)
        self.mode_img2.setPixmap(self.mode2_png)
        self.mode_img3.setPixmap(self.mode3_png)
        self.mode_img4.setPixmap(self.mode4_png)
        self.theme1.setPixmap(self.theme1_png)
        self.theme2.setPixmap(self.theme2_png)
        self.theme3.setPixmap(self.theme3_png)
        self.menu_rnd.setPixmap(self.menu_btn_png)
        self.setStyleSheet("background-color: %s" % self.text_color2)
        for widget in (self.mode_pad1, self.mode_pad2, self.mode_pad3, self.mode_pad4):
            widget.setStyleSheet('background-color: %s; border-radius: 10px' % self.pad_color)
        for widget in (self.mode_mode1, self.mode_mode2, self.mode_mode3, self.mode_mode4):
            widget.setStyleSheet('background-color: %s; color: %s' % (self.text_color2, self.text_color1))
        for widget in (self.mode_desc1, self.mode_desc2, self.mode_desc3, self.mode_desc4):
            widget.setStyleSheet('background-color: %s; color: %s' % (self.pad_color, self.text_color2))
        for widget in (self.theme1, self.theme2, self.theme3):
            widget.setStyleSheet("background-color: %s; border-radius: 10px" % self.pad_color)
        for widget in (self.achiev1_pad, self.achiev2_pad, self.achiev3_pad, self.achiev4_pad, self.achiev5_pad, self.achiev6_pad, self.achiev7_pad, self.achiev8_pad):
            widget.setStyleSheet('background-color: %s; border-radius: 10px' % self.pad_color)
        for widget in (self.achiev1_title, self.achiev2_title, self.achiev3_title, self.achiev4_title, self.achiev5_title, self.achiev6_title, self.achiev7_title, self.achiev8_title, self.achiev8_2_title):
            widget.setStyleSheet('background-color: %s; color: %s' % (self.pad_color, self.text_color2))
        for widget in (self.achiev1_ico, self.achiev2_ico, self.achiev3_ico, self.achiev4_ico, self.achiev5_ico, self.achiev6_ico, self.achiev7_ico, self.achiev8_ico):
            widget.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (self.hollow_color, self.hollow_color))
        for widget in (self.achiev1_desc, self.achiev2_desc, self.achiev3_desc, self.achiev4_desc, self.achiev5_desc, self.achiev6_desc, self.achiev7_desc, self.achiev8_desc):
            widget.setStyleSheet('background-color: %s; color: %s' % (self.pad_color, self.text_color1))
        for widget in (self.mode_title, self.theme_title, self.rules_title, self.rules_rules, self.achievments_title, self.stats_title, self.icon):
            widget.setStyleSheet('color: %s' % self.text_color1)
        for widget in (self.stats_pad1, self.stats_pad2, self.stats_pad3, self.stats_pad4):
            widget.setStyleSheet('background-color: %s; border-radius: 10px' % self.pad_color)
        for widget in (self.stats_mode_title1, self.stats_mode_title2, self.stats_mode_title3, self.stats_mode_title4):
            widget.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (self.pad_color, self.text_color1))
        for widget in (self.stats_bs1, self.stats_bs2, self.stats_bs3, self.stats_bt1, self.stats_bt2, self.stats_bt3, self.stats_ttm, self.stats_ac):
            widget.setStyleSheet('background-color: %s; color: %s' % (self.pad_color, self.text_color1))
        for widget in (self.stats_bs1_val, self.stats_bs2_val, self.stats_bs3_val, self.stats_bt1_val, self.stats_bt2_val, self.stats_bt3_val, self.stats_ttm_val, self.stats_ac_val):
            widget.setStyleSheet('background-color: %s; color: %s; border-radius: 10px; padding: 1px' % (self.text_color1, self.text_color2))
        for widget in (self.menu_game, self.menu_mode, self.menu_theme, self.menu_achievments, self.menu_rules, self.menu_stats):
            widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); color: %s" % self.text_color1)
        for widget in (self.menu_game_h, self.menu_mode_h, self.menu_theme_h, self.menu_achievments_h, self.menu_rules_h, self.menu_stats_h):
            widget.setStyleSheet("background-color: %s; color: %s; border-radius: 10px; padding: 10px" % (self.hollow_color, self.text_color1))
        for widget in (self.score_plain, self.best_plain):
            widget.setStyleSheet("background-color: %s; color: %s; border-radius: 10px" % (self.tile_color2, self.text_color1))
        for widget in (self.score_value, self.best_value):
            widget.setStyleSheet("background-color: %s; color: %s; border-radius: 10px" % (self.tile_color2, self.text_color2))
        for widget in (self.new_game_btn_panel, self.change_mode_btn_panel, self.continue_game_btn_panel):
            widget.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (self.tile_color2, self.text_color1))
        self.menu_pad.setStyleSheet("background-color: %s" % self.pad_color)
        self.menu_menu.setStyleSheet("background-color: %s; border-radius: 75px" % self.tile_color2)
        self.menu_txt.setStyleSheet("background-color: %s; color: %s" % (self.tile_color2, self.text_color1))
        self.menu_rnd.setStyleSheet("background-color: %s; border-radius: 60" % self.tile_color2)
        self.menu_exit.setStyleSheet("background-color: %s; color: %s; border-radius: 10px" % (self.tile_color32, self.text_color2))
        self.menu_tile.setStyleSheet("background-color: %s; border-radius: 10px" % self.tile_color2)
        self.bg_plain.setStyleSheet("background-color: %s; border-radius: 10px" % self.pad_color)
        self.winlose_msg_pad.setStyleSheet("background-color: %s; border-radius: 10px" % self.pad_color)
        self.winlose_msg_text.setStyleSheet('background-color: rgba(0, 0, 0, 0.0); color: %s' % self.text_color2)
        self.achievment_msg_pad.setStyleSheet('background-color: %s; border-radius: 10px' % self.pad_color)
        self.achievment_msg_text.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (self.pad_color, self.text_color1))
        self.achievment_msg_tile.setStyleSheet('background-color: %s; color: %s; border-radius: 10px' % (self.tile_color2, self.text_color1))
        settings_panel.clr_change()
        self.achievments_check()
        self.set_tiles_style()

    def set_tiles_style(self):
        for i in range(self.ysize):
            for j in range(self.xsize):
                self.hollows_lst[i][j][0].setStyleSheet("background-color: %s; border-radius: 10px" % self.hollow_color)
                if self.game_area[i][j][0] != None:
                        if self.game_area[i][j][2] < 8:
                            text_color = self.text_color1
                        else:
                            text_color = self.text_color2
                        if self.game_area[i][j][2] < 4096:
                            bg_color = self.color_dict[self.game_area[i][j][2]]
                        else:
                            bg_color = self.text_color1
                        self.game_area[i][j][0].setStyleSheet(f'background-color: {bg_color}; color: {text_color}; border-radius: 10')
                        self.game_area[i][j][0].setText(str(self.game_area[i][j][2]))
                        new_tile_font = self.font_40
                        new_tile_font.setPointSize(44 - len(str(self.game_area[i][j][2])) * 4)
                        if new_tile_font.pointSize() < 10:
                            new_tile_font.setPointSize(10)
                        self.game_area[i][j][0].setFont(new_tile_font)
        
    def mode_window_init(self):
        self.mode_title = QLabel("выбор режима игры", self)
        self.mode_title.setFont(self.font_50)
        self.mode_title.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.mode_title.setGeometry(QRect(600, 50 - self.desk_h, 1200, 100))
        self.mode_pad1 = QWidget(self)
        self.mode_pad1.setGeometry(QRect(610, 200 - self.desk_h, 580, 280))
        self.mode_pad2 = QWidget(self)
        self.mode_pad2.setGeometry(QRect(1250, 200 - self.desk_h, 580, 280))
        self.mode_pad3 = QWidget(self)
        self.mode_pad3.setGeometry(QRect(610, 625 - self.desk_h, 580, 280))
        self.mode_pad4 = QWidget(self)
        self.mode_pad4.setGeometry(QRect(1250, 625 - self.desk_h, 580, 280))
        self.mode_mode1 = QLabel("4x4", self)
        self.mode_mode1.setFont(self.font_25)
        self.mode_mode1.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.mode_mode1.setGeometry((QRect(650, 480 - self.desk_h, 500, 85)))
        self.mode_mode2 = QLabel("3x3", self)
        self.mode_mode2.setFont(self.font_25)
        self.mode_mode2.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.mode_mode2.setGeometry((QRect(1290, 480 - self.desk_h, 500, 85)))
        self.mode_mode3 = QLabel("быстрая игра", self)
        self.mode_mode3.setFont(self.font_25)
        self.mode_mode3.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.mode_mode3.setGeometry((QRect(650, 905 - self.desk_h, 500, 85)))
        self.mode_mode4 = QLabel("пользовательский", self)
        self.mode_mode4.setFont(self.font_25)
        self.mode_mode4.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.mode_mode4.setGeometry((QRect(1290, 905 - self.desk_h, 500, 85)))
        self.mode_desc1 = QLabel("классический режим игры в 2048 со стандартным полем и правилами", self)
        self.mode_desc1.setFont(self.font_15)
        self.mode_desc1.setWordWrap(True)
        self.mode_desc1.setAlignment(Qt.AlignTop)
        self.mode_desc1.setGeometry((QRect(890, 225 - self.desk_h, 275, 230)))
        self.mode_desc2 = QLabel("проверьте свои способности на уменьшенном поле!", self)
        self.mode_desc2.setFont(self.font_15)
        self.mode_desc2.setWordWrap(True)
        self.mode_desc2.setAlignment(Qt.AlignTop)
        self.mode_desc2.setGeometry((QRect(890, 650 - self.desk_h, 275, 230)))
        self.mode_desc3 = QLabel("стандартное поле 4x4, но время на каждое действие ограничено!", self)
        self.mode_desc3.setFont(self.font_15)
        self.mode_desc3.setWordWrap(True)
        self.mode_desc3.setAlignment(Qt.AlignTop)
        self.mode_desc3.setGeometry((QRect(1535, 225 - self.desk_h, 275, 230)))
        self.mode_desc4 = QLabel("прямоугольное поле? считанные секунды на размышление? в этом режиме можно всё!", self)
        self.mode_desc4.setFont(self.font_15)
        self.mode_desc4.setWordWrap(True)
        self.mode_desc4.setAlignment(Qt.AlignTop)
        self.mode_desc4.setGeometry((QRect(1535, 650 - self.desk_h, 275, 230)))
        self.mode_img1 = QLabel(self)
        self.mode_img1.setGeometry((QRect(635, 225 - self.desk_h, 230, 230)))
        self.mode_img1.setStyleSheet('border-radius: 10px')
        self.mode_img2 = QLabel(self)
        self.mode_img2.setGeometry((QRect(635, 650 - self.desk_h, 230, 230)))
        self.mode_img2.setStyleSheet('border-radius: 10px')
        self.mode_img3 = QLabel(self)
        self.mode_img3.setGeometry((QRect(1275, 225 - self.desk_h, 230, 230)))
        self.mode_img3.setStyleSheet('border-radius: 10px')
        self.mode_img4 = QLabel(self)
        self.mode_img4.setGeometry((QRect(1275, 650 - self.desk_h, 230, 230)))
        self.mode_img4.setStyleSheet('border-radius: 10px')
        self.mode_btn1 = QPushButton(self)
        self.mode_btn1.setGeometry(QRect(610, 200 - self.desk_h, 580, 280))
        self.mode_btn1.clicked.connect(lambda: self.new_mode_start(0))
        self.mode_btn1.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.mode_btn2 = QPushButton(self)
        self.mode_btn2.setGeometry(QRect(1250, 200 - self.desk_h, 580, 280))
        self.mode_btn2.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.mode_btn2.clicked.connect(lambda: self.new_mode_start(1))
        self.mode_btn3 = QPushButton(self)
        self.mode_btn3.setGeometry(QRect(610, 625 - self.desk_h, 580, 280))
        self.mode_btn3.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.mode_btn3.clicked.connect(lambda: self.new_mode_start(2))
        self.mode_btn4 = QPushButton(self)
        self.mode_btn4.setGeometry(QRect(1250, 625 - self.desk_h, 580, 280))
        self.mode_btn4.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.mode_widgets = [self.mode_title, self.mode_pad1, self.mode_pad2, self.mode_pad3, self.mode_pad4, 
                             self.mode_mode1, self.mode_mode2, self.mode_mode3, self.mode_mode4,
                             self.mode_desc1, self.mode_desc2, self.mode_desc3, self.mode_desc4,
                             self.mode_img1, self.mode_img2, self.mode_img3, self.mode_img4,
                             self.mode_btn1, self.mode_btn2, self.mode_btn3, self.mode_btn4]

    def theme_window_init(self):
        self.theme_title = QLabel("выбор цветовой темы", self)
        self.theme_title.setFont(self.font_50)
        self.theme_title.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.theme_title.setGeometry(QRect(600, 50 - self.desk_h, 1200, 100))
        self.theme1 = QLabel(self)
        self.theme1.setGeometry(QRect(940, 190 - self.desk_h, 550, 200))
        self.theme2 = QLabel(self)
        self.theme2.setGeometry(QRect(940, 500 - self.desk_h, 550, 200))
        self.theme3 = QLabel(self)
        self.theme3.setGeometry(QRect(940, 810 - self.desk_h, 550, 200))
        self.theme1_btn = QPushButton(self)
        self.theme1_btn.setStyleSheet("background-color: rgba(0, 0, 0, 0.0)")
        self.theme1_btn.setGeometry(QRect(940, 190 - self.desk_h, 550, 200))
        self.theme1_btn.clicked.connect(lambda: self.clr_change('classic'))
        self.theme2_btn = QPushButton(self)
        self.theme2_btn.setStyleSheet("background-color: rgba(0, 0, 0, 0.0)")
        self.theme2_btn.setGeometry(QRect(940, 500 - self.desk_h, 550, 200))
        self.theme2_btn.clicked.connect(lambda: self.clr_change('cold'))
        self.theme3_btn = QPushButton(self)
        self.theme3_btn.setStyleSheet("background-color: rgba(0, 0, 0, 0.0)")
        self.theme3_btn.setGeometry(QRect(940, 810 - self.desk_h, 550, 200))
        self.theme3_btn.clicked.connect(lambda: self.clr_change('gray'))
        self.theme1_title = QLabel('классическая', self)
        self.theme1_title.setFont(self.font_25)
        self.theme1_title.setStyleSheet('color: #776e65')
        self.theme1_title.setGeometry(QRect(940, 400 - self.desk_h, 550, 60))
        self.theme1_title.setAlignment(Qt.AlignHCenter)
        self.theme2_title = QLabel('холодная', self)
        self.theme2_title.setFont(self.font_25)
        self.theme2_title.setStyleSheet('color: #657477')
        self.theme2_title.setGeometry(QRect(940, 710 - self.desk_h, 550, 60))
        self.theme2_title.setAlignment(Qt.AlignHCenter)
        self.theme3_title = QLabel('оттенки серого', self)
        self.theme3_title.setFont(self.font_25)
        self.theme3_title.setStyleSheet('color: #464646')
        self.theme3_title.setGeometry(QRect(940, 1020 - self.desk_h, 550, 60))
        self.theme3_title.setAlignment(Qt.AlignHCenter)
        self.theme_widgets = (self.theme_title, self.theme1, self.theme2, self.theme3, 
                              self.theme1_title, self.theme2_title, self.theme3_title,
                              self.theme1_btn, self.theme2_btn, self.theme3_btn)

    def achievments_window_init(self):
        self.achievments_title = QLabel("достижения", self)
        self.achievments_title.setFont(self.font_50)
        self.achievments_title.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.achievments_title.setGeometry(QRect(600, 50 - self.desk_h, 1200, 100))
        self.achiev1_pad = QWidget(self)
        self.achiev1_pad.setGeometry(QRect(640, 200 - self.desk_h, 500, 150))
        self.achiev2_pad = QWidget(self)
        self.achiev2_pad.setGeometry(QRect(640, 410 - self.desk_h, 500, 150))
        self.achiev3_pad = QWidget(self)
        self.achiev3_pad.setGeometry(QRect(640, 620 - self.desk_h, 500, 150))
        self.achiev4_pad = QWidget(self)
        self.achiev4_pad.setGeometry(QRect(640, 830 - self.desk_h, 500, 150))
        self.achiev5_pad = QWidget(self)
        self.achiev5_pad.setGeometry(QRect(1280, 200 - self.desk_h, 500, 150))
        self.achiev6_pad = QWidget(self)
        self.achiev6_pad.setGeometry(QRect(1280, 410 - self.desk_h, 500, 150))
        self.achiev7_pad = QWidget(self)
        self.achiev7_pad.setGeometry(QRect(1280, 620 - self.desk_h, 500, 150))
        self.achiev8_pad = QWidget(self)
        self.achiev8_pad.setGeometry(QRect(1280, 830 - self.desk_h, 500, 150))
        self.achiev1_title = QLabel('первые шаги', self)
        self.achiev1_title.setAlignment(Qt.AlignTop)
        self.achiev1_title.setFont(self.font_18)
        self.achiev1_title.setGeometry(QRect(790, 205 - self.desk_h, 345, 70))
        self.achiev2_title = QLabel('первые успехи', self)
        self.achiev2_title.setAlignment(Qt.AlignTop)
        self.achiev2_title.setFont(self.font_18)
        self.achiev2_title.setGeometry(QRect(790, 415 - self.desk_h, 345, 70))
        self.achiev3_title = QLabel('первая победа', self)
        self.achiev3_title.setAlignment(Qt.AlignTop)
        self.achiev3_title.setFont(self.font_18)
        self.achiev3_title.setGeometry(QRect(790, 625 - self.desk_h, 345, 70))
        self.achiev4_title = QLabel('сверх нормы', self)
        self.achiev4_title.setAlignment(Qt.AlignTop)
        self.achiev4_title.setFont(self.font_18)
        self.achiev4_title.setGeometry(QRect(790, 835 - self.desk_h, 345, 70))
        self.achiev5_title = QLabel('это было сложно', self)
        self.achiev5_title.setAlignment(Qt.AlignTop)
        self.achiev5_title.setFont(self.font_18)
        self.achiev5_title.setGeometry(QRect(1430, 205 - self.desk_h, 345, 70))
        self.achiev6_title = QLabel('это было быстро', self)
        self.achiev6_title.setAlignment(Qt.AlignTop)
        self.achiev6_title.setFont(self.font_18)
        self.achiev6_title.setGeometry(QRect(1430, 415 - self.desk_h, 345, 70))
        self.achiev7_title = QLabel('мастер плиток', self)
        self.achiev7_title.setAlignment(Qt.AlignTop)
        self.achiev7_title.setFont(self.font_18)
        self.achiev7_title.setGeometry(QRect(1430, 625 - self.desk_h, 345, 70))
        self.achiev8_2_title = QLabel('миллионером?', self)
        self.achiev8_2_title.setAlignment(Qt.AlignTop)
        self.achiev8_2_title.setFont(self.font_16)
        self.achiev8_2_title.setGeometry(QRect(1430, 862 - self.desk_h, 345, 35))
        self.achiev8_title = QLabel('а кто не хочет стать', self)
        self.achiev8_title.setAlignment(Qt.AlignTop)
        self.achiev8_title.setFont(self.font_16)
        self.achiev8_title.setGeometry(QRect(1430, 835 - self.desk_h, 345, 35))
        self.achiev1_ico = QLabel('8', self)
        self.achiev1_ico.setFont(self.font_30)
        self.achiev1_ico.setGeometry(QRect(650, 210 - self.desk_h, 120, 120))
        self.achiev1_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev2_ico = QLabel('128', self)
        self.achiev2_ico.setFont(self.font_25)
        self.achiev2_ico.setGeometry(QRect(650, 420 - self.desk_h, 120, 120))
        self.achiev2_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev3_ico = QLabel('2048', self)
        self.achiev3_ico.setFont(self.font_20)
        self.achiev3_ico.setGeometry(QRect(650, 630 - self.desk_h, 120, 120))
        self.achiev3_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev4_ico = QLabel('4096', self)
        self.achiev4_ico.setFont(self.font_20)
        self.achiev4_ico.setGeometry(QRect(650, 840 - self.desk_h, 120, 120))
        self.achiev4_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev5_ico = QLabel('512', self)
        self.achiev5_ico.setFont(self.font_25)
        self.achiev5_ico.setGeometry(QRect(1290, 210 - self.desk_h, 120, 120))
        self.achiev5_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev6_ico = QLabel('2048', self)
        self.achiev6_ico.setFont(self.font_20)
        self.achiev6_ico.setGeometry(QRect(1290, 420 - self.desk_h, 120, 120))
        self.achiev6_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev7_ico = QLabel('100 000', self)
        self.achiev7_ico.setFont(self.font_20)
        self.achiev7_ico.setGeometry(QRect(1290, 630 - self.desk_h, 120, 120))
        self.achiev7_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev7_ico.setWordWrap(True)
        self.achiev8_ico = QLabel('1000 000', self)
        self.achiev8_ico.setFont(self.font_18)
        self.achiev8_ico.setGeometry(QRect(1290, 840 - self.desk_h, 120, 120))
        self.achiev8_ico.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.achiev8_ico.setWordWrap(True)
        self.achiev1_desc = QLabel('соберите плитку номиналом 8 в режиме “4x4”', self)
        self.achiev1_desc.setWordWrap(True)
        self.achiev1_desc.setFont(self.font_10)
        self.achiev1_desc.setGeometry(QRect(790, 250 - self.desk_h, 320, 90))
        self.achiev1_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev2_desc = QLabel('соберите плитку номиналом 128 в режиме “4x4”', self)
        self.achiev2_desc.setWordWrap(True)
        self.achiev2_desc.setFont(self.font_10)
        self.achiev2_desc.setGeometry(QRect(790, 460 - self.desk_h, 320, 90))
        self.achiev2_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev3_desc = QLabel('соберите плитку номиналом 2048 в режиме “4x4”', self)
        self.achiev3_desc.setWordWrap(True)
        self.achiev3_desc.setFont(self.font_10)
        self.achiev3_desc.setGeometry(QRect(790, 670 - self.desk_h, 320, 90))
        self.achiev3_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev4_desc = QLabel('соберите плитку номиналом 4096 в режиме “4x4”', self)
        self.achiev4_desc.setWordWrap(True)
        self.achiev4_desc.setFont(self.font_10)
        self.achiev4_desc.setGeometry(QRect(790, 880 - self.desk_h, 320, 90))
        self.achiev4_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev5_desc = QLabel('соберите плитку номиналом 512 в режиме “3x3”', self)
        self.achiev5_desc.setWordWrap(True)
        self.achiev5_desc.setFont(self.font_10)
        self.achiev5_desc.setGeometry(QRect(1430, 250 - self.desk_h, 320, 90))
        self.achiev5_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev6_desc = QLabel('соберите плитку номиналом 2048 в режиме “быстрая игра”', self)
        self.achiev6_desc.setWordWrap(True)
        self.achiev6_desc.setFont(self.font_10)
        self.achiev6_desc.setGeometry(QRect(1430, 460 - self.desk_h, 320, 90))
        self.achiev6_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev7_desc = QLabel('сложите суммарно 100 000 плиток в режимах “4x4”, “3x3” и “быстрая игра”', self)
        self.achiev7_desc.setWordWrap(True)
        self.achiev7_desc.setFont(self.font_10)
        self.achiev7_desc.setGeometry(QRect(1430, 670 - self.desk_h, 320, 90))
        self.achiev7_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achiev8_desc = QLabel('достигните счёта 1 000 000 в режиме “4x4” или “быстрая игра”', self)
        self.achiev8_desc.setWordWrap(True)
        self.achiev8_desc.setFont(self.font_10)
        self.achiev8_desc.setGeometry(QRect(1430, 900 - self.desk_h, 320, 70))
        self.achiev8_desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.achievment_msg_pad = QWidget(self)
        self.achievment_msg_pad.setGeometry(QRect(1360, self.desk_h + 150, 500, 150))
        self.achievment_msg_text = QLabel('получено новое достижение',self)
        self.achievment_msg_text.setWordWrap(True)
        self.achievment_msg_text.setFont(self.font_18)
        self.achievment_msg_text.setGeometry(QRect(1520, self.desk_h + 175, 330, 100))
        self.achievment_msg_tile = QLabel('!', self)
        self.achievment_msg_tile.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.achievment_msg_tile.setFont(self.font_40)
        self.achievment_msg_tile.setGeometry(QRect(1385, self.desk_h + 175, 100, 100))
        self.achievment_msg = [self.achievment_msg_pad, self.achievment_msg_text, self.achievment_msg_tile]
        self.achievments_dict = {
            self.achiev1_ico: False,
            self.achiev2_ico: False,
            self.achiev3_ico: False,
            self.achiev4_ico: False,
            self.achiev5_ico: False,
            self.achiev6_ico: False,
            self.achiev7_ico: False,
            self.achiev8_ico: False,
        }
        self.achievments_widgets = (self.achievments_title, self.achiev1_pad, self.achiev2_pad, self.achiev3_pad, self.achiev4_pad, self.achiev5_pad, self.achiev6_pad, self.achiev7_pad, self.achiev8_pad,
                                    self.achiev1_title, self.achiev2_title, self.achiev3_title, self.achiev4_title, self.achiev5_title, self.achiev6_title, self.achiev7_title, self.achiev8_title, self.achiev8_2_title,
                                    self.achiev1_ico, self.achiev2_ico, self.achiev3_ico, self.achiev4_ico, self.achiev5_ico, self.achiev6_ico, self.achiev7_ico, self.achiev8_ico,
                                    self.achiev1_desc, self.achiev2_desc, self.achiev3_desc, self.achiev4_desc, self.achiev5_desc, self.achiev6_desc, self.achiev7_desc, self.achiev8_desc)
    
    def rules_window_init(self):
        self.rules_title = QLabel('правила', self)
        self.rules_title.setFont(self.font_50)
        self.rules_title.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.rules_title.setGeometry(QRect(600, 50 - self.desk_h, 1200, 100))
        self.rules_rules = QLabel("""
    используйте стрелки или клавиши WASD на клавиатуре, чтобы перемещать плитки                      
    когда две плитки с одинаковыми числами соприкасаются, они сливаются в одну, чей номинал равен сумме исходных плиток                    
    когда всё игровое поле заполнено плитками и новое действие более невозможно, игра заканчивается                       
    особенности режимов игры:               
    4x4: цель - собрать плитку номиналом 2048         
    3x3: цель - собрать плитку номиналом 512           
    быстрая игра: цель - собрать плитку номиналом 2048, на каждое действие отводится 3 секунды, по истчении которых игра заканчивается               
    пользовательский: произвольный выбор цели (от 4 до 131072), номиналов появляющихся плиток (от 2 до 4096) и шансов их появления (от 0 до 100), ограничения по времени (от 1 до 60) и размеров игрового поля (от 3 до 6)
    при желании Вы можете продолжить играть после достижения основной цели в любом из режимов
        """, self)
        self.rules_rules.setGeometry(QRect(515, 150 - self.desk_h, 1400, 940))
        self.rules_rules.setWordWrap(True)
        self.rules_rules.setFont(self.font_20)
        self.rules_widgets = (self.rules_title, self.rules_rules)

    def stats_window_init(self):
        self.stats_title = QLabel('статистика', self)
        self.stats_title.setFont(self.font_50)
        self.stats_title.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.stats_title.setGeometry(QRect(600, 50 - self.desk_h, 1200, 100))
        self.stats_pad1 = QWidget(self)
        self.stats_pad1.setGeometry(QRect(550, 200 - self.desk_h, 650, 350))
        self.stats_pad2 = QWidget(self)
        self.stats_pad2.setGeometry(QRect(550, 570 - self.desk_h, 650, 350))
        self.stats_pad3 = QWidget(self)
        self.stats_pad3.setGeometry(QRect(1220, 200 - self.desk_h, 650, 350))
        self.stats_pad4 = QWidget(self)
        self.stats_pad4.setGeometry(QRect(1220, 570 - self.desk_h, 650, 350))
        self.stats_mode_title1 = QLabel('4x4', self)
        self.stats_mode_title1.setFont(self.font_35)
        self.stats_mode_title1.setAlignment(Qt.AlignHCenter)
        self.stats_mode_title1.setGeometry(QRect(550, 200 - self.desk_h, 650, 100))
        self.stats_mode_title2 = QLabel('3x3', self)
        self.stats_mode_title2.setFont(self.font_35)
        self.stats_mode_title2.setAlignment(Qt.AlignHCenter)
        self.stats_mode_title2.setGeometry(QRect(550, 570 - self.desk_h, 650, 100))
        self.stats_mode_title3 = QLabel('быстрая игра', self)
        self.stats_mode_title3.setFont(self.font_35)
        self.stats_mode_title3.setAlignment(Qt.AlignHCenter)
        self.stats_mode_title3.setGeometry(QRect(1220, 200 - self.desk_h, 650, 100))
        self.stats_mode_title4 = QLabel('общее', self)
        self.stats_mode_title4.setFont(self.font_35)
        self.stats_mode_title4.setAlignment(Qt.AlignHCenter)
        self.stats_mode_title4.setGeometry(QRect(1220, 570 - self.desk_h, 650, 100))
        self.stats_bs1 = QLabel('лучший счёт:', self)
        self.stats_bs1.setFont(self.font_20)
        self.stats_bs1.setAlignment(Qt.AlignVCenter)
        self.stats_bs1.setGeometry(QRect(575, 300 - self.desk_h, 330, 80))
        self.stats_bs2 = QLabel('лучший счёт:', self)
        self.stats_bs2.setFont(self.font_20)
        self.stats_bs2.setAlignment(Qt.AlignVCenter)
        self.stats_bs2.setGeometry(QRect(575, 675 - self.desk_h, 330, 80))
        self.stats_bs3 = QLabel('лучший счёт:', self)
        self.stats_bs3.setFont(self.font_20)
        self.stats_bs3.setAlignment(Qt.AlignVCenter)
        self.stats_bs3.setGeometry(QRect(1250, 300 - self.desk_h, 330, 80))
        self.stats_bt1 = QLabel('лучшая плитка:', self)
        self.stats_bt1.setFont(self.font_20)
        self.stats_bt1.setAlignment(Qt.AlignVCenter)
        self.stats_bt1.setGeometry(QRect(575, 425 - self.desk_h, 330, 80))
        self.stats_bt2 = QLabel('лучшая плитка:', self)
        self.stats_bt2.setFont(self.font_20)
        self.stats_bt2.setAlignment(Qt.AlignVCenter)
        self.stats_bt2.setGeometry(QRect(575, 800 - self.desk_h, 330, 80))
        self.stats_bt3 = QLabel('лучшая плитка:', self)
        self.stats_bt3.setFont(self.font_20)
        self.stats_bt3.setAlignment(Qt.AlignVCenter)
        self.stats_bt3.setGeometry(QRect(1250, 425 - self.desk_h, 330, 80))
        self.stats_ttm = QLabel('сложено плиток:', self)
        self.stats_ttm.setFont(self.font_20)
        self.stats_ttm.setAlignment(Qt.AlignVCenter)
        self.stats_ttm.setGeometry(QRect(1250, 675 - self.desk_h, 360, 80))
        self.stats_ac = QLabel('получено достижений:', self)
        self.stats_ac.setFont(self.font_20)
        self.stats_ac.setAlignment(Qt.AlignVCenter)
        self.stats_ac.setGeometry(QRect(1250, 800 - self.desk_h, 480, 80))
        self.stats_bs1_val = QLabel(str(self.best_scores_lst[0]), self)
        self.stats_bs1_val.setFont(self.font_20)
        self.stats_bs1_val.setAlignment(Qt.AlignVCenter)
        self.stats_bs1_val.setGeometry(QRect(875, 300 - self.desk_h, 300, 80))
        self.stats_bs2_val = QLabel(str(self.best_scores_lst[1]), self)
        self.stats_bs2_val.setFont(self.font_20)
        self.stats_bs2_val.setAlignment(Qt.AlignVCenter)
        self.stats_bs2_val.setGeometry(QRect(875, 675 - self.desk_h, 300, 80))
        self.stats_bs3_val = QLabel(str(self.best_scores_lst[2]), self)
        self.stats_bs3_val.setFont(self.font_20)
        self.stats_bs3_val.setAlignment(Qt.AlignVCenter)
        self.stats_bs3_val.setGeometry(QRect(1550, 300 - self.desk_h, 300, 80))
        self.stats_bt1_val = QLabel(str(self.best_tiles_lst[0]), self)
        self.stats_bt1_val.setFont(self.font_20)
        self.stats_bt1_val.setAlignment(Qt.AlignVCenter)
        self.stats_bt1_val.setGeometry(QRect(925, 425 - self.desk_h, 250, 80))
        self.stats_bt2_val = QLabel(str(self.best_tiles_lst[1]), self)
        self.stats_bt2_val.setFont(self.font_20)
        self.stats_bt2_val.setAlignment(Qt.AlignVCenter)
        self.stats_bt2_val.setGeometry(QRect(925, 800 - self.desk_h, 250, 80))
        self.stats_bt3_val = QLabel(str(self.best_tiles_lst[2]), self)
        self.stats_bt3_val.setFont(self.font_20)
        self.stats_bt3_val.setAlignment(Qt.AlignVCenter)
        self.stats_bt3_val.setGeometry(QRect(1600, 425 - self.desk_h, 250, 80))
        self.stats_ttm_val = QLabel(str(self.merge_cnt), self)
        self.stats_ttm_val.setFont(self.font_20)
        self.stats_ttm_val.setAlignment(Qt.AlignVCenter)
        self.stats_ttm_val.setGeometry(QRect(1620, 675 - self.desk_h, 230, 80))
        self.stats_ac_val = QLabel(str(self.achievments_cnt), self)
        self.stats_ac_val.setFont(self.font_20)
        self.stats_ac_val.setAlignment(Qt.AlignVCenter)
        self.stats_ac_val.setGeometry(QRect(1740, 800 - self.desk_h, 110, 80))
        self.stats_widgets = (self.stats_title, self.stats_pad1, self.stats_pad2, self.stats_pad3, self.stats_pad4,
                              self.stats_mode_title1, self.stats_mode_title2, self.stats_mode_title3, self.stats_mode_title4,
                              self.stats_bs1, self.stats_bs2, self.stats_bs3, self.stats_ttm, 
                              self.stats_bt1, self.stats_bt2, self.stats_bt3, self.stats_ac,
                              self.stats_bs1_val, self.stats_bs2_val, self.stats_bs3_val, self.stats_ttm_val, 
                              self.stats_bt1_val, self.stats_bt2_val, self.stats_bt3_val, self.stats_ac_val)
        
    def menu_init(self):
        self.menu_pad = QWidget(self)
        self.menu_pad.setGeometry(-350, 0, 500, self.desk_h)
        self.menu_menu = QWidget(self)
        self.menu_menu.setGeometry(-450, 25, 600, 150)
        self.menu_txt = QLabel('меню', self)
        self.menu_txt.setGeometry(-350, 50, 350, 100)
        self.menu_txt.setFont(self.font_50)
        self.menu_txt.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.menu_rnd = QLabel(self)
        self.menu_rnd.setGeometry(10, 40, 120, 120)
        self.menu_btn = QPushButton(self)
        self.menu_btn.setGeometry(-450, 25, 600, 150)
        self.menu_btn.clicked.connect(self.menu_btn_action)
        self.menu_btn.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.menu_game_h = QWidget(self)
        self.menu_mode_h = QWidget(self)
        self.menu_theme_h = QWidget(self)
        self.menu_achievments_h = QWidget(self)
        self.menu_rules_h = QWidget(self)
        self.menu_stats_h = QWidget(self)
        self.menu_tile = QWidget(self)
        self.menu_game = QPushButton(self, text='игра')
        self.menu_mode = QPushButton(self, text='режим')
        self.menu_theme = QPushButton(self, text='тема')
        self.menu_achievments = QPushButton(self, text='достижения')
        self.menu_rules = QPushButton(self, text='правила')
        self.menu_stats = QPushButton(self, text='статистика')
        self.menu_exit = QPushButton(self, text='выход')
        self.menu_game.clicked.connect(lambda: self.window_change(0))
        self.menu_mode.clicked.connect(lambda: self.window_change(1))
        self.menu_theme.clicked.connect(lambda: self.window_change(2))
        self.menu_achievments.clicked.connect(lambda: self.window_change(3))
        self.menu_rules.clicked.connect(lambda: self.window_change(4))
        self.menu_stats.clicked.connect(lambda: self.window_change(5))
        self.menu_exit.clicked.connect(self.close_app)
        self.menu_game.setFont(self.font_30)
        self.menu_mode.setFont(self.font_30)
        self.menu_theme.setFont(self.font_30)
        self.menu_achievments.setFont(self.font_30)
        self.menu_rules.setFont(self.font_30)
        self.menu_stats.setFont(self.font_30)
        self.menu_exit.setFont(self.font_30)
        self.menu_game.setGeometry(-475, 200, 450, 100)
        self.menu_mode.setGeometry(-475, 325, 450, 100)
        self.menu_theme.setGeometry(-475, 450, 450, 100)
        self.menu_achievments.setGeometry(-475, 575, 450, 100)
        self.menu_rules.setGeometry(-475, 700, 450, 100)
        self.menu_stats.setGeometry(-475, 825, 450, 100)
        self.menu_exit.setGeometry(-395, 975, 300, 100)
        self.menu_tile.setGeometry(-475, 200, 450, 100)
        self.menu_game_h.setGeometry(-475, 200, 450, 100)
        self.menu_mode_h.setGeometry(-475, 325, 450, 100)
        self.menu_theme_h.setGeometry(-475, 450, 450, 100)
        self.menu_achievments_h.setGeometry(-475, 575, 450, 100)
        self.menu_rules_h.setGeometry(-475, 700, 450, 100)
        self.menu_stats_h.setGeometry(-475, 825, 450, 100)
        self.menu_widgets = (self.menu_menu, self.menu_btn, self.menu_pad, self.menu_rnd, self.menu_txt)
        self.menu_points = (self.menu_game, self.menu_mode, self.menu_theme, self.menu_achievments, self.menu_rules, self.menu_stats,
                            self.menu_game_h, self.menu_mode_h, self.menu_theme_h, self.menu_achievments_h, self.menu_rules_h, self.menu_stats_h,
                            self.menu_exit, self.menu_tile)
        
    def menu_btn_action(self):
        if not self.isTimerEnable or self.isGameEnded:
            self.move_menu()

    def new_mode_start(self, mode: int):
        if self.isWindowAnimEnd:
            settings_panel.check_input()
            self.game_window_del()
            self.choose_mode(mode)
            self.game_window_init_new()
            self.game_window_show() 

    def window_change(self, newwin: int):
        if self.curwin != newwin and self.menu_btn.isEnabled():
            self.newwin = newwin
            settings_panel.move_with_window_step1()
            for btn in self.windows_btns:
                btn.setDisabled(True)
            window_anim_group = QParallelAnimationGroup(self)
            for widget in self.windows[self.curwin]:
                if isinstance(widget, list):
                    for i in range(self.ysize):
                        for j in range(self.xsize):
                            window_anim = QPropertyAnimation(widget[i][j][0], b"pos")
                            window_anim.setEasingCurve(QEasingCurve.OutCubic)
                            window_anim.setEndValue(QPoint(widget[i][j][0].x(), widget[i][j][0].y() + self.desk_h))
                            window_anim.setDuration(400)
                            window_anim_group.addAnimation(window_anim)
                else:
                    window_anim = QPropertyAnimation(widget, b"pos")
                    window_anim.setEasingCurve(QEasingCurve.OutCubic)
                    window_anim.setEndValue(QPoint(widget.x(), widget.y() + self.desk_h))
                    window_anim.setDuration(400)
                    window_anim_group.addAnimation(window_anim)
            for widget in self.windows[newwin]:
                if isinstance(widget, list):
                    for i in range(self.ysize):
                        for j in range(self.xsize):
                            window_anim = QPropertyAnimation(widget[i][j][0], b"pos")
                            window_anim.setEasingCurve(QEasingCurve.OutCubic)
                            window_anim.setEndValue(QPoint(widget[i][j][0].x(), widget[i][j][0].y() + self.desk_h))
                            window_anim.setDuration(400)
                            window_anim_group.addAnimation(window_anim)
                else: 
                    window_anim = QPropertyAnimation(widget, b"pos")
                    window_anim.setEasingCurve(QEasingCurve.OutCubic)
                    window_anim.setEndValue(QPoint(widget.x(), widget.y() + self.desk_h))
                    window_anim.setDuration(400)
                    window_anim_group.addAnimation(window_anim)
            menu_tile_anim = QPropertyAnimation(self.menu_tile, b"pos")
            menu_tile_anim.setEasingCurve(QEasingCurve.OutCubic)
            menu_tile_anim.setEndValue(QPoint(self.menu_tile.x(), 200 + 125 * newwin))
            menu_tile_anim.setDuration(400)
            window_anim_group.addAnimation(menu_tile_anim)
            self.isWindowAnimEnd = False
            window_anim_group.start()
            self.window_timer.start()

    def move_window(self):
        for btn in self.windows_btns:
            btn.setDisabled(False)
        window_anim_group = QParallelAnimationGroup(self)
        for widget in self.windows[self.curwin]:
            if isinstance(widget, list):
                for i in range(self.ysize):
                    for j in range(self.xsize):
                        window_anim = QPropertyAnimation(widget[i][j][0], b"pos")
                        window_anim.setEndValue(QPoint(widget[i][j][0].x(), widget[i][j][0].y() - 2 * self.desk_h))
                        window_anim.setDuration(0)
                        window_anim_group.addAnimation(window_anim)
            else:
                window_anim = QPropertyAnimation(widget, b"pos")
                window_anim.setEndValue(QPoint(widget.x(), widget.y() - 2 * self.desk_h))
                window_anim.setDuration(0)
                window_anim_group.addAnimation(window_anim)
        window_anim_group.start()
        self.curwin = self.newwin
        self.window_timer.stop()
        self.isWindowAnimEnd = True
            
    def move_menu(self):
        if self.isMovingAble and self.isWindowAnimEnd:
            settings_panel.move_with_menu()
            self.isMenuActive = not self.isMenuActive
            menu_anim_group = QParallelAnimationGroup(self)
            if not self.isMenuActive:
                shift1 = -350
                shift2 = -500
            else:
                shift1 = 350
                shift2 = 500
            for widget in self.menu_widgets:
                menu_anim = QPropertyAnimation(widget, b"pos")
                menu_anim.setEasingCurve(QEasingCurve.OutCubic)
                menu_anim.setEndValue(QPoint(widget.x() + shift1, widget.y()))
                menu_anim.setDuration(300)
                menu_anim_group.addAnimation(menu_anim)
            for widget in self.menu_points:
                menu_anim = QPropertyAnimation(widget, b"pos")
                menu_anim.setEasingCurve(QEasingCurve.OutCubic)
                menu_anim.setEndValue(QPoint(widget.x() + shift2, widget.y()))
                menu_anim.setDuration(400)
                menu_anim_group.addAnimation(menu_anim)
            for widget in self.windows[self.curwin]:
                if isinstance(widget, list):
                    for i in range(self.ysize):
                        for j in range(self.xsize):
                            window_anim = QPropertyAnimation(widget[i][j][0], b"pos")
                            window_anim.setEasingCurve(QEasingCurve.OutCubic)
                            window_anim.setEndValue(QPoint(widget[i][j][0].x() + shift1 // 2, widget[i][j][0].y()))
                            window_anim.setDuration(400)
                            menu_anim_group.addAnimation(window_anim)
                else:
                    window_anim = QPropertyAnimation(widget, b"pos")
                    window_anim.setEasingCurve(QEasingCurve.OutCubic)
                    window_anim.setEndValue(QPoint(widget.x() + shift1 // 2, widget.y()))
                    window_anim.setDuration(400)
                    menu_anim_group.addAnimation(window_anim)
            menu_anim_group.start()
            self.menu_btn.setEnabled(False)
            self.menu_timer.start()

    def get_game_state(self):
        if not self.isWinner:
            for i in range(self.ysize):
                for j in range(self.xsize):
                    if self.game_area[i][j][2] == self.winnomin:
                        return 'win'
        for i in range(self.ysize):
            for j in range(self.xsize):
                if self.game_area[i][j][0] == None:
                    return 'continue'
                if j < self.xsize - 1:
                    if self.game_area[i][j][2] == self.game_area[i][j + 1][2]:
                        return 'continue'
                if i < self.ysize - 1:
                    if self.game_area[i][j][2] == self.game_area[i + 1][j][2]:
                        return 'continue'
        return 'end'
    
    def move_tiles(self, direction: str):
        match direction:
            case 'left':
                for i in range(self.ysize):
                    for j in range(1, self.xsize):
                        new_pos = j - 1
                        if self.game_area[i][j][0] == None:
                            continue
                        while new_pos != -1 and self.game_area[i][new_pos][0] == None:
                            new_pos -= 1
                        if new_pos == -1 or self.game_area[i][new_pos][2] != self.game_area[i][j][2]:
                            new_pos += 1
                            self.game_area[i][new_pos] = self.game_area[i][j]
                            if new_pos != j:
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                        else:
                            if self.game_area[i][new_pos][1] == None:
                                self.game_area[i][new_pos][1] = self.game_area[i][j][0]
                                self.game_area[i][new_pos][2] *= 2
                                self.score += self.game_area[i][new_pos][2]
                                if self.curmode != 3:
                                    self.merge_cnt += 1
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                            else:
                                new_pos += 1
                                self.game_area[i][new_pos] = self.game_area[i][j]
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
            case 'right':
                for i in range(self.ysize):
                    for j in range(self.xsize - 2, -1, -1):
                        new_pos = j + 1
                        if self.game_area[i][j][0] == None:
                            continue
                        while new_pos != self.xsize and self.game_area[i][new_pos][0] == None:
                            new_pos += 1
                        if new_pos == self.xsize or self.game_area[i][new_pos][2] != self.game_area[i][j][2]:
                            new_pos -= 1
                            self.game_area[i][new_pos] = self.game_area[i][j]
                            if new_pos != j:
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                        else:
                            if self.game_area[i][new_pos][1] == None:
                                self.game_area[i][new_pos][1] = self.game_area[i][j][0]
                                self.game_area[i][new_pos][2] *= 2
                                self.score += self.game_area[i][new_pos][2]
                                if self.curmode != 3:
                                    self.merge_cnt += 1
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                            else:
                                new_pos -= 1
                                self.game_area[i][new_pos] = self.game_area[i][j]
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
            case 'up':
                for j in range(self.xsize):
                    for i in range(1, self.ysize):
                        new_pos = i - 1
                        if self.game_area[i][j][0] == None:
                            continue
                        while new_pos != -1 and self.game_area[new_pos][j][0] == None:
                            new_pos -= 1
                        if new_pos == -1 or self.game_area[new_pos][j][2] != self.game_area[i][j][2]:
                            new_pos += 1
                            self.game_area[new_pos][j] = self.game_area[i][j]
                            if new_pos != i:
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                        else:
                            if self.game_area[new_pos][j][1] == None:
                                self.game_area[new_pos][j][1] = self.game_area[i][j][0]
                                self.game_area[new_pos][j][2] *= 2
                                self.score += self.game_area[new_pos][j][2]
                                if self.curmode != 3:
                                    self.merge_cnt += 1
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                            else:
                                new_pos += 1
                                self.game_area[new_pos][j] = self.game_area[i][j]
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
            case 'down':
                for j in range(self.xsize):
                    for i in range(self.ysize - 2, -1, -1):
                        new_pos = i + 1
                        if self.game_area[i][j][0] == None:
                            continue
                        while new_pos != self.ysize and self.game_area[new_pos][j][0] == None:
                            new_pos += 1
                        if new_pos == self.ysize or self.game_area[new_pos][j][2] != self.game_area[i][j][2]:
                            new_pos -= 1
                            self.game_area[new_pos][j] = self.game_area[i][j]
                            if new_pos != i:
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                        else:
                            if self.game_area[new_pos][j][1] == None:
                                self.game_area[new_pos][j][1] = self.game_area[i][j][0]
                                self.game_area[new_pos][j][2] *= 2
                                self.score += self.game_area[new_pos][j][2]
                                if self.curmode != 3:
                                    self.merge_cnt += 1
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
                            else:
                                new_pos -= 1
                                self.game_area[new_pos][j] = self.game_area[i][j]
                                self.game_area[i][j] = [None, None, 2]
                                self.changes = True
        for i in range(self.ysize):
            for j in range(self.xsize):
                if self.game_area[i][j][0] != None:
                    tile_anim = QPropertyAnimation(self.game_area[i][j][0], b"pos")
                    tile_anim.setEndValue(QPoint(self.game_area_pos[i][j][0], self.game_area_pos[i][j][1]))
                    tile_anim.setDuration(200)
                    tile_anim.setEasingCurve(QEasingCurve.OutCubic)
                    self.pos_anim.addAnimation(tile_anim)
                    if self.game_area[i][j][1] != None:
                        tile_anim = QPropertyAnimation(self.game_area[i][j][1], b"pos")
                        tile_anim.setEndValue(QPoint(self.game_area_pos[i][j][0], self.game_area_pos[i][j][1]))
                        tile_anim.setDuration(200)
                        tile_anim.setEasingCurve(QEasingCurve.OutCubic)
                        self.pos_anim.addAnimation(tile_anim)
        self.pos_anim.start()
    
    def add_tiles(self, amount_of_tiles: int, start=False, tiles=[]):
        for k in range(amount_of_tiles):
            self.isMovingAble = False
            sec_break = False
            for i in range(self.ysize):
                if sec_break:
                    break
                for j in range(self.xsize):
                    if not self.tiles_lst[i][j][1]:
                        self.tiles_lst[i][j][1] = True
                        if not start:
                            r, c = random.randint(0, self.ysize - 1), random.randint(0, self.xsize - 1)
                            while self.game_area[r][c][0] != None:
                                r, c = random.randint(0, self.ysize - 1), random.randint(0, self.xsize - 1)
                            if random.randint(1, 100) <= self.chance:
                                self.game_area[r][c][2] = self.new_tile_nomin2
                            else:
                                self.game_area[r][c][2] = self.new_tile_nomin1
                        else:
                            r, c = tiles[k][0], tiles[k][1]
                            self.game_area[r][c][2] = tiles[k][2]
                        self.game_area[r][c][0] = self.tiles_lst[i][j][0]
                        self.game_area[r][c][0].setVisible(True)
                        self.game_area[r][c][0].setText(str(self.game_area[r][c][2]))
                        self.game_area[r][c][0].setGeometry(QRect(self.game_area_pos[r][c][0], self.game_area_pos[r][c][1], 0, 0))
                        new_tile_font = self.font_40
                        new_tile_font.setPointSize(44 - len(str(self.game_area[r][c][2])) * 4)
                        if new_tile_font.pointSize() < 7:
                                new_tile_font.setPointSize(10)
                        self.game_area[r][c][0].setFont(new_tile_font)
                        size_anim = QPropertyAnimation(self.game_area[r][c][0], b'geometry')
                        size_anim.setStartValue(QRect(self.game_area[r][c][0].geometry().adjusted(70, 70, 0, 0)))
                        size_anim.setEndValue(QRect(self.game_area[r][c][0].geometry().adjusted(0, 0, 150, 150)))
                        size_anim.setEasingCurve(QEasingCurve.InOutQuad)
                        size_anim.setDuration(100)
                        if self.game_area[r][c][2] < 8:
                            text_color = self.text_color1
                        else:
                            text_color = self.text_color2
                        if self.game_area[r][c][2] < 4096:
                            bg_color = self.color_dict[self.game_area[r][c][2]]
                        else:
                            bg_color = self.text_color1
                        self.game_area[r][c][0].setStyleSheet('background-color: %s; color: %s; border-radius: 10' % (bg_color, text_color))
                        self.size_anim.addAnimation(size_anim)
                        sec_break = True
                        break
                self.move_timer.start()
                self.size_anim.start()

    def game_window_del(self):
        self.grid.removeWidget(self.timer_tile)
        for widget in self.windows[0]:
            if isinstance(widget, list):
                for i in range(self.ysize):
                    for j in range(self.xsize):
                        widget[i][j][0].deleteLater()
                        del widget[i][j][0]
            else:
                widget.deleteLater()
                del widget

    def game_window_show(self):
        for widget in self.windows[0]:
            if isinstance(widget, list):
                for i in range(self.ysize):
                    for j in range(self.xsize):
                        widget[i][j][0].show()
            else:
                widget.show()

    def game_window_init_new(self):
        self.score = 0
        self.game_window_init()
        self.opacity.setOpacity(0)
        self.windows[0] = self.game_widgets
        new_game_init_anim_group = QParallelAnimationGroup(self)
        if self.isMenuActive:
            shiftx = 175
        else:
            shiftx = 0
        if self.curwin == 0:
            shifty = 0
        else:
            shifty = 1200
        for widget in self.windows[0]:
                if isinstance(widget, list):
                    for i in range(self.ysize):
                        for j in range(self.xsize):
                            new_game_init_anim = QPropertyAnimation(widget[i][j][0], b"pos")
                            new_game_init_anim.setEndValue(QPoint(widget[i][j][0].x() + shiftx, widget[i][j][0].y() - shifty))
                            new_game_init_anim.setDuration(0)
                            new_game_init_anim_group.addAnimation(new_game_init_anim)
                else:
                    new_game_init_anim = QPropertyAnimation(widget, b"pos")
                    new_game_init_anim.setEndValue(QPoint(widget.x() + shiftx, widget.y() - shifty))
                    new_game_init_anim.setDuration(0)
                    new_game_init_anim_group.addAnimation(new_game_init_anim)
        new_game_init_anim_group.start()
        self.window_change(0)
        self.clr_change(self.clrtheme)
        self.new_game_timer.start()

    def new_game_tiles(self):
        if self.isMenuActive:
            self.move_menu()
            self.new_game_timer.setInterval(400)
        else:
            self.new_game_timer.stop()
            self.add_tiles(2)

    def game_window_init(self):
        self.isMovingAble = True
        self.game_area_pos = [[[] for j in range(self.xsize)] for i in range(self.ysize)]
        self.game_area = [[[None, None, 2] for j in range(self.xsize)] for i in range(self.ysize)]
        self.tileposy = round(self.desk_h - 162.5 * self.ysize) // 2
        for i in range(self.ysize):
            self.tileposx = round(self.desk_w - 162.5 * self.xsize) // 2
            self.tileposy += 10
            if self.ysize == 6:
                self.tileposy += 1
            if i > 0:
                self.tileposy += 150
            for j in range(self.xsize):
                self.tileposx += 10
                if self.xsize == 6:
                    self.tileposx += 1
                if j > 0:
                    self.tileposx += 150              
                self.game_area_pos[i][j].append(self.tileposx)
                self.game_area_pos[i][j].append(self.tileposy)

        self.bg_plain = QWidget(self)
        self.bg_plain.setGeometry(round(self.desk_w - 162.5 * self.xsize) // 2, round(self.desk_h - 162.5 * self.ysize) // 2, round(162.5 * self.xsize), round(162.5 * self.ysize))
        self.score_plain = QLabel("счёт", self)
        self.score_plain.setGeometry((self.desk_w - 650) // 2 + 300, round(self.desk_h - 162.5 * self.ysize) // 2 - 100, 150, 75)
        self.score_plain.setFont(self.font_14)
        self.score_plain.setAlignment(Qt.AlignHCenter)
        self.score_value = QLabel(str(self.score), self)
        self.score_value.setGeometry((self.desk_w - 650) // 2 + 300, round(self.desk_h - 162.5 * self.ysize) // 2 - 67, 150, 30)
        self.score_value.setFont(self.font_14)
        self.score_value.setAlignment(Qt.AlignHCenter)
        self.best_plain = QLabel("лучший", self)
        self.best_plain.setGeometry((self.desk_w - 650) // 2 + 490, round(self.desk_h - 162.5 * self.ysize) // 2 - 100, 150, 75)
        self.best_plain.setFont(self.font_14)
        self.best_plain.setAlignment(Qt.AlignHCenter)
        self.best_value = QLabel(str(self.best_scores_lst[self.curmode]), self)
        self.best_value.setGeometry((self.desk_w - 650) // 2 + 490, round(self.desk_h - 162.5 * self.ysize) // 2 - 67, 150, 30)
        self.best_value.setFont(self.font_14)
        self.best_value.setAlignment(Qt.AlignHCenter)
        self.icon = QLabel(self)
        self.icon.setText("2048")
        self.icon.setGeometry((self.desk_w - 650) // 2 + 8, round(self.desk_h - 162.5 * self.ysize) // 2 - 112, 255, 90)
        self.icon.setFont(self.font_50)
        self.tiles_lst = list()
        self.hollows_lst = list()
        for i in range(self.ysize):
            self.hollows_lst.append([])
            for j in range(self.xsize):
                globals()['hollow' + str( i * (j + 1) + j + 1)] = QWidget(self)
                self.hollows_lst[i].append([globals()['hollow' + str(i * (j + 1) + j + 1)]])
        for i in range(self.ysize):
            self.tiles_lst.append([])
            for j in range(self.xsize):
                globals()['tile' + str(i * (j + 1) + j + 1)] = QLabel(self)
                self.tiles_lst[i].append([globals()['tile' + str(i * (j + 1) + j + 1)], False])
        self.pos_anim = QParallelAnimationGroup()
        self.size_anim = QParallelAnimationGroup()
        for i in range(self.ysize):
            for j in range(self.xsize):
                self.tiles_lst[i][j][0].setGeometry(self.game_area_pos[i][j][0], self.game_area_pos[i][j][1], 0, 0)
                self.tiles_lst[i][j][0].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.hollows_lst[i][j][0].setGeometry(self.game_area_pos[i][j][0], self.game_area_pos[i][j][1], 150, 150)
        self.winlose_msg_pad = QWidget(self)
        self.winlose_msg_pad.setGeometry(round(self.desk_w - 162.5 * self.xsize) // 2, round(self.desk_h - 162.5 * self.ysize) // 2, round(162.5 * self.xsize), round(162.5 * self.ysize))
        self.winlose_msg_pad.setGraphicsEffect(self.opacity)
        self.new_game_btn_panel = QLabel('начать\nновую игру', self)
        self.new_game_btn_panel.setGeometry(QRect(670, 730, 0, 0))
        self.new_game_btn_panel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.new_game_btn_panel.setFont(self.font_16)
        self.change_mode_btn_panel = QLabel('сменить\nрежим', self)
        self.change_mode_btn_panel.setGeometry(QRect(980, 730, 0, 0))
        self.change_mode_btn_panel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.change_mode_btn_panel.setFont(self.font_16)
        self.continue_game_btn_panel = QLabel('продолжить\nтекущую игру', self)
        self.continue_game_btn_panel.setGeometry(QRect(980, 730, 0, 0))
        self.continue_game_btn_panel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.continue_game_btn_panel.setFont(self.font_16)
        self.new_game_btn = QPushButton(self)
        self.new_game_btn.clicked.connect(self.new_game_btn_action)
        self.new_game_btn.setGeometry(QRect(670, 730, 0, 0))
        self.new_game_btn.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.change_mode_btn = QPushButton(self)
        self.change_mode_btn.clicked.connect(self.change_mode_btn_action)
        self.change_mode_btn.setGeometry(QRect(980, 730, 0, 0))
        self.change_mode_btn.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.continue_game_btn = QPushButton(self)
        self.continue_game_btn.clicked.connect(self.continue_game_btn_action)
        self.continue_game_btn.setGeometry(QRect(980, 730, 0, 0))
        self.continue_game_btn.setStyleSheet('background-color: rgba(0, 0, 0, 0.0)')
        self.winlose_msg_text = QLabel(self)
        self.font_var.setPointSize(12 * max(self.ysize, self.xsize))
        self.winlose_msg_text.setGeometry(QRect(round(1920 - 162.5 * self.xsize) // 2, 400 - 25 * self.ysize, round(162.5 * self.xsize), 310))
        self.winlose_msg_text.setFont(self.font_var)
        self.winlose_msg_text.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        if self.isTimerEnable:
            self.timer_tile = Timer()
            self.timer_tile.start()
        else:
            self.timer_tile = QWidget(self)
            self.timer_tile.resize(0, 0)
        self.isGameEnded = False
        self.game_widgets = [self.tiles_lst, self.hollows_lst, self.bg_plain, self.best_plain, self.score_plain, self.icon, self.score_value, self.best_value, 
                             self.winlose_msg_pad, self.new_game_btn, self.change_mode_btn, self.continue_game_btn,
                             self.new_game_btn_panel, self.change_mode_btn_panel, self.continue_game_btn_panel, self.winlose_msg_text,
                             self.timer_tile]

    def new_game_btn_action(self):
        self.game_window_del()
        self.game_window_init_new()
        self.game_window_show()
        self.isGameEnded = False
        self.isWinner = False

    def change_mode_btn_action(self):
        if not self.isMenuActive:
            self.move_menu()
            self.change_mode_timer.setInterval(600)
            self.change_mode_timer.start()
        else:
            self.change_mode_timer.setInterval(0)
            self.change_mode_timer.start()

    def change_mode_timer_action(self):
        self.change_mode_timer.stop()
        self.window_change(1)
        self.isGameEnded = False

    def continue_game_btn_action(self):
        self.opacity.setOpacity(0)
        self.new_game_btn.setGeometry(QRect(self.new_game_btn.geometry().adjusted(0, 0, -270, -80)))
        self.continue_game_btn.setGeometry(QRect(self.continue_game_btn.geometry().adjusted(0, 0, -270, -80)))
        self.new_game_btn_panel.setGeometry(QRect(self.new_game_btn.geometry()))
        self.continue_game_btn_panel.setGeometry(QRect(self.continue_game_btn.geometry()))
        self.winlose_msg_text.setText('')
        self.isGameEnded = False
        if self.isTimerEnable:
            self.timer_tile.start()

    def enable_moving(self):
        self.move_timer.stop()
        self.isMovingAble = True

    def after_action(self):
        self.timer_times += 1
        if self.timer_times == 2:
            self.add_tiles(1)
            self.action_timer.setInterval(100)
        elif self.timer_times == 3:
            self.action_timer.stop()
            self.show_winlose_msg(self.get_game_state())
            self.achievments_check()
            self.stats_update()
        else:
            self.set_tiles_style()
            for i in range(self.ysize):
                for j in range(self.xsize):
                    if self.game_area[i][j][2] > self.best_tiles_lst[self.curmode]:
                        self.best_tiles_lst[self.curmode] = self.game_area[i][j][2]
                    if self.game_area[i][j][0] != None:
                        if self.game_area[i][j][1] != None:
                            self.game_area[i][j][1].setGeometry(self.game_area_pos[i][j][0], self.game_area_pos[i][j][1], 0, 0)
                            for r in range(self.ysize):
                                for c in range(self.xsize):
                                    if self.tiles_lst[r][c][0] == self.game_area[i][j][1]:
                                        self.tiles_lst[r][c][1] = False
                                        self.game_area[i][j][1] = None
            self.action_timer.setInterval(50)

    def enable_menu_moving(self):
        self.menu_btn.setEnabled(True)
        self.menu_timer.stop()

    def keyPressEvent(self, e):
        self.changes = False
        if self.isMovingAble and not self.isMenuActive and not self.isGameEnded and self.curwin == 0 and self.menu_btn.isEnabled():
            self.pos_anim = QParallelAnimationGroup()
            self.size_anim = QParallelAnimationGroup()
            if e.key() == Qt.Key_D or e.key() == Qt.Key_Right or e.key() == 1042:
                self.move_tiles('right')
            elif e.key() == Qt.Key_A or e.key() == Qt.Key_Left or e.key() == 1060:
                self.move_tiles('left')
            elif e.key() == Qt.Key_W or e.key() == Qt.Key_Up or e.key() == 1062:
                self.move_tiles('up')
            elif e.key() == Qt.Key_S or e.key() == Qt.Key_Down or e.key() == 1067:
                self.move_tiles('down')
            if self.changes:
                self.score_value.setText(str(self.score))
                if self.score > self.best_scores_lst[self.curmode]:
                    self.best_scores_lst[self.curmode] = self.score
                    self.best_value.setText(str(self.best_scores_lst[self.curmode]))
                self.isMovingAble = False
                self.timer_times = 0
                if self.isTimerEnable:
                    self.timer_tile.restart()
                self.action_timer.start()

    def close_app(self):
        self.write_save_file()
        self.close()
save_path = 'save.sav'
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.showMaximized()
settings_panel = SettingsPanel()
for btn in (
    main_window.windows_btns + 
    [settings_panel.back_btn, settings_panel.start_btn] + 
    [main_window.new_game_btn, main_window.continue_game_btn, main_window.change_mode_btn, main_window.mode_btn1, main_window.mode_btn2, main_window.mode_btn3, main_window.mode_btn3, main_window.mode_btn4, main_window.theme1_btn, main_window.theme2_btn, main_window.theme3_btn, main_window.menu_exit, main_window.menu_btn]
): btn.setFocusPolicy(Qt.NoFocus)
main_window.clr_change(main_window.clrtheme)
if not main_window.isSaveExists:
    main_window.add_tiles(2)
else:
    main_window.add_tiles(main_window.game_area_config.pop(-1), True, main_window.game_area_config)
sys.exit(app.exec_())