import os, sys, config, webbrowser
from PySide2.QtCore import QUrl, Qt, QEvent
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import (QAction, QGridLayout, QLineEdit, QMainWindow, QPushButton, QToolBar, QWidget)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from TextCommandParser import TextCommandParser
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.textCommandParser = TextCommandParser(self)

        self.setWindowTitle('Unique Bible App')
        
        appIconFile = os.path.join("htmlResources", "theText.png")
        appIcon = QIcon(appIconFile)
        QGuiApplication.setWindowIcon(appIcon)
        
        self.create_menu()
        self.setupToolBar()
        self.setupSecondToolBar()
        self.setupBaseUrl()
        
        self.centralWidget = CentralWidget(self)
        self.mainView = self.centralWidget.mainView
        self.mainPage = self.mainView.page()
        self.mainPage.titleChanged.connect(self.mainTextCommandChanged)
        self.mainPage.loadFinished.connect(self.finishMainViewLoading)
        self.studyView = self.centralWidget.studyView
        self.studyPage = self.studyView.page()
        self.studyPage.titleChanged.connect(self.studyTextCommandChanged)
        self.studyPage.loadFinished.connect(self.finishStudyViewLoading)
        self.instantView = self.centralWidget.instantView
        self.instantPage = self.instantView.page()
        self.instantPage.titleChanged.connect(self.instantTextCommandChanged)
        self.setCentralWidget(self.centralWidget)

    def __del__(self):
        del self.textCommandParser

    def event(self, event):
        if event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Tab:
            self.textCommandLineEdit.setFocus()
            return True
        return QWidget.event(self, event)

    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser("YES")
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    def create_menu(self):
        
        menu1 = self.menuBar().addMenu("&UniqueBible.app")
        appIcon = QIcon(os.path.join("htmlResources", "theText.png"))
        quit_action = QAction(appIcon, "E&xit", self, shortcut = "Ctrl+Q", triggered=qApp.quit)
        menu1.addAction(quit_action)
        
        menu2 = self.menuBar().addMenu("&View")
        menu2.addAction(QAction("&Full Screen", self, shortcut = "Ctrl+F", triggered=self.fullsizeWindow))
        menu2.addAction(QAction("&Resize", self, shortcut = "Ctrl+R", triggered=self.twoThirdWindow))
        menu2.addSeparator()
        menu2.addAction(QAction("&Top Half", self, shortcut = "Ctrl+T", triggered=self.halfScreenHeight))
        menu2.addAction(QAction("&Left Half", self, shortcut = "Ctrl+L", triggered=self.halfScreenWidth))

        menu3 = self.menuBar().addMenu("&Layout")
        menu3.addAction(QAction("&Main Toolbar [Hide / Show]", self, shortcut = "Ctrl+M", triggered=self.hideShowToolBar))
        menu3.addAction(QAction("Seco&nd Toolbar [Hide / Show]", self, shortcut = "Ctrl+N", triggered=self.hideShowSecondToolBar))
        menu3.addSeparator()
        menu3.addAction(QAction("&Study Window [Hide / Resize]", self, shortcut = "Ctrl+P", triggered=self.parallel))
        menu3.addAction(QAction("L&ightning Window [Hide / Show]", self, shortcut = "Ctrl+I", triggered=self.instant))
        menu3.addSeparator()
        menu3.addAction(QAction("&Larger Font", self, shortcut = "Ctrl++", triggered=self.largerFont))
        menu3.addAction(QAction("&Smaller Font", self, shortcut = "Ctrl+-", triggered=self.smallerFont))

        menu4 = self.menuBar().addMenu("&Quick Access")
        menu4.addAction(QAction("&Enabled Lightning", self, shortcut = "Ctrl+1", triggered=self.enableLightning))
        menu4.addAction(QAction("&Disabled Lightning", self, shortcut = "Ctrl+0", triggered=self.disableLightning))
        menu4.addSeparator()
        menu4.addAction(QAction("&Paste from Clipboard", self, shortcut = "Ctrl+*", triggered=self.pasteFromClipboard))

        menu5 = self.menuBar().addMenu("&History")
        menu5.addAction(QAction("&Main", self, shortcut = "Ctrl+;", triggered=self.mainHistoryButtonClicked))
        menu5.addAction(QAction("&Back", self, shortcut = "Ctrl+[", triggered=self.back))
        menu5.addAction(QAction("&Forward", self, shortcut = "Ctrl+]", triggered=self.forward))
        menu5.addSeparator()
        menu5.addAction(QAction("&Study", self, shortcut = "Ctrl+'", triggered=self.studyHistoryButtonClicked))
        menu5.addAction(QAction("&Back", self, shortcut = "Ctrl+{", triggered=self.studyBack))
        menu5.addAction(QAction("&Forward", self, shortcut = "Ctrl+}", triggered=self.studyForward))

        menu6 = self.menuBar().addMenu("&About")
        menu6.addAction(QAction("&BibleTools.app", self, triggered=self.openBibleTools))
        menu6.addAction(QAction("&UniqueBible.app", self, triggered=self.openUniqueBible))
        menu6.addAction(QAction("&Marvel.bible", self, triggered=self.openMarvelBible))
        menu6.addAction(QAction("&BibleBento.com", self, triggered=self.openBibleBento))
        menu6.addAction(QAction("&OpenGNT.com", self, triggered=self.openOpenGNT))
        menu6.addSeparator()
        menu6.addAction(QAction("&GitHub Repositories", self, triggered=self.openSource))
        menu6.addAction(QAction("&Unique Bible", self, triggered=self.openUniqueBibleSource))
        menu6.addAction(QAction("&Open Hebrew Bible", self, triggered=self.openHebrewBibleSource))
        menu6.addAction(QAction("&Open Greek New Testament", self, triggered=self.openOpenGNTSource))
        menu6.addSeparator()
        menu6.addAction(QAction("&Credits", self, triggered=self.openCredits))
        menu6.addSeparator()
        menu6.addAction(QAction("&Contact Eliran Wong", self, triggered=self.contactEliranWong))

    def setupToolBar(self):
        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle("Text Command")
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.toolBar)

        backButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "left.png")
        backButton.setIcon(QIcon(leftButtonFile))
        backButton.clicked.connect(self.back)
        self.toolBar.addWidget(backButton)

        forwardButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "right.png")
        forwardButton.setIcon(QIcon(rightButtonFile))
        forwardButton.clicked.connect(self.forward)
        self.toolBar.addWidget(forwardButton)

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        self.toolBar.addWidget(self.textCommandLineEdit)

        studyBackButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "left.png")
        studyBackButton.setIcon(QIcon(leftButtonFile))
        studyBackButton.clicked.connect(self.studyBack)
        self.toolBar.addWidget(studyBackButton)

        studyForwardButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "right.png")
        studyForwardButton.setIcon(QIcon(rightButtonFile))
        studyForwardButton.clicked.connect(self.studyForward)
        self.toolBar.addWidget(studyForwardButton)

        # put the secondary toolbar below the main one
        self.addToolBarBreak()

    def setupSecondToolBar(self):
        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790; }"
        
        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle("Special Features")
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        mainHistoryButton = QPushButton()
        mainHistoryButtonFile = os.path.join("htmlResources", "history.png")
        mainHistoryButton.setIcon(QIcon(mainHistoryButtonFile))
        mainHistoryButton.clicked.connect(self.mainHistoryButtonClicked)
        self.secondToolBar.addWidget(mainHistoryButton)

        searchBibleButton = QPushButton()
        searchBibleButtonFile = os.path.join("htmlResources", "search.png")
        searchBibleButton.setIcon(QIcon(searchBibleButtonFile))
        searchBibleButton.clicked.connect(self.displaySearchBibleCommand)
        self.secondToolBar.addWidget(searchBibleButton)

        self.mainRefButton = QPushButton(self.verseReference("main"))
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.secondToolBar.addWidget(self.mainRefButton)

        self.secondToolBar.addSeparator()

        self.parallelMode = 1 # default parallel mode
        parallelButton = QPushButton()
        parallelButtonFile = os.path.join("htmlResources", "parallel.png")
        parallelButton.setIcon(QIcon(parallelButtonFile))
        parallelButton.clicked.connect(self.parallel)
        self.secondToolBar.addWidget(parallelButton)

        studyHistoryButton = QPushButton()
        studyHistoryButtonFile = os.path.join("htmlResources", "history.png")
        studyHistoryButton.setIcon(QIcon(studyHistoryButtonFile))
        studyHistoryButton.clicked.connect(self.studyHistoryButtonClicked)
        self.secondToolBar.addWidget(studyHistoryButton)

        self.studyRefButton = QPushButton(self.verseReference("study"))
        self.studyRefButton.setStyleSheet(textButtonStyle)
        self.studyRefButton.clicked.connect(self.studyRefButtonClicked)
        self.secondToolBar.addWidget(self.studyRefButton)

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        self.secondToolBar.addSeparator()

        searchBookButton = QPushButton()
        searchBookButtonFile = os.path.join("htmlResources", "search.png")
        searchBookButton.setIcon(QIcon(searchBookButtonFile))
        searchBookButton.clicked.connect(self.displaySearchBookCommand)
        self.secondToolBar.addWidget(searchBookButton)

        self.bookButton = QPushButton(config.book)
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        self.secondToolBar.addSeparator()

        self.instantMode = 1 # default parallel mode
        instantButton = QPushButton()
        instantButtonFile = os.path.join("htmlResources", "lightning.png")
        instantButton.setIcon(QIcon(instantButtonFile))
        instantButton.clicked.connect(self.instant)
        self.secondToolBar.addWidget(instantButton)

        self.enableInstantButton = QPushButton(self.getInstantInformation())
        self.enableInstantButton.setStyleSheet(textButtonStyle)
        self.enableInstantButton.clicked.connect(self.enableInstantButtonClicked)
        self.secondToolBar.addWidget(self.enableInstantButton)

        self.secondToolBar.addSeparator()

        fontMinusButton = QPushButton()
        fontMinusButtonFile = os.path.join("htmlResources", "fontMinus.png")
        fontMinusButton.setIcon(QIcon(fontMinusButtonFile))
        fontMinusButton.clicked.connect(self.smallerFont)
        self.secondToolBar.addWidget(fontMinusButton)

        fontPlusButton = QPushButton()
        fontPlusButtonFile = os.path.join("htmlResources", "fontPlus.png")
        fontPlusButton.setIcon(QIcon(fontPlusButtonFile))
        fontPlusButton.clicked.connect(self.largerFont)
        self.secondToolBar.addWidget(fontPlusButton)

        self.secondToolBar.addSeparator()

    # Actions - hide / show tool bars
    def hideShowToolBar(self):
        if self.toolBar.isVisible():
            self.toolBar.hide()
        else:
            self.toolBar.show()

    def hideShowSecondToolBar(self):
        if self.secondToolBar.isVisible():
            self.secondToolBar.hide()
        else:
            self.secondToolBar.show()

    # Actions - open urls
    def openBibleTools(self):
        webbrowser.open("https://bibletools.app")

    def openUniqueBible(self):
        webbrowser.open("https://uniquebible.app")

    def openMarvelBible(self):
        webbrowser.open("https://marvel.bible")

    def openBibleBento(self):
        webbrowser.open("https://biblebento.com")
        
    def openOpenGNT(self):
        webbrowser.open("https://opengnt.com")

    def openSource(self):
        webbrowser.open("https://github.com/eliranwong/")

    def openUniqueBibleSource(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible")

    def openHebrewBibleSource(self):
        webbrowser.open("https://github.com/eliranwong/OpenHebrewBible")

    def openOpenGNTSource(self):
        webbrowser.open("https://github.com/eliranwong/OpenGNT")

    def openCredits(self):
        webbrowser.open("https://marvel.bible/resource.php")

    def contactEliranWong(self):
        webbrowser.open("https://marvel.bible/contact/contactform.php")

    # Actions - resize the main window
    def fullsizeWindow(self):
        self.resizeWindow(1, 1)

    def twoThirdWindow(self):
        self.resizeWindow(2/3, 2/3)

    def halfScreenHeight(self):
        self.resizeWindow(1, 1/2)

    def halfScreenWidth(self):
        self.resizeWindow(1/2, 1)

    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    # Actions - hide / show / resize study & lightning views
    def instant(self):
        if self.instantMode == 0:
            self.instantMode = 1
            self.instantView.show()
            self.centralWidget.layout.setRowStretch(0, 10)
            self.centralWidget.layout.setRowStretch(1, 2)
        elif self.instantMode == 1:
            self.instantMode = 0
            self.centralWidget.layout.setRowStretch(0, 10)
            self.centralWidget.layout.setRowStretch(1, 0)
            self.instantView.hide()

    def parallel(self):
        parallelRatio = {
            0: (1, 0),
            1: (2, 1),
            2: (1, 1),
            3: (1, 2),
        }
        if self.parallelMode == 3:
            self.parallelMode = 0
            self.studyView.hide()
        else:
            self.parallelMode += 1
            self.studyView.show()
        ratio = parallelRatio[self.parallelMode]
        self.centralWidget.layout.setColumnStretch(0, ratio[0])
        self.centralWidget.layout.setColumnStretch(1, ratio[1])

    # Action - paste text from clipboard into study view
    def pasteFromClipboard(self):
        clipboardText = qApp.clipboard().text()
        # note: use qApp.clipboard().setText to set text in clipboard
        html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script><script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {0}%;'><span id='v0.0.0'></span>{1}</body></html>".format(config.fontSize, clipboardText)
        self.studyView.setHtml(html, baseUrl)

    # Actions - enable or disable lightning feature
    def enableLightning(self):
        config.instantInformationEnabled = 1
        self.enableInstantButton.setText(self.getInstantInformation())

    def disableLightning(self):
        config.instantInformationEnabled = 0
        self.enableInstantButton.setText(self.getInstantInformation())

    def getInstantInformation(self):
        if config.instantInformationEnabled == 0:
            return "DISABLED"
        elif config.instantInformationEnabled == 1:
            return "ENABLED"

    def enableInstantButtonClicked(self):
        if config.instantInformationEnabled == 0:
            config.instantInformationEnabled = 1
        elif config.instantInformationEnabled == 1:
            config.instantInformationEnabled = 0
        self.enableInstantButton.setText(self.getInstantInformation())

    # Actions - book features
    def openBookMenu(self):
        self.runTextCommand("_book:::", False, "main")

    def displaySearchBookCommand(self):
        config.bookSearchString = ""
        self.textCommandLineEdit.setText("SEARCHBOOK:::{0}:::".format(config.book))

    # Actions - change font size
    def smallerFont(self):
        if not config.fontSize == 10:
            config.fontSize = config.fontSize - 5
            self.reloadCurrentRecord()

    def largerFont(self):
        config.fontSize = config.fontSize + 5
        self.reloadCurrentRecord()

    def reloadCurrentRecord(self):
        views = {
            "main": self.mainView,
            "study": self.studyView
        }
        for view in views.keys():
            textCommand = config.history[view][config.currentRecord[view]]
            self.runTextCommand(textCommand, False, view)

    # Action - search main view bible
    def displaySearchBibleCommand(self):
        self.textCommandLineEdit.setText("SEARCH:::{0}:::".format(config.mainText))

    # Actions - recently opened bibles & commentary
    def mainRefButtonClicked(self):
        newTextCommand = "_menu:::{0}.{1}.{2}.{3}".format(config.mainText, config.mainB, config.mainC, config.mainV)
        self.runTextCommand(newTextCommand, False, "main")

    def studyRefButtonClicked(self):
        newTextCommand = "_menu:::{0}.{1}.{2}.{3}".format(config.studyText, config.studyB, config.studyC, config.studyV)
        self.runTextCommand(newTextCommand, False, "study")

    def commentaryRefButtonClicked(self):
        newTextCommand = "_commentary:::{0}.{1}.{2}.{3}".format(config.commentaryText, config.commentaryB, config.commentaryC, config.commentaryV)
        self.runTextCommand(newTextCommand, False, "study")

    def updateMainRefButton(self):
        self.mainRefButton.setText(self.verseReference("main"))

    def updateStudyRefButton(self):
        self.studyRefButton.setText(self.verseReference("study"))

    def updateCommentaryRefButton(self):
        self.commentaryRefButton.setText(self.verseReference("commentary"))

    def verseReference(self, view):
        if view == "main":
            return "{0} - {1}".format(config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        elif view == "study":
            return "{0} - {1}".format(config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV))
        elif view == "commentary":
            return "{0} - {1}".format(config.commentaryText, self.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV))

    # Actions - access history records
    def mainHistoryButtonClicked(self):
        self.mainView.setHtml(self.getHistory("main"), baseUrl)

    def studyHistoryButtonClicked(self):
        self.studyView.setHtml(self.getHistory("study"), baseUrl)

    def getHistory(self, view):
        historyRecords = [(counter, record) for counter, record in enumerate(config.history[view])]
        html = "<br>".join(["<button class='feature' onclick='openHistoryRecord({0})'>{1}</button>".format(counter, record) for counter, record in reversed(historyRecords)])
        html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script><script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {0}%;'><span id='v0.0.0'></span>{1}</body></html>".format(config.fontSize, html)
        return html

    # navigation between history records
    def openHistoryRecord(self, view, recordNumber):
        config.currentRecord[view] = recordNumber
        textCommand = config.history[view][recordNumber]
        if view == "main":
            self.textCommandLineEdit.setText(textCommand)
        self.runTextCommand(textCommand, False, view)
    
    def back(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == 0:
            mainCurrentRecord = mainCurrentRecord - 1
            self.openHistoryRecord("main", mainCurrentRecord)

    def forward(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == (len(config.history["main"]) - 1):
            mainCurrentRecord = mainCurrentRecord + 1
            self.openHistoryRecord("main", mainCurrentRecord)

    def studyBack(self):
        if self.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == 0:
            studyCurrentRecord = studyCurrentRecord - 1
            self.openHistoryRecord("study", studyCurrentRecord)

    def studyForward(self):
        if self.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == (len(config.history["study"]) - 1):
            studyCurrentRecord = studyCurrentRecord + 1
            self.openHistoryRecord("study", studyCurrentRecord)

    # root folder for webViewEngine
    def setupBaseUrl(self):
        # baseUrl
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "theText.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)

    # finish view loading
    def finishMainViewLoading(self):
        # scroll to the main verse
        self.mainPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.mainB)+"."+str(config.mainC)+"."+str(config.mainV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    def finishStudyViewLoading(self):
        # scroll to the study verse
        self.studyPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    # change of unique bible commands
    def mainTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "main")

    def studyTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "study")

    def instantTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "instant")

    # change of text command detected via change of document.title
    def textCommandChanged(self, newTextCommand, source="main"):
        exceptionTuple = ("UniqueBible.app", "about:blank", "study.html")
        if not (newTextCommand.startswith("data:text/html;") or newTextCommand.startswith("file:///") or newTextCommand[-4:] == ".txt" or newTextCommand in exceptionTuple):
            if source == "main" and not newTextCommand.startswith("_"):
                self.textCommandLineEdit.setText(newTextCommand)
            if newTextCommand.startswith("_"):
                self.runTextCommand(newTextCommand, False, source)
            else:
                self.runTextCommand(newTextCommand, True, source)

    # change of text command detected via user input
    def textCommandEntered(self, source="main"):
        newTextCommand = self.textCommandLineEdit.text()
        self.runTextCommand(newTextCommand, True, source)

    def runTextCommand(self, textCommand, addRecord=True, source="main"):
        view, content = self.textCommandParser.parser(textCommand, source)
        if content == "INVALID_COMMAND_ENTERED":
            self.mainPage.runJavaScript("alert('Invalid command not processed.')")
        elif view == "":
            pass
        elif view == "command":
            self.textCommandLineEdit.setText(content)
        else:
            activeBCVsettings = ""
            if view == "main":
                activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
            elif view == "study":
                activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
            html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script>{0}<script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {1}%;'><span id='v0.0.0'></span>{2}</body></html>".format(activeBCVsettings, config.fontSize, content)
            views = {
                "main": self.mainView,
                "study": self.studyView,
                "instant": self.instantView,
            }
            if view == "study":
                # save html in a separate file
                # reason: setHTML does not work with content larger than 2 MB
                outputFile = os.path.join("htmlResources", "study.html")
                f = open(outputFile,'w')
                f.write(html)
                f.close()
                fullOutputPath = os.path.abspath(outputFile)
                self.studyView.load(QUrl.fromLocalFile(fullOutputPath))
                if self.parallelMode == 0:
                    self.parallel()
            elif view.startswith("popover"):
                view = view.split(".")[1]
                views[view].openPopover(html=html)
            else:
                views[view].setHtml(html, baseUrl)
            if addRecord == True and view in ("main", "study"):
                self.addHistoryRecord(view, textCommand)

    # add a history record
    def addHistoryRecord(self, view, textCommand):
        if not textCommand.startswith("_"):
            viewhistory = config.history[view]
            if not (viewhistory[-1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                historyRecordAllowed = config.historyRecordAllowed
                if len(viewhistory) > historyRecordAllowed:
                    viewhistory = viewhistory[-historyRecordAllowed:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1


class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QGridLayout()

        self.html = "<h1>UniqueBible.app</h1><p>UniqueBible.app</p>"
        self.mainView = WebEngineView(self, "main")
        self.mainView.setHtml(self.html, baseUrl)
        self.studyView = WebEngineView(self, "study")
        self.studyView.setHtml("Study View", baseUrl)
        self.instantView = WebEngineView(self, "instant")
        self.instantView.setHtml("Instant Information", baseUrl)

        self.layout.addWidget(self.mainView, 0, 0)
        self.layout.addWidget(self.studyView, 0, 1)
        self.layout.addWidget(self.instantView, 1, 0, 1, 2)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 1)

        self.layout.setRowStretch(0, 10)
        self.layout.setRowStretch(1, 2)

        self.setLayout(self.layout)


class WebEngineView(QWebEngineView):

    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.selectionChanged.connect(self.updateContextMenu)
        self.addMenuActions();

    def updateContextMenu(self):
        text = self.getText()
        parser = BibleVerseParser("YES")
        book = parser.bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        del parser
        self.searchText.setText("Search in {0}".format(text))
        self.searchTextInBook.setText("Search in {0} > {1}".format(text, book))
        self.iSearchText.setText("iSearch in {0}".format(text))
        self.iSearchTextInBook.setText("iSearch in {0} > {1}".format(text, book))
        self.searchBibleTopic.setText("Bible Topic > {0}".format(config.topic))
        self.searchBibleDictionary.setText("Bible Dictionary > {0}".format(config.dictionary))
        self.searchBibleEncyclopedia.setText("Bible Encyclopedia > {0}".format(config.encyclopedia))
        self.searchThirdDictionary.setText("3rd Party Dictionary > {0}".format(config.thirdDictionary))

    def getText(self):
        text = {
            "main": config.mainText,
            "study": config.studyText,
            "instant": config.mainText,
        }
        return text[self.name]

    def getBook(self):
        book = {
            "main": config.mainB,
            "study": config.studyB,
            "instant": config.mainB,
        }
        return book[self.name]

    def addMenuActions(self):
        copyText = QAction(self)
        copyText.setText("Copy")
        copyText.triggered.connect(self.copySelectedText)
        self.addAction(copyText)
        
        self.searchText = QAction(self)
        self.searchText.setText("Search")
        self.searchText.triggered.connect(self.searchSelectedText)
        self.addAction(self.searchText)

        self.searchTextInBook = QAction(self)
        self.searchTextInBook.setText("Search in Current Book")
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        self.addAction(self.searchTextInBook)

        self.iSearchText = QAction(self)
        self.iSearchText.setText("iSearch")
        self.iSearchText.triggered.connect(self.iSearchSelectedText)
        self.addAction(self.iSearchText)

        self.iSearchTextInBook = QAction(self)
        self.iSearchTextInBook.setText("iSearch in Current Book")
        self.iSearchTextInBook.triggered.connect(self.iSearchSelectedTextInBook)
        self.addAction(self.iSearchTextInBook)

        searchBibleCharacter = QAction(self)
        searchBibleCharacter.setText("Bible Character")
        searchBibleCharacter.triggered.connect(self.searchCharacter)
        self.addAction(searchBibleCharacter)

        searchBibleName = QAction(self)
        searchBibleName.setText("Bible Name")
        searchBibleName.triggered.connect(self.searchName)
        self.addAction(searchBibleName)

        searchBibleLocation = QAction(self)
        searchBibleLocation.setText("Bible Location")
        searchBibleLocation.triggered.connect(self.searchLocation)
        self.addAction(searchBibleLocation)

        self.searchBibleTopic = QAction(self)
        self.searchBibleTopic.setText("Bible Topic")
        self.searchBibleTopic.triggered.connect(self.searchTopic)
        self.addAction(self.searchBibleTopic)

        self.searchBibleDictionary = QAction(self)
        self.searchBibleDictionary.setText("Bible Dictionary")
        self.searchBibleDictionary.triggered.connect(self.searchDictionary)
        self.addAction(self.searchBibleDictionary)

        self.searchBibleEncyclopedia = QAction(self)
        self.searchBibleEncyclopedia.setText("Bible Encyclopedia")
        self.searchBibleEncyclopedia.triggered.connect(self.searchEncyclopedia)
        self.addAction(self.searchBibleEncyclopedia)

        self.searchThirdDictionary = QAction(self)
        self.searchThirdDictionary.setText("3rd Party Dictionary")
        self.searchThirdDictionary.triggered.connect(self.searchThirdPartyDictionary)
        self.addAction(self.searchThirdDictionary)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText("Extract All Bible References")
        searchBibleReferences.triggered.connect(self.extractAllReferences)
        self.addAction(searchBibleReferences)

    def messageNoSelection(self):
        self.page().runJavaScript("alert('You have not selected word(s) for this action!')")

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def searchSelectedText(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextInBook(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def iSearchSelectedText(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ISEARCH:::{0}:::{1}".format(self.getText(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def iSearchSelectedTextInBook(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDISEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchResource(self, module):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTOOL:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchCharacter(self):
        self.searchResource("EXLBP")

    def searchName(self):
        self.searchResource("HBN")

    def searchLocation(self):
        self.searchResource("EXLBL")

    def searchTopic(self):
        self.searchResource(config.topic)

    def searchDictionary(self):
        self.searchResource(config.dictionary)

    def searchEncyclopedia(self):
        self.searchResource(config.encyclopedia)

    def searchThirdPartyDictionary(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def extractAllReferences(self):
        selectedText = self.selectedText()
        parser = BibleVerseParser("YES")
        verseList = parser.extractAllReferences(selectedText, False)
        del parser
        if not verseList:
            self.page().runJavaScript("alert('No bible verse reference is found from the text you selected.')")
        else:
            biblesSqlite = BiblesSqlite()
            verses = biblesSqlite.readMultipleVerses(self.getText(), verseList)
            del biblesSqlite
            self.openPopover(html=verses)

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            self.openPopover()
        return super().createWindow(windowType)

    def openPopover(self, name="popover", html="UniqueBible.app"):
        html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script><script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {0}%;'><span id='v0.0.0'></span>{1}</body></html>".format(config.fontSize, html)
        self.popoverView = WebEngineViewPopover(self, name, self.name)
        self.popoverView.setHtml(html, baseUrl)
        self.popoverView.show()


class WebEngineViewPopover(QWebEngineView):
    def __init__(self, parent, name, source):
        super().__init__()
        self.parent = parent
        self.name = name
        self.source = source
        self.setWindowTitle('Unique Bible App - Popover')
        self.titleChanged.connect(self.popoverTextCommandChanged)

    def popoverTextCommandChanged(self, newTextCommand):
        self.parent.parent.parent.textCommandChanged(newTextCommand, self.source)
