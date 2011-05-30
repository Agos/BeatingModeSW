import wx
from wx.xrc import *
import os
import wxmpl
from numpy import *
from beatingmode import BeatingImage
from colors import rate_color_map, ratio_color_map, gray_color_map
import multiprocessing


class MainFrame(wx.Frame):

    def __init__(self, parent, id, title, res):

        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition,
            size=(900, 700), style=wx.DEFAULT_FRAME_STYLE)

        # set up resource file and config file
        self.res = res

        # Load the main panel for the program
        self.panelGeneral = self.res.LoadPanel(self, 'panelGeneral')

        # Initialize the General panel controls
        self.notebook = XRCCTRL(self, 'notebook')

        # Setup the layout for the frame
        mainGrid = wx.BoxSizer(wx.VERTICAL)
        hGrid = wx.BoxSizer(wx.HORIZONTAL)
        hGrid.Add(self.panelGeneral, 1, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTRE,
            border=4)
        mainGrid.Add(hGrid, 1, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTRE)

        # Load the menu for the frame
        menuMain = self.res.LoadMenuBar('menuMain')

        # Bind menu events to the proper methods
        wx.EVT_MENU(self, XRCID('menuOpen'), self.OnOpenMeasure)
        wx.EVT_MENU(self, XRCID('menuExit'), self.OnClose)

        # Set the menu as the default menu for this frame
        self.SetMenuBar(menuMain)

        self.SetSizer(mainGrid)
        self.Layout()

        #Set the Minumum size
        self.SetMinSize((900, 700))
        self.Centre(wx.BOTH)

        # Initialize the welcome notebook tab
        panelWelcome = self.res.LoadPanel(self.notebook, 'panelWelcome')
        self.notebook.AddPage(panelWelcome, 'Welcome')

    def OnOpenMeasure(self, evt):
        wildcard = "Data file (*.dat)|*.dat|" \
            "Ago file (*.ago)|*.ago|" \
            "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a measure file", os.getcwd(),
            "", wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            print("Opening: {0}".format(dialog.GetPath()))
            self.loadData(dialog.GetPath())
            dialog.Destroy()

    def loadData(self, path):
        # Initialize the panel
        self.notebook.DeleteAllPages()
        self.panelReconstruct = self.res.LoadPanel(self.notebook,
            'panelReconstruct')
        self.panelReconstruct.Init(self.res)
        self.notebook.AddPage(self.panelReconstruct, "Rate")
        self.panelReconstruct.Update()
        dialog = wx.ProgressDialog("A progress box", "Loading", 100,
            style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
        dialog.SetSize((300,200))
        dialog.Update(0)
        # Do the actual data loading
        self.bimg = BeatingImage(path=path)
        # Let's reconstruct the image
        manager = multiprocessing.Manager()
        queue = manager.Queue()
        self.bimg.reconstruct_with_update(queue=queue, dialog=dialog)
        dialog.Destroy()
        self.rec_on = self.bimg.reconstructed_on
        # Paint it!
        self.panelReconstruct.guiRebuild.Replot(rec_on=self.rec_on,
            max_rate=self.rec_on.max())

    def OnClose(self, _):
        self.Destroy()


class PanelReconstruct(wx.Panel):

    def __init__(self):
        pre = wx.PrePanel()
        # the Create step is done by XRC.
        self.PostCreate(pre)

    def Init(self, res):
        self.guiRebuild = GuiRebuild(self)
        res.AttachUnknownControl('panelReconstructed',
            self.guiRebuild.panelOnOff, self)
        self.guiRebuild.Replot()


class GuiRebuild:
    """Displays and updates the rebuilt on/off state."""

    def __init__(self, parent):
        self.panelOnOff = wxmpl.PlotPanel(parent, -1, size=(6, 4.50), dpi=68,
            crosshairs=True, autoscaleUnzoom=False)
        self.Replot()

    def Replot(self, rec_on=None, max_rate=None):
        fig = self.panelOnOff.get_figure()
        fig.set_edgecolor('white')
        # clear the axes and replot everything
        if rec_on is not None:
            axes = fig.gca()
            axes.cla()
            axes.imshow(rec_on, cmap=rate_color_map,
            interpolation='nearest', vmin=0.0, vmax=max_rate)
        self.panelOnOff.draw()


class bmgui(wx.App):

    def OnInit(self):
        wx.InitAllImageHandlers()
        wx.GetApp().SetAppName("bmgui")

        # Load the XRC file for our gui resources
        self.res = XmlResource('main.xrc')

        bmFrame = MainFrame(None, -1, "bmgui", self.res)
        self.SetTopWindow(bmFrame)
        bmFrame.Centre()
        bmFrame.Show()
        return 1


if __name__ == '__main__':
    app = bmgui(0)
    app.MainLoop()