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


_font = QFont('Courier')
_SHA1WIDTH = 350


def _label(title):
    label = QLabel(title)
    label.adjustSize()
    return label


def _lineEdit(readonly=False, width=None, changed=None):
    line = QLineEdit()
    line.setFont(_font)
    line.setReadOnly(readonly)
    if changed is not None:
        line.textEdited.connect(changed)
    if width is not None:
        line.setMinimumWidth(width)
    return line


def _textEdit(readonly=False, height=None):
    text = QTextEdit()
    text.setFont(_font)
    text.setReadOnly(readonly)
    if height is not None:
        text.setMaximumHeight(height)
    return text


class DropArea(QLabel):

    changedData = pyqtSignal(QMimeData)

    def __init__(self):
        super(DropArea, self).__init__()
        self.setText('<Drop SC2Bank file here>')
        self.setMinimumSize(200, 200)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Dark)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        self.setBackgroundRole(QPalette.Highlight)
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        self.setBackgroundRole(QPalette.Dark)
        self.changedData.emit(event.mimeData())

    def dragLeaveEvent(self, event):
        self.setBackgroundRole(QPalette.Dark)


class DropSiteWindow(QWidget):

    changedData = pyqtSignal(QMimeData)
    WINDOW_TITLE = 'SC2Bank Signer'

    def __init__(self):
        super(DropSiteWindow, self).__init__()

        self.model = None
        self.createGUI()

    def createGUI(self):
        self.oldSigLabel = _label("Old signature:")
        self.oldSigText = _lineEdit(readonly=True, width=_SHA1WIDTH)

        self.newSigLabel = _label("New signature:")
        self.newSigText = _lineEdit(readonly=True, width=_SHA1WIDTH)

        self.fileNameLabel = _label("File name:")
        self.fileNameText = _textEdit(readonly=True, height=60)

        self.authorIdLabel = _label("Author ID:")
        self.authorIdText = _lineEdit(changed=self.authorChanged)

        self.userIdLabel = _label("User ID:")
        self.userIdText = _lineEdit(changed=self.userChanged)

        self.bankNameLabel = _label("Bank Name:")
        self.bankNameText = _lineEdit(changed=self.nameChanged)

        self.dropArea = DropArea()
        self.dropArea.changedData.connect(self.droppedSC2Bank)

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
        mainLayout.addWidget(self.dropArea)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(350, 500)        

    def clear(self):
        for widget in [self.newSigText, self.oldSigText, self.fileNameText,
                       self.authorIdText, self.userIdText, self.bankNameText]:
            widget.setText('')

        self.model = None

    def updateSignature(self):
        if self.model:
            self.model.save()
            self.model = Model(self.model.file)
            self.reflectModel()

    def reflectModel(self):
        self.oldSigText.setText(self.model.recorded_signature)
        self.newSigText.setText(self.model.calculate_signature())
        self.authorIdText.setText(self.model.author_id)
        self.userIdText.setText(self.model.user_id)
        self.bankNameText.setText(self.model.name)
        self.fileNameText.setText(self.model.file)
        self.setWindowTitle(''.join([self.WINDOW_TITLE + ': ', self.model.name]))

    def droppedSC2Bank(self, mimeData=None):
        if mimeData is None or not mimeData.hasUrls():
            return

        urls = mimeData.urls()

        if len(urls) > 1:
            raise NotImplemented('Can only handle one file at once.')

        fname = urls[0].path()

        self.model = Model(fname)
        self.reflectModel()

    def authorChanged(self, event):
        if self.model:
            self.model.update(author_id=self.authorIdText.text())
            self.newSigText.setText(self.model.calculate_signature())

    def userChanged(self, event):
        if self.model:
            self.model.update(user_id=self.userIdText.text())
            self.newSigText.setText(self.model.calculate_signature())

    def nameChanged(self, event):
        if self.model:
            self.model.update(name=self.bankNameText.text())
            self.newSigText.setText(self.model.calculate_signature())


class Model(object):

    def __init__(self, file_):
        self.file = file_

        info = sc2bank.inspect_file_path(file_)
        self.author_id = info.author_id
        self.user_id = info.user_id
        self.name = info.name

        with open(file_, 'r') as f:
            self.contents = f.read()

        self.bank, self.recorded_signature = sc2bank.parse(self.contents, from_string=True)

    def calculate_signature(self):
        return sc2bank.sign(self.author_id, self.user_id, self.name, self.bank)

    def update(self, **changes):
        for k, v in changes.iteritems():
            if k == 'author_id':
                self.author_id = v
            if k == 'user_id':
                self.user_id = v
            if k == 'name':
                self.name = v

    def save(self, file_=None):
        if file_ is None:
            file_ = self.file
        signature = self.calculate_signature()
        if self.contents.count(self.recorded_signature) != 1:
            raise RuntimeError('There are more than one occurence of the hash, not replacing.')
            return
        with open(file_, 'w') as f:
            f.write(str.replace(self.contents, self.recorded_signature, signature))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = DropSiteWindow()
    window.show()
    sys.exit(app.exec_())

