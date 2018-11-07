#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2018 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import absolute_import, print_function

import os
import wx

from ._base import PavloviaMiniBrowser
from psychopy.projects import pavlovia
from psychopy.localization import _translate

try:
    import wx.adv as wxhl  # in wx 4
except ImportError:
    wxhl = wx  # in wx 3.0.2


def setLocalPath(parent, project=None, path=""):
    """Open a DirDialog and set the project local folder to that specified

    Returns
    ----------

    None for no change and newPath if this has changed from previous
    """
    if path:
        origPath = path
    elif project and 'localRoot' in project:
        origPath = project.localRoot
    else:
        origPath = ""
    # create the dialog
    dlg = wx.DirDialog(
            parent,
            defaultPath=origPath,
            message=_translate(
                    "Choose/create the root location for the synced project"))
    if dlg.ShowModal() == wx.ID_OK:
        newPath = dlg.GetPath()
        if os.path.isfile(newPath):
            newPath = os.path.split(newPath)[0]
        if newPath != origPath:
            if project:
                project.localRoot = newPath
        return newPath


def logInPavlovia(parent, event=None):
    """Opens the built-in browser dialog to login to pavlovia

    Returns
    -------
    None (user closed window without logging on) or a gitlab.User object
    """
    # check known users list
    dlg = PavloviaMiniBrowser(parent=parent, loginOnly=True)
    dlg.ShowModal()  # with loginOnly=True this will EndModal once logged in
    if dlg.tokenInfo:
        token = dlg.tokenInfo['token']
        pavlovia.login(token, rememberMe=True)  # log in to the current pavlovia session
        return pavlovia.getCurrentSession().user


def logOutPavlovia(parent, event=None):
    """Opens the built-in browser dialog to login to pavlovia

    Returns
    -------
    None (user closed window without logging on) or a gitlab.User object
    """
    # also log out of gitlab session in python
    pavlovia.logout()
    # create minibrowser so we can logout of the session
    dlg = PavloviaMiniBrowser(parent=parent, logoutOnly=True)
    dlg.logout()
    dlg.Destroy()


def showCommitDialog(parent, project, initMsg=""):
    """Brings up a commit dialog (if there is anything to commit

    Returns
    -------
    0 nothing to commit
    1 successful commit
    -1 user cancelled
    """
    changeDict, changeList = project.getChanges()
    # if changeList is empty then nothing to do
    if not changeList:
        return 0

    infoStr = "Changes to commit:\n"
    for categ in ['untracked', 'changed', 'deleted', 'renamed']:
        changes = changeDict[categ]
        if categ == 'untracked':
            categ = 'New'
        if changes:
            infoStr += "\t{}: {} files\n".format(categ.title(), len(changes))
    
    dlg = wx.Dialog(parent, id=wx.ID_ANY, title="Committing changes")
    
    updatesInfo = wx.StaticText(dlg, label=infoStr)
    
    commitTitleLbl = wx.StaticText(dlg, label='Summary of changes')
    commitTitleCtrl = wx.TextCtrl(dlg, size=(500, -1), value=initMsg)
    commitTitleCtrl.SetToolTip(wx.ToolTip(_translate(
        "A title summarizing the changes you're making in these files"
        )))
    commitDescrLbl = wx.StaticText(dlg, label='Details of changes\n (optional)')
    commitDescrCtrl = wx.TextCtrl(dlg, size=(500, 200),
                                  style=wx.TE_MULTILINE | wx.TE_AUTO_URL)
    commitDescrCtrl.SetToolTip(wx.ToolTip(_translate(
        "Optional further details about the changes you're making in these files"
        )))
    commitSizer = wx.FlexGridSizer(cols=2, rows=2, vgap=5, hgap=5)
    commitSizer.AddMany([(commitTitleLbl, 0, wx.ALIGN_RIGHT),
                       commitTitleCtrl,
                       (commitDescrLbl, 0, wx.ALIGN_RIGHT),
                       commitDescrCtrl
                       ])

    btnOK  = wx.Button(dlg, wx.ID_OK)
    btnCancel  = wx.Button(dlg, wx.ID_CANCEL)
    buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
    buttonSizer.AddMany([btnCancel, btnOK])

    # main sizer and layout
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    mainSizer.Add(updatesInfo, 0, wx.ALL, border=5)
    mainSizer.Add(commitSizer, 1, wx.ALL | wx.EXPAND, border=5)
    mainSizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_RIGHT, border=5)
    dlg.SetSizerAndFit(mainSizer)
    dlg.Layout()
    if dlg.ShowModal() == wx.ID_CANCEL:
        return -1

    commitMsg = commitTitleCtrl.GetValue()
    if commitDescrCtrl.GetValue():
        commitMsg += "\n\n" + commitDescrCtrl.GetValue()
    project.stageFiles(changeList)

    project.commit(commitMsg)
    return 1


def noGitWarning(parent):
    """Raise a simpler warning dialog that the user needs to install git first"""
    dlg = wx.Dialog(parent=parent, style=wx.ICON_ERROR | wx.OK | wx.STAY_ON_TOP)

    errorBitmap = wx.ArtProvider.GetBitmap(
        wx.ART_ERROR, wx.ART_MESSAGE_BOX
    )
    errorBitmapCtrl = wx.StaticBitmap(dlg, -1)
    errorBitmapCtrl.SetBitmap(errorBitmap)

    msg = wx.StaticText(dlg, label=_translate("You need to install git to use Pavlovia projects"))
    link = wxhl.HyperlinkCtrl(dlg, url="https://git-scm.com/")
    OK = wx.Button(dlg, wx.ID_OK, label="OK")

    msgsSizer = wx.BoxSizer(wx.VERTICAL)
    msgsSizer.Add(msg, 1, flag=wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, border=5)
    msgsSizer.Add(link, 1, flag=wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, border=5)
    msgsAndIcon = wx.BoxSizer(wx.HORIZONTAL)
    msgsAndIcon.Add(errorBitmapCtrl, 0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
    msgsAndIcon.Add(msgsSizer, 1, flag=wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, border=5)

    mainSizer = wx.BoxSizer(wx.VERTICAL)
    mainSizer.Add(msgsAndIcon, 0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
    mainSizer.Add(OK, 0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
    
    dlg.SetSizerAndFit(mainSizer)
    dlg.Layout()
    dlg.ShowModal()
