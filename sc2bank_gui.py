#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2010 Hans-Peter Jansen <hpj@urpla.net>.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtCore import pyqtSignal, QMimeData, Qt
from PyQt5.QtGui import QPalette, QPixmap, QFont
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialogButtonBox,
        QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
        QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QGridLayout, QTextEdit,
        QTreeWidget)
import hashlib
import sc2bank


class DropSiteWindow(QWidget):

    SHA1WIDTH = 350
    changed = pyqtSignal(QMimeData)
    WINDOW_TITLE = 'SC2Bank Signer'

    def __init__(self):
        super(DropSiteWindow, self).__init__()

        font = QFont('Courier')

        self.sc2bank = None

        self.changed.connect(self.droppedSC2Bank)

        self.setAcceptDrops(True)

        self.setAutoFillBackground(True)

        self.oldSigLabel = QLabel("Old signature:")
        self.oldSigLabel.adjustSize()
        self.oldSigText = QLineEdit()
        self.oldSigText.setReadOnly(True)
        self.oldSigText.setMinimumWidth(self.SHA1WIDTH)
        self.oldSigText.setFont(font)

        self.newSigLabel = QLabel("New signature:")
        self.newSigLabel.adjustSize()
        self.newSigText = QLineEdit()
        self.newSigText.setReadOnly(True)
        self.newSigText.setMinimumWidth(self.SHA1WIDTH)
        self.newSigText.setFont(font)

        self.fileNameLabel = QLabel("File name:")
        self.fileNameLabel.adjustSize()
        self.fileNameText = QTextEdit()
        self.fileNameText.setReadOnly(True)
        self.fileNameText.setFont(font)
        self.fileNameText.setMaximumHeight(60)

        self.authorIdLabel = QLabel("Author ID:")
        self.authorIdLabel.adjustSize()
        self.authorIdText = QLineEdit()
        self.authorIdText.setFont(font)

        self.userIdLabel = QLabel("User ID:")
        self.userIdLabel.adjustSize()
        self.userIdText = QLineEdit()
        self.userIdText.setFont(font)

        self.bankNameLabel = QLabel("Bank Name:")
        self.bankNameLabel.adjustSize()
        self.bankNameText = QLineEdit()
        self.bankNameText.setFont(font)

        # self.bankLabel = QLabel("Bank XML")
        # self.bankLabel.adjustSize()
        # self.bankText = QTextEdit()
        # self.bankText.setFont(font)
        # self.bankText.setReadOnly(True)

        self.dropArea = QLabel('<Drop SC2Bank file here>')
        self.dropArea.setMinimumSize(200, 200)
        self.dropArea.setAutoFillBackground(True)
        self.dropArea.setBackgroundRole(QPalette.Dark)
        self.dropArea.setAlignment(Qt.AlignCenter)

        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.oldSigLabel, 0, 0)
        self.gridLayout.addWidget(self.oldSigText, 0, 1)
        self.gridLayout.addWidget(self.newSigLabel, 1, 0)
        self.gridLayout.addWidget(self.newSigText, 1, 1)
        self.gridLayout.addWidget(self.fileNameLabel, 2, 0)
        self.gridLayout.addWidget(self.fileNameText, 2, 1)
        self.gridLayout.addWidget(self.authorIdLabel, 3, 0)
        self.gridLayout.addWidget(self.authorIdText, 3, 1)
        self.gridLayout.addWidget(self.userIdLabel, 4, 0)
        self.gridLayout.addWidget(self.userIdText, 4, 1)
        self.gridLayout.addWidget(self.bankNameLabel, 5, 0)
        self.gridLayout.addWidget(self.bankNameText, 5, 1)

        self.clearButton = QPushButton("Clear")
        self.quitButton = QPushButton("Quit")
        self.updateSignatureButton = QPushButton("Update Signature")

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.clearButton, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.updateSignatureButton, QDialogButtonBox.ApplyRole)
        self.buttonBox.addButton(self.quitButton, QDialogButtonBox.RejectRole)

        self.quitButton.pressed.connect(self.close)
        self.clearButton.pressed.connect(self.clear)
        self.updateSignatureButton.pressed.connect(self.updateSignature)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.gridLayout)
        # mainLayout.addWidget(self.bankLabel)
        # mainLayout.setAlignment(self.bankLabel, Qt.AlignHCenter)
        # mainLayout.addWidget(self.bankText)
        mainLayout.addWidget(self.dropArea)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(350, 500)


    def dragEnterEvent(self, event):
        self.setBackgroundRole(QPalette.Highlight)
        self.dropArea.setBackgroundRole(QPalette.Highlight)
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        self.setBackgroundRole(QPalette.Window)
        self.dropArea.setBackgroundRole(QPalette.Dark)
        self.changed.emit(event.mimeData())

    def dragLeaveEvent(self, event):
        self.setBackgroundRole(QPalette.Window)
        self.dropArea.setBackgroundRole(QPalette.Dark)


    def clear(self):
        for widget in [self.newSigText, self.oldSigText, self.fileNameText,
                       self.authorIdText, self.userIdText, self.bankNameText,
                       self.bankText]:
            widget.setText('')

        self.sc2bank = None


    def updateSignature(self):
        if self.sc2bank is None:
            return
        if self.sc2bank['new'] != self.sc2bank['old']:
            contents = ''
            with open(self.sc2bank['name'], 'r') as f:
                contents = f.read()
            count = contents.count(self.sc2bank['old'])
            print(count, contents)
            if count != 1:
                raise RuntimeError('There are more than one occurence of the hash, not replacing.')
                return
            with open(self.sc2bank['name'], 'w') as f:
                f.write(str.replace(contents, self.sc2bank['old'], self.sc2bank['new']))
            self.checkSC2Bank()

    def checkSC2Bank(self, name=None):
        if name is None:
            name = self.sc2bank['name']
        else:
            self.sc2bank = {}


        author_id, user_id, bank_name = sc2bank.inspect_file_path(name)
        with open(name) as f:
            contents = f.read()
        checksum = hashlib.sha1(contents)
        bank, old = sc2bank.parse_sc2bank(contents, from_string=True)
        new = None
        if None not in [author_id, user_id, bank_name, bank]:
           new = sc2bank.sign(author_id, user_id, bank_name, bank)
        self.sc2bank = {
            'old': old,
            'new': new,
            'name': name,
            'bank_name': bank_name,
            'author_id': author_id,
            'user_id': user_id,
            'contents': contents,
            'checksum': checksum
        }
        self.oldSigText.setText(old)
        self.newSigText.setText(new)
        self.authorIdText.setText(author_id)
        self.userIdText.setText(user_id)
        self.bankNameText.setText(bank_name)
        self.fileNameText.setText(name)
        self.bankText.setText(contents)
        self.setWindowTitle(''.join([self.WINDOW_TITLE + ': ', bank_name]))

    def droppedSC2Bank(self, mimeData=None):
        if mimeData is None or not mimeData.hasUrls():
            return

        urls = mimeData.urls()

        if len(urls) > 1:
            raise NotImplemented('Can only handle one file at once.')

        fname = urls[0].path()

        self.checkSC2Bank(fname)



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = DropSiteWindow()
    window.show()
    sys.exit(app.exec_())

