# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 18:52:37 2021

@author: circi
"""

import json
import sys
from PyQt5.QtCore import Qt
from PyQt5 import  QtWidgets
from PyQt5.QtWidgets import QFileDialog, QDialog, QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QAbstractItemView, QAction, QInputDialog
#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
from PyQt5 import uic 
import winreg as reg  
import os
from pathlib import Path
import shutil
#from distutils.dir_util import copy_tree
#from distutils.dir_util import _path_created
#import time
#import distutils 
import configparser
import zipfile
import sqlite3


#path
d2rPath = ""
path_config = "./config/config.ini"
path_modinfo = "./config/modinfo.json"
config = configparser.ConfigParser()


#ui
form_class = uic.loadUiType("./config/seonhee.ui")[0]
Ui_InputSkin,_ = uic.loadUiType("./config/input_skin.ui")

skinList = []
folderPathList = []
filePathList = []



#db
# =============================================================================
# filePathDB = []
# with open('filePathDb.txt','r', encoding='UTF-8') as f:
#     lines = f.readlines()
#     for strs in lines:
#         splitStr = strs.split(',')
#         filePathDB.append(splitStr)
# 
# =============================================================================
#conn = sqlite3.connect("file:FileDB.db?mode=ro")
conn = sqlite3.connect('./config/FileDB.db')
cur = conn.cursor()

##
class MyWindow(QMainWindow, form_class):
    def getReg(self):
        try:
            key = reg.HKEY_LOCAL_MACHINE
            key_value = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Diablo II Resurrected"
            open = reg.OpenKey(key,key_value,0,reg.KEY_ALL_ACCESS)
            try:
                value, type = reg.QueryValueEx(open,"InstallLocation")
            except:
                value = ""
                #reply = QMessageBox.question(self, 'Message', "", QMessageBox.Yes , QMessageBox.Yes)
                self.listWidgetDebug.addItem("D2R 폴더를 찾지못했어요! 수동으로라도 등록해주세요!")
            #print(value)
            # now close the opened key 
            reg.CloseKey(open)
        except:
            value = ""
            self.listWidgetDebug.addItem("D2R 폴더를 찾지못했어요! 수동으로라도 등록해주세요!")
            return
        
        global d2rPath
        d2rPath = value
        
        

        
    def table_cell_clicked(self, row, col):
        #cell = self.tableWidgetMain.item(row, col)
        #print(cell)
        self.tableWidgetMain.item(row, col)
        
        if col == 0: #스위칭 해준다
            print("row =",row)
            skinList[row][1] = 0 if skinList[row][1] == 1 else 1
            str = 'X'
            if skinList[row][1] == 1:
                str = '적용'
            self.tableWidgetMain.setItem(row, 0, QTableWidgetItem(str))
        return
    
    def files_load(self):
        while len(skinList) > 0 : skinList.pop()
        
        #폴더 읽어오기
        path_dir = './files'
        fileList = os.listdir(path_dir)
        #print(fileList)
        iLen = len(fileList)
        self.tableWidgetMain.setRowCount(iLen)
        
        for i in range(iLen):
            skinList.append([i,0,fileList[i],'']) #0:순서, 1:사용여부(0:안함 1:사용), 2:이름, 3:설명
            #폴더들 돌면서 readme.txt가 있으면 가져온다
            readPath = './files/' + fileList[i] + '/readme.txt'
            #print(readPath)
            if os.access(readPath, os.F_OK):
                with open(readPath, 'r', encoding='utf-8') as file:
                    strs = file.readline()
                    #print(strs)
                    skinList[i][3] = strs
        #print(skinList)
        
    def table_dataRefresh(self):
        #idx = 0
        global skinList
        iLen = len(skinList)
        self.tableWidgetMain.setRowCount(iLen)
        for i in range(iLen):
            str = 'X'
            if skinList[i][1] == 1:
                str = '적용'
            self.tableWidgetMain.setItem(i, 0, QTableWidgetItem(str))
            self.tableWidgetMain.setItem(i, 1, QTableWidgetItem(skinList[i][2]))
            self.tableWidgetMain.setItem(i, 2, QTableWidgetItem(skinList[i][3]))
            
    def table_data_sorting(self):
        #데이터들을 ini기준으로 정렬한다. 맨위부터 하나씩 찾아서 위로 올려주는식으로한다
        global skinList
        topidx = 0 #맨위 인덱스
        #iniidx = 0 #ini상 인덱스
        #listidx = 0 #현재 list에서 읽고있는 인덱스
        #print('sorting test')
        
        foridx = 0
        
        #전체 for문 돌린다
        for ni in range(0,100):
            orderStr = '%d' % (ni)
# =============================================================================
#             try:
#                 strTitle = config['order'][orderStr]
#                 print(strTitle)
#             except:
#                 print("더이상 order데이터가 없음")
#                 return
# =============================================================================
            
            if config.has_option('order',orderStr):
                strTitle = config.get('order', orderStr)
                foridx = 0
                for listStr in skinList:
                    if strTitle in listStr:
                        #발견되면 발견된얘부터 순차적으로 위로올려준다
                        skinList[foridx][1] = int(config.get('flag', orderStr))
                        skinList[topidx], skinList[foridx] = skinList[foridx], skinList[topidx]
                        topidx = topidx + 1
                        break
                    else:
                        foridx = foridx + 1
                        #print('있음', strTitle)
            else:
                return
            

        
        
        
        
    def btn_table_row_up(self): #올리는것이므로 idx는 내려간다
        global skinList
        #iLen = len(skinList)
        row = self.tableWidgetMain.currentRow()
        if row >= 1:
            skinList[row - 1], skinList[row] = skinList[row], skinList[row - 1]
            self.tableWidgetMain.setCurrentCell(row-1, 0)
        self.table_dataRefresh()
        
        
        
    def btn_table_row_down(self): #리스트에서 내리는것이므로 idx는 올라간다
        global skinList
        iLen = len(skinList)
        row = self.tableWidgetMain.currentRow()
        if row <= iLen - 2 and row >= 0:
            skinList[row + 1], skinList[row] = skinList[row], skinList[row + 1]
            self.tableWidgetMain.setCurrentCell(row+1, 0)
        self.table_dataRefresh()
        
    def btn_configSave(self):
        self.config_save()
        #reply = QMessageBox.question(self, 'Message', "설정을 저장했습니다", QMessageBox.Yes , QMessageBox.Yes)
        QMessageBox.question(self, 'Message', "설정을 저장했습니다", QMessageBox.Yes , QMessageBox.Yes)
        
        
    def config_save(self):
        with open(path_config, 'w', encoding='utf-8') as configfile:
            config['global'] = {}
            config['global']['d2rPath'] = d2rPath
            config['global']['modeName'] = self.lineEditCustomName.text()
            config['global']['sound-rune'] = self.lineEditSoundPath.text()
            config['global']['font'] = self.lineEditFontPath.text()
            
            config['checkbox'] = {}
            config['checkbox']['sound-rune'] = str(self.checkBox98.isChecked())
            config['checkbox']['font'] = str(self.checkBox99.isChecked())
            
            config['order'] = {}
            config['flag'] = {}
            for i in range(len(skinList)):
                orderStr='%d' % (i)
                config['order'][orderStr] = skinList[i][2]
                flag='%d' % (skinList[i][1])
                config['flag'][orderStr] = flag
                
                
            
            config.write(configfile)
        
    def config_load(self):
        if os.access(path_config, os.F_OK):
            config.read(path_config, encoding='utf-8')
            return True
        else:
            return False
        
    def debug(self, str):
        self.listWidgetDebug.addItem(str)
        self.listWidgetDebug.scrollToBottom()
        
        
    def btn_reload(self):    
        self.files_load()
        self.table_data_sorting()  #소팅한다
        self.table_dataRefresh()   #데이터를 재배치하고
        
    def btnSelectFolder(self):
        global d2rPath
        fPath = QFileDialog.getExistingDirectory(self, caption='Open Directory', directory=d2rPath)
        
        
        if len(fPath) > 1:
            print(fPath)
            d2rPath = fPath
            self.lineEditD2RPath.setText(d2rPath)
    
    def btnSelectFile(self, str1):
        fPath = QFileDialog.getOpenFileName(self, caption='Open Directory', directory=str1)
        return fPath

    def btn_selectRuneSound(self):
        defaultPath = self.lineEditSoundPath.text()
        fPath = self.btnSelectFile(defaultPath)
        try:
            readPath = str(fPath[0])
            print(readPath)
            if os.access(readPath, os.F_OK):
                self.lineEditSoundPath.setText(readPath)
        except:
            print()
    def btn_selectFont(self):
        defaultPath = self.lineEditFontPath.text()
        fPath = self.btnSelectFile(defaultPath)
        try:
            readPath = str(fPath[0])
            print(readPath)
            if os.access(readPath, os.F_OK):
                self.lineEditFontPath.setText(readPath)
        except:
            print()

    def btn_selectLoadZip(self): #zip파일 처리
        fPath = self.btnSelectFile('./') #파일 선택
        try:
            readPath = str(fPath[0])
            print(readPath)
            if os.access(readPath, os.F_OK): #선택한 파일이 access가 가능하면...
                
                #zip파일을 일단 해체한다
                head, tail = os.path.splitext(readPath)
                head = os.path.basename(readPath)
                orgZipFileName = head
                head = head[:-len(tail)]
                
                
                #head=파일명, tail=확장자
                m_modal = InputSkinDialog()
                m_modal.setInputName(head)
                m_modal.exec_()
                
                if len(m_modal.inputStr) < 2:
                    QMessageBox.question(self, 'Message', "이름을 입력하지 않아 불러오지 않았습니다", QMessageBox.Yes , QMessageBox.Yes)
                    return
                skinName = str(m_modal.inputStr).strip()
                skinName = skinName.strip()
                #self.lineEditFontPath.setText(readPath)
                #우선 zip파일을 해체합니다
                #print(tail)
                
                createSkinPath = '.\\files\\' + skinName
                if os.path.isdir(createSkinPath) == True:
                    QMessageBox.question(self, 'Message', "입력한 명칭이 이미 존재합니다. 만들 수 없습니다.", QMessageBox.Yes , QMessageBox.Yes)
                    return
                tail = tail.lower() #혹시 확장자 문제생길지모르니 소문자처리
                
                zipFlag= False
                
                if tail == '.zip':
                    zipFlag = True
                    
                    newPath = '.\\temp\\zipExtract\\'
                    #일단 해당경로는 지운다
                    if os.path.exists(newPath):
                        shutil.rmtree(newPath)
                        
                    #print(newPath)
                    Path(newPath).mkdir(parents=True,exist_ok=True)
                    
                    myZip = zipfile.ZipFile(readPath)
                    myZip.extractall(newPath)
                    
                    #폴더내용을 검색한다, 우선 폴더내용을 알아냄
                    self.clearPathList()
                    self.checkDir(newPath)
                    
                    
                    inZipPath = ""
                    
                    #zip파일내 경로를 감지한다
                    fCheckFlag = True
                    while True:
                        self.clearPathList()
                        self.search(newPath)
                        #mpq경로가 있는지 감지해본다
                        #print(folderPathList)
                        for strs in folderPathList:
                            print(strs)
                            if "mpq" in strs:
                                #print("mpq=", strs)
                                inZipPath = strs+"\\data"
                                fCheckFlag = False
                                break
                        if fCheckFlag == False: #mpq검사에서 찾으면 패스
                            break
                        
                        self.clearPathList()
                        self.checkDir(newPath)
                        #바로 앞 경로가 아무것도아니라면
                        for strs in folderPathList:
                            #print(strs)
                            head = os.path.basename(strs)
                            if 'data' != head and 'hd' != head and 'global' != head and 'local' != head:
                                print('아무런 패턴도 발견하지못함. 한번 더 들어감')
                                self.clearPathList()
                                self.checkDir(strs)
                        
                        for strs in folderPathList:
                            head = os.path.basename(strs)
                            if head == 'data':
                                print('data글자를 찾았습니다. 다시한번 찾습니다')
                                self.clearPathList()
                                self.checkDir(strs)
                        
                        #바로 앞 경로에 hd,global,local중 하나라도 걸리면 hit!
                        for strs in folderPathList:
                            head = os.path.basename(strs)
                            if 'hd' == head or 'global' == head or 'local' == head:
                                print('hd,global,local=', strs)
                                inZipPath = strs[:-(len(head)+1)]
                                fCheckFlag = False
                                break
                        
                        
                        
                        
                        if fCheckFlag == False: #Yes!
                            break
                        
                        break#잊지말고 while마지막 정지
                        
                    #if fCheckFlag == True:
                    #    QMessageBox.question(self, 'Message', "해당 zip 파일을 인식할 수 없습니다. 제작자에게 문의해주세요 (ㅠㅠ)", QMessageBox.Yes , QMessageBox.Yes)
                    #    return
                    
                
                
                if zipFlag == True and len(inZipPath) > 2:
                    
                    
                    print("입력한 스킨명 경로:", skinName, "len:", str(len(skinName)))
                    print("찾아낸 경로:", inZipPath)
                    print("만들어낼 스킨경로:", createSkinPath)
                    
                    Path(createSkinPath).mkdir(parents=True,exist_ok=True)
                    self.copyTree_s(inZipPath, createSkinPath)
                    strs = '%s 파일으로부터 %s 스킨 을 만들었습니다.' % (orgZipFileName, skinName)
                    self.debug(strs)
                    QMessageBox.question(self, 'Message', strs, QMessageBox.Yes , QMessageBox.Yes)
                    #전체파일을 다시 로딩해준다
                    self.files_load()
                    self.table_data_sorting()  #소팅한다
                    self.table_dataRefresh()   #데이터를 재배치하고
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                elif zipFlag == True: #모두에도 해당하지않는다면 DB에서 조회하여 자동으로 만든다
                    print('임의로 생성중')    
                    #일단 내용물을 모두 조회한다. 파일명을 모두알아내야함
                    newPath = '.\\temp\\zipExtract\\'
                    self.clearPathList()
                    self.search(newPath)
                    #파일명가지고 전부다 알아낸다
                    for strs in filePathList:
                        print(strs)
                    
                    
                    for strs in filePathList:
                        #파일이름 가져와서
                        
                        onlyFileName = strs[len(newPath):].lower()
                        #print("파일명칭 : " +onlyFileName)
                        
                        #db에서 조회해서
                        #해당 폴더를 만들고, 카피한다
                        
                        query = 'select path from filePath where fileName = "' + onlyFileName+ '" limit 1'
                        #print(query)
                        cur.execute(query)
                        rows = False
                        rows = cur.fetchone()
                        
                        if rows:
                            makePath = createSkinPath + rows[0]
                            #print('만든폴더:' + makePath)
                            Path(makePath).mkdir(parents=True,exist_ok=True)
                            
                            fileNewPath = os.path.join(makePath, onlyFileName) 
                            
                            #print(strs)
                            #print(fileNewPath)
                            #strs=zip압축푼 경로 
                            shutil.copy2(strs, fileNewPath)
                            strInput = "자동으로 찾은 경로 : " + rows[0] + "\\" + onlyFileName
                            self.debug(strInput)
                            
                        #print('for문돌았음')
                    #print('끝?')            
                    self.files_load()
                    self.table_data_sorting()  #소팅한다
                    self.table_dataRefresh()   #데이터를 재배치하고
                    strs = '%s 파일으로부터 %s 스킨 을 만들었습니다.' % (orgZipFileName, skinName)
                    self.debug(strs)
                    QMessageBox.question(self, 'Message', '[경로 데이터가 존재하지 않아, 자동으로 인식하여 스킨을 생성하였습니다]\n경로가 설정되어있지 않는 zip파일 이여서, 자동으로 db와 비교하여 스킨을 생성하였습니다.\n경로가 잘못되었을 수 있으니 적용 전 files 폴더에서 꼭 확인해주세요', QMessageBox.Yes , QMessageBox.Yes)
                
                    
                    
# =============================================================================
#                             print("path:" + strs)
#                             #print(strs)
#                             head = os.path.basename(strs)
#                             #print("감지된 경로 : " + strs)
#                             print("basename:" + head)
# =============================================================================
                        
                    
                    
        except:
            print()
    
    def clearPathList(self):
        while len(folderPathList) > 0 : folderPathList.pop()
        while len(filePathList) > 0 : filePathList.pop()

    
    def checkDir(self, dir):
        files = os.listdir(dir)
        for file in files:
            fullFilename = os.path.join(dir, file)
            if os.path.isdir(fullFilename):
                folderPathList.append(fullFilename)
                        
    def search(self, dir):
        files = os.listdir(dir)
        for file in files:
            fullFilename = os.path.join(dir, file)
            if os.path.isdir(fullFilename):
                folderPathList.append(fullFilename)
                self.search(fullFilename)
            else:
                filePathList.append(fullFilename)
                pass
            
    def copyTree_s(self, orgDir, desDir):
        findPath = orgDir
        newPath = desDir
        
        self.clearPathList() #리스트를 초기화합니다
        self.search(findPath) #전체리스트검색
        for strs in folderPathList: #폴더먼저 생성
            resultStr = strs[len(findPath):]
            foldercreatePath = newPath + resultStr
            Path(foldercreatePath).mkdir(parents=True,exist_ok=True)
        for strs in filePathList: #파일 카피
            resultStr = strs[len(findPath):]
            FilenewPath = newPath + resultStr
            shutil.copy2(strs, FilenewPath)
        
        
    def btnCreate(self):
        d2rPath = self.lineEditD2RPath.text()
        if "Diablo" not in d2rPath:
            reply = QMessageBox.question(self, 'Message', '[경고] 현재 설정된 경로에 diablo 글자가 없어요!\n%s\n경로가 디아블로2 레저렉션이 설치된 폴더가 맞습니까?' % (d2rPath), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                pass
            else:
                reply = QMessageBox.question(self, 'Message', "설치를 취소했습니다", QMessageBox.Yes , QMessageBox.Yes)
                return
            
        
        #distutils.dir_util._path_created.clear()
        self.debug("----- 설치 초기화중입니다 -----")
        #print("버튼이 눌렸습니다")
        modName = self.lineEditCustomName.text()
        newPath = d2rPath + "\\mods\\" + modName + "\\"
        
        try:
            if os.path.exists(newPath):
                reply = QMessageBox.question(self, 'Message', '이미 %s 모드가 설치되어있습니다. %s 모드 폴더를 삭제후 설치할까요?' % (modName, modName), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    shutil.rmtree(newPath)
                else:
                    print("그외누름")
            if not os.path.exists(newPath):
                os.makedirs(newPath)
                #Path(newPath).mkdir(exist_ok=True)
        except OSError:
            self.listWidgetDebug.addItem("mods 폴더를 생성할 수 없습니다. (권한등 점검)")
            return
        
        self.listWidgetDebug.addItem("mods/"+modName+" 폴더를 생성했습니다")
        
        newPath = newPath + modName + ".mpq\\data\\"
        #print(newPath)
        Path(newPath).mkdir(parents=True,exist_ok=True)
        #self.listWidgetDebug.addItem("기본 mod폴더 생성 완료")
        #self.listWidgetDebug.addItem(newPath)
        newPath2 = d2rPath + "\\mods\\" + modName + "\\" + modName + ".mpq\\modinfo.json"
        
        print(newPath2)
        
        print(path_modinfo)
        with open(path_modinfo, encoding="UTF-8-sig") as f_org:
            data1 = json.load(f_org)
            print(data1)
        data1["name"] = modName
        with open(newPath2, "w", encoding="UTF-8-sig") as f_export:
            json.dump(data1, f_export, indent=4)
        
        
        #이제 설정된 데이터를 돌면서 카피해줍니다
        for skinStr in skinList:
            if skinStr[1] == 1: # 1=사용 인경우에만 카피함
                orgPath = "./files/" + skinStr[2]
                if os.path.exists(orgPath):
                    
                    
                    
                    #findPath = orgPath
                    #while len(folderPathList) > 0 : folderPathList.pop()
                    #while len(filePathList) > 0 : filePathList.pop()
                    self.copyTree_s(orgPath, newPath)
                    
# =============================================================================
#                     self.clearPathList() #리스트를 초기화합니다
#                     self.search(findPath) #전체리스트검색
#                     for strs in folderPathList: #폴더먼저 생성
#                         resultStr = strs[len(findPath):]
#                         foldercreatePath = newPath + resultStr
#                         Path(foldercreatePath).mkdir(parents=True,exist_ok=True)
#                     for strs in filePathList: #파일 카피
#                         resultStr = strs[len(findPath):]
#                         FilenewPath = newPath + resultStr
#                         shutil.copy2(strs, FilenewPath)
# =============================================================================
                        
                    self.debug('[적용] %s' % (skinStr[2]))

                

# =============================================================================
#         orgPath = ""
#         if self.checkBox1.isChecked():
#             orgPath = "./files/01 stringpatch"
#             if os.path.exists(orgPath):
#                 distutils.dir_util.copy_tree(orgPath, newPath)
#                 #shutil.copytree(orgPath, newPath)
# =============================================================================
    
        if self.checkBox98.isChecked():
            orgPath = self.lineEditSoundPath.text()
            if os.path.exists(orgPath):
                #copy_tree(orgPath, newPath)
                soundPath = newPath + "hd/global/sfx/item/"
                Path(soundPath).mkdir(parents=True, exist_ok=True)
                shutil.copy2(orgPath, soundPath + "item_rune_hd.flac")
                self.debug('[적용] 룬 드랍 소리 %s' % (orgPath))
            else:
                self.debug('[실패] 룬 드랍 소리 : 파일이 없습니다')
                
        if self.checkBox99.isChecked():
            orgPath = self.lineEditFontPath.text()
            if os.path.exists(orgPath):
                #copy_tree(orgPath, newPath)
                fontPath = newPath + "hd/ui/fonts/"
                Path(fontPath).mkdir(parents=True, exist_ok=True)
                shutil.copy2(orgPath, fontPath + "kodia.ttf")
                self.debug('[적용] 폰트 %s' % (orgPath))
            else:
                self.debug('[실패] 폰트 : 파일이 없습니다')

            
        #모두완료하였으니 readme.txt를 지우도록한다
        removePath = newPath + 'readme.txt'
        if os.access(removePath, os.F_OK):
            os.remove(removePath)
        self.debug("설정된 파일을 복사 완료하였습니다!")
        self.debug("배틀넷 앱 명령줄 인자에 반드시 아래 내용을 입력하셨는지 확인 후 실행해주세요")
        self.debug(" -mod " + modName +" -txt")
        #self.listWidgetDebug.scrollToBottom()
        reply = QMessageBox.question(self, 'Message', "적용 완료!\n설정도 저장했습니다!", QMessageBox.Yes , QMessageBox.Yes)
        self.config_save()
    
    def __init__(self):
        global skinList
        global d2rPath
        
        QtWidgets.QMainWindow.__init__(self)
        
        
        super().__init__()
        self.setupUi(self)
        
        #초기값 읽어오기
        self.getReg() #레지스트리 읽어옴
        if self.config_load() == False:
            self.config_save()
            
        #config에 이미 diablo경로가있다면 불러옴
        #d2rPath    
        if config.has_option('global','d2rPath'):
            tempStr = config.get('global','d2rPath')
            if len(tempStr) > 1:
                d2rPath = tempStr
                print('path입력완료')
            else:
                print('너무짧음 이상함')
        else:
            print('저장되어있는 d2rPath 데이터가없음')
        self.lineEditD2RPath.setText(d2rPath)
        tempStr = "D2R Path : %s" % (d2rPath)
        
        self.listWidgetDebug.addItem(tempStr)
        self.lineEditCustomName.setText("seonheeCustom")
        
        #sound
        readPath = "./misc/sample_diablo3_legendary.flac"
        if os.access(readPath, os.F_OK):
            self.lineEditSoundPath.setText(readPath)
             
        
        self.pushButtonCreate.clicked.connect(self.btnCreate)
        self.pushButtonConfigSave.clicked.connect(self.btn_configSave)
        self.pushButtonPathSelect.clicked.connect(self.btnSelectFolder)
        self.pushButtonListUp.clicked.connect(self.btn_table_row_up)
        self.pushButtonListDown.clicked.connect(self.btn_table_row_down)
        self.pushButtonPathSelect_2.clicked.connect(self.btn_selectRuneSound)
        self.pushButtonPathSelect_3.clicked.connect(self.btn_selectFont)
        self.pushButtonLoadzip.clicked.connect(self.btn_selectLoadZip)
        self.pushButtonReload.clicked.connect(self.btn_reload)
        
        
        #config 처리
        
        #config로 읽어온 데이터가 있다면 써준다
        #if len(config.values['global']['modeName']) > 0:
        #self.lineEditCustomName.setText()
        if config.has_option('global','modeName'):
            self.lineEditCustomName.setText(config.get('global','modeName'))
        if config.has_option('global','sound-rune'):
            self.lineEditSoundPath.setText(config.get('global','sound-rune'))
        if config.has_option('global','font'):
            self.lineEditFontPath.setText(config.get('global','font'))
        if config.has_option('checkbox','sound-rune'):
            if config.get('checkbox','sound-rune') == 'True':
                Flag = True
            else:
                Flag = False
                self.checkBox98.setChecked(Flag)
        if config.has_option('checkbox','font'):
            if config.get('checkbox','font') == 'True':
                Flag = True
            else:
                Flag = False
                self.checkBox99.setChecked(Flag)
                
            
        

        
        #줄
        self.tableWidgetMain.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidgetMain.verticalHeader().setVisible(False) 
        #self.tableWidgetMain.horizontalHeader().setVisible(False) 
        self.tableWidgetMain.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetMain.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.tableWidgetMain.setColumnCount(3)
        #스킨갯수만큼
        
        self.tableWidgetMain.setColumnWidth(0,40)
        self.tableWidgetMain.setColumnWidth(1,280)
        self.tableWidgetMain.setColumnWidth(2,440)
        self.tableWidgetMain.setHorizontalHeaderLabels(["Seon","스킨명","설명"])
        self.tableWidgetMain.cellClicked.connect(self.table_cell_clicked)
        
        ###
        self.tableWidgetMain.setContextMenuPolicy(Qt.ActionsContextMenu)

        table_action_modify1 = QAction("이름 수정하기", self.tableWidgetMain)
        table_action_modify2 = QAction("설명 수정하기", self.tableWidgetMain)
        table_action_skinDelete = QAction("이 스킨을 삭제하기", self.tableWidgetMain)

        self.tableWidgetMain.addAction(table_action_modify1)
        self.tableWidgetMain.addAction(table_action_modify2)
        self.tableWidgetMain.addAction(table_action_skinDelete)
        

        table_action_modify1.triggered.connect(self._table_action_modify1)
        table_action_modify2.triggered.connect(self._table_action_modify2)
        table_action_skinDelete.triggered.connect(self._table_action_skinDelete)
        ###

        self.files_load()
        self.table_data_sorting()  #소팅한다
        self.table_dataRefresh()   #데이터를 재배치하고
        
    def _table_action_modify1(self):
        row = self.tableWidgetMain.currentRow()
        OrgSkinName = skinList[row][2]
        text, ok = QInputDialog.getText(self, '입력 창', '변경할 명칭을 입력해주세요:', text=OrgSkinName)
        text = text.strip()
        if ok: #ok가 눌렸다면
            if OrgSkinName != text and len(text) > 1: #글자가있는경우에만
                #path 검사해야합니다
                oldPath = '.\\files\\' + OrgSkinName
                newPath = '.\\files\\' + text
                if os.path.exists(newPath):
                     QMessageBox.question(self, 'Message', "이미 존재하는 스킨 명칭입니다. 변경할 수 없어요!", QMessageBox.Yes , QMessageBox.Yes)
                else:
                    if os.path.exists(oldPath):
                        skinList[row][2] = text
                        os.rename(oldPath, newPath)
                        #print('변경완료')
                        self.config_save()
                        self.table_dataRefresh()   #데이터를 재배치
                
        
            

    def _table_action_modify2(self):
        row = self.tableWidgetMain.currentRow()
        OrgSkindescrip = skinList[row][3]
        text, ok = QInputDialog.getText(self, '입력 창', '변경할 설명을 입력해주세요:', text=OrgSkindescrip)
        text = text.strip()
        if ok: #ok가 눌렸다면
            if OrgSkindescrip != text and len(text) > 1: #글자가있는경우에만
                #path 검사해야합니다
                newPath = '.\\files\\' + skinList[row][2]
                if os.path.exists(newPath):
                    with open('%s\\readme.txt' % (newPath), 'w', encoding='UTF-8') as f:
                        f.writelines(text)
                    skinList[row][3] = text
                    
                    self.config_save()
                    self.table_dataRefresh()   #데이터를 재배치
                    #QMessageBox.question(self, 'Message', "이미 존재하는 스킨 명칭입니다. 변경할 수 없어요!", QMessageBox.Yes , QMessageBox.Yes)




    def _table_action_skinDelete(self):
        #정말 지우시겠습니까? ~
        row = self.tableWidgetMain.currentRow()
        deleteSkinName= skinList[row][2]
        strs = '[%s] 이 스킨을 정말로 지우시겠습니까?' % (deleteSkinName)
        reply = QMessageBox.question(self, 'Message', strs, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            deletePath = '.\\files\\' + deleteSkinName
            if os.path.exists(deletePath):
                shutil.rmtree(deletePath)
                #그냥 다시불러오면됨
                self.files_load()
                self.table_data_sorting()  #소팅한다
                self.table_dataRefresh()   #데이터를 재배치하고
                QMessageBox.question(self, 'Message', "[%s] 삭제했습니다" % (deleteSkinName) , QMessageBox.Yes , QMessageBox.Yes)
                
    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', '변경할 스킨명을 작성해주세요:')
        
            
            
            
            

        
class InputSkinDialog(QDialog, Ui_InputSkin):
    def __init__(self):
        QDialog.__init__(self)
        Ui_InputSkin.__init__(self)
        self.setupUi(self)
        self.pushButtonOK.clicked.connect(self.pressok)
        self.pushButtonCANCEL.clicked.connect(self.reject)
        self.inputStr = ""
        #print('subdialog 불러옴')
        
    def setInputName(self, str):
        self.lineEditSkinName.setText(str)
        
        
    def Close(self):
        self.close()
    
    
    def pressok(self):
        self.inputStr = self.lineEditSkinName.text()
        self.close()
        
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    #dialog_inputSkin = InputSkin()
    
    app.exec_()












