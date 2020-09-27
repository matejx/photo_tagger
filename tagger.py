#!/usr/bin/python3

import sys,os,wx,json,shutil

class PhotoTagger(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title='Photo Tagger')

		self.bgCol = wx.Colour(40,44,52)
		self.txtCol = wx.Colour(171,178,169)
		self.darkTheme = False
		self.phototags = {}
		self.alltags = []
		self.photofns = {}
		self.tagsfn = ""
		self.filtertags = ""
		self.changedTags = False

	def createWidgets(self):
		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.panel = wx.Panel(self)
		if self.darkTheme:
			self.panel.SetBackgroundColour(self.bgCol)

		menu1 = wx.Menu()
		menuItem1_1 = menu1.Append(wx.ID_ANY, "Add directory")
		menuItem1_2 = menu1.Append(wx.ID_ANY, "Add files")
		menuItem1_3 = menu1.Append(wx.ID_ANY, "Copy to...")
		menuItem1_4 = menu1.Append(wx.ID_ANY, "Symlink in...")
		menu1.Bind(wx.EVT_MENU, self.onAddDir, menuItem1_1)
		menu1.Bind(wx.EVT_MENU, self.onAddFiles, menuItem1_2)
		menu1.Bind(wx.EVT_MENU, self.onCopyTo, menuItem1_3)
		menu1.Bind(wx.EVT_MENU, self.onSymlinkTo, menuItem1_4)

		menu2 = wx.Menu()
		menuItem2_1 = menu2.Append(wx.ID_ANY, "Open")
		menuItem2_2 = menu2.Append(wx.ID_ANY, "Add")
		menuItem2_3 = menu2.Append(wx.ID_ANY, "Save")
		menuItem2_4 = menu2.Append(wx.ID_ANY, "Save as")
		menu2.Bind(wx.EVT_MENU, self.onTagsOpen, menuItem2_1)
		menu2.Bind(wx.EVT_MENU, self.onTagsAdd, menuItem2_2)
		menu2.Bind(wx.EVT_MENU, self.onTagsSave, menuItem2_3)
		menu2.Bind(wx.EVT_MENU, self.onTagsSaveAs, menuItem2_4)

		menu3 = wx.Menu()
		menuItem3_1 = menu3.Append(wx.ID_ANY, "All")
		menuItem3_2 = menu3.Append(wx.ID_ANY, "Untagged")
		menuItem3_3 = menu3.Append(wx.ID_ANY, "Tags...")
		menu3.Bind(wx.EVT_MENU, self.onFilterAll, menuItem3_1)
		menu3.Bind(wx.EVT_MENU, self.onFilterUntagged, menuItem3_2)
		menu3.Bind(wx.EVT_MENU, self.onFilterTags, menuItem3_3)

		menuBar = wx.MenuBar()
		menuBar.Append(menu1, "Photos")
		menuBar.Append(menu2, "Tags")
		menuBar.Append(menu3, "Filter")
		self.SetMenuBar(menuBar)

		self.statusBar = self.CreateStatusBar(1)
		self.statusBar.SetStatusText("Hello!")

		self.photoView = wx.StaticBitmap(self.panel, wx.ID_ANY)
		self.photoView.SetMinClientSize(wx.Size(800, 600))
		self.photoView.Bind(wx.EVT_LEFT_DCLICK, self.onPhotoClick)
		self.displayedPhotoPath = ""
		#self.photoView.SetScaleMode(wx.StaticBitmap.ScaleMode.Scale_AspectFit) # requires wxpython 4.1

		self.tagsList = wx.ListView(self.panel, wx.ID_ANY, style=wx.LC_LIST)
		if self.darkTheme:
			self.tagsList.SetBackgroundColour(self.bgCol)
			self.tagsList.SetTextColour(self.txtCol)
		if sys.platform == "win32":
			self.tagsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onTagSelectedWin)
			self.tagsList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onTagDeselectedWin)
		else:
			self.tagsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onTagSelected)
		self.tagsList.Bind(wx.EVT_LIST_KEY_DOWN, self.onTagsListKey)
		self.onTagSelected_disable = False

		self.photoList = wx.ListView(self.panel, wx.ID_ANY, style=wx.LC_LIST|wx.LC_SINGLE_SEL)
		#self.photoList.AppendColumn("Photo")
		if self.darkTheme:
			self.photoList.SetBackgroundColour(self.bgCol)
			self.photoList.SetTextColour(self.txtCol)
		self.photoList.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onPhotoFocused)
		self.photoList.Bind(wx.EVT_KEY_DOWN, self.onTagsListKey)

		self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer1.Add(self.photoList, 1, wx.EXPAND | wx.ALL, 5)
		self.sizer1.Add(self.photoView, 1, wx.ALL, 5)
		self.sizer1.Add(self.tagsList, 1, wx.EXPAND | wx.ALL, 5)
		self.panel.SetSizer(self.sizer1)
		self.sizer1.Fit(self)
		#self.panel.Layout()

	def RebuildPhotoFns(self):
		self.photofns = {}
		for fn in self.phototags:
			self.photofns[os.path.basename(fn)] = fn

	def GetSelectedPhoto(self):
		i = self.photoList.GetFocusedItem()
		if i == -1: return ""
		p = self.photoList.GetItemText(i)
		return self.photofns[p]

	def DisplayAllTags(self):
		self.tagsList.DeleteAllItems()
		for t in self.alltags:
			self.tagsList.Append([t])

	def DisplayPhotoTags(self, fn):
		self.onTagSelected_disable = True
		for i in range(self.tagsList.GetItemCount()):
			on = self.tagsList.GetItemText(i) in self.phototags[fn]
			self.tagsList.Select(i, on)
		self.onTagSelected_disable = False

	def DisplayAllPhotos(self):
		self.photoList.DeleteAllItems()
		for fn in sorted(self.phototags):
			self.photoList.Append([os.path.basename(fn)])

	def DisplayMsg(self, cap, msg):
		mbox = wx.MessageDialog(None, msg, cap, style=wx.OK)
		mbox.ShowModal()
		mbox.Destroy()

	def DisplayPhotoListCount(self):
		self.statusBar.SetStatusText(str(self.photoList.GetItemCount()) + ' photos')

	def onFilterAll(self, event):
		self.DisplayAllPhotos()
		self.DisplayPhotoListCount()

	def onFilterUntagged(self, event):
		self.photoList.DeleteAllItems()
		for fn in sorted(self.phototags):
			if not len(self.phototags[fn]):
				self.photoList.Append([os.path.basename(fn)])
		self.DisplayPhotoListCount()

	def onFilterTags(self, event):
		s = ""
		dialog = wx.TextEntryDialog(None, "Enter Tags", value=self.filtertags)
		if dialog.ShowModal() == wx.ID_OK:
			s = dialog.GetValue()
		dialog.Destroy()
		if len(s):
			self.filtertags = s
			op = "&"
			if s[0] in ["&","|","=","!"]:
				op = s[0]
				s = s[1:]
			ftags = set([x.strip() for x in s.split(',')])
			#print(op, ftags)
			atags = set(self.alltags)
			if not ftags <= atags:
				self.DisplayMsg('Warning','Invalid tags in your query')
			self.photoList.DeleteAllItems()
			for fn in sorted(self.phototags):
				ptags = set(self.phototags[fn])
				if (op == "&") and (ftags <= ptags):
					self.photoList.Append([os.path.basename(fn)])
					continue
				if (op == "|") and len(ftags & ptags):
					self.photoList.Append([os.path.basename(fn)])
					continue
				if (op == "=") and (ftags == ptags):
					self.photoList.Append([os.path.basename(fn)])
					continue
				if (op == "!") and not len(ftags & ptags):
					self.photoList.Append([os.path.basename(fn)])
					continue
			self.DisplayPhotoListCount()


	def CopyPhotosTo(self, symlink=False):
		dialog = wx.DirDialog(None, "Open", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
		if dialog.ShowModal() == wx.ID_OK:
			dir = dialog.GetPath()
			for i in range(self.photoList.GetItemCount()):
				p = self.photoList.GetItemText(i)
				fn = self.photofns[p]
				dst = os.path.join(dir, os.path.basename(fn))
				if os.path.isfile(dst): continue
				if symlink:
					os.symlink(fn, dst)
				else:
					shutil.copyfile(fn, dst)
				print("{} --> {} ({}/{})".format(fn, dst, i+1, self.photoList.GetItemCount()))
		dialog.Destroy()

	def onCopyTo(self, event):
		self.CopyPhotosTo()

	def onSymlinkTo(self, event):
		self.CopyPhotosTo(symlink=True)

	def SaveTags(self, fn):
		f = open(fn, 'w')
		json.dump({'alltags':self.alltags,'phototags':self.phototags}, f, indent=4)
		f.close()
		self.changedTags = False

	def OpenTags(self, fn):
		f = open(self.tagsfn,'r')
		d = json.load(f)
		f.close()
		self.alltags = sorted(d['alltags'])
		self.phototags = d['phototags']
		self.RebuildPhotoFns()
		self.DisplayAllPhotos()
		self.DisplayAllTags()
		self.DisplayPhotoListCount()
		self.changedTags = False

	def onTagsSave(self, event):
		if self.tagsfn:
			self.SaveTags(self.tagsfn)
		else:
			self.onTagsSaveAs(event)

	def onTagsSaveAs(self, event):
		dialog = wx.FileDialog(None, "Save", wildcard="*.json", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dialog.ShowModal() == wx.ID_OK:
			self.tagsfn = dialog.GetPath()
			self.SaveTags(self.tagsfn)
		dialog.Destroy()

	def onTagsOpen(self, event):
		dialog = wx.FileDialog(None, "Open", wildcard="*.json", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if dialog.ShowModal() == wx.ID_OK:
			self.tagsfn = dialog.GetPath()
			self.OpenTags(self.tagsfn)
		dialog.Destroy()

	def AddTag(self, t):
		if t not in self.alltags:
			self.alltags.append(t)
			self.alltags.sort()
			self.DisplayAllTags()

	def onTagsAdd(self, event):
		dialog = wx.TextEntryDialog(None, "Add Tag", "")
		if dialog.ShowModal() == wx.ID_OK:
			for s in dialog.GetValue().split(','):
				self.AddTag(s.strip())
		dialog.Destroy()

	def onTagsListKey(self, event):
		kc = event.GetKeyCode()
		if kc == 87 or kc == 65 or kc == 83 or kc == 68: # WSAD
			d = 1
			if kc == 87 or kc == 65: d = -1
			c = self.photoList.GetItemCount()
			if c == 0: return
			i = self.photoList.GetFocusedItem() + d
			if i >= c: i = 0
			if i < 0: i = c - 1
			self.photoList.Focus(i)
			self.photoList.Select(i)
			return
		event.Skip()

	def onTagSelected(self, event):
		if self.onTagSelected_disable: return
		fn = self.GetSelectedPhoto()
		if not fn: return
		t = event.GetText()
		if t not in self.phototags[fn]:
			self.phototags[fn].append(t)
		else:
			self.phototags[fn].remove(t)
		self.changedTags = True
		self.DisplayPhotoTags(fn)

	def onTagSelectedWin(self, event):
		if self.onTagSelected_disable: return
		fn = self.GetSelectedPhoto()
		if not fn: return
		t = event.GetText()
		if t not in self.phototags[fn]:
			self.phototags[fn].append(t)
			self.changedTags = True

	def onTagDeselectedWin(self, event):
		if self.onTagSelected_disable: return
		fn = self.GetSelectedPhoto()
		if not fn: return
		t = event.GetText()
		if t in self.phototags[fn]:
			self.phototags[fn].remove(t)
			self.changedTags = True

	def onAddFiles(self, event):
		dialog = wx.FileDialog(None, "Open", wildcard="*.jpg", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
		if dialog.ShowModal() == wx.ID_OK:
			for fn in sorted(dialog.GetPaths()):
				if fn not in self.phototags:
					self.phototags[fn] = []
			self.RebuildPhotoFns()
			self.DisplayAllPhotos()
			self.DisplayPhotoListCount()
		dialog.Destroy()

	def onAddDir(self, event):
		dialog = wx.DirDialog(None, "Open", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
		if dialog.ShowModal() == wx.ID_OK:
			dir = dialog.GetPath()
			for bfn in sorted(os.listdir(dir)):
				sfn = os.path.splitext(bfn)
				if sfn[1] != '.jpg': continue
				fn = os.path.join(dir, bfn)
				if fn not in self.phototags:
					self.phototags[fn] = []
			self.RebuildPhotoFns()
			self.DisplayAllPhotos()
			self.DisplayPhotoListCount()
		dialog.Destroy()

	def onPhotoFocused(self, event):
		p = event.GetText()
		if not p: return
		fn = self.photofns[p]
		if os.path.isfile(fn):
			img = wx.Image(fn, wx.BITMAP_TYPE_ANY)
			# scale the image
			maxw = self.photoView.GetMinClientSize()[0]
			maxh = self.photoList.GetSize()[1] # ugly dirty hack
			w = img.GetWidth()
			h = img.GetHeight()
			f = 1.0
			if w > maxw:
				f = 1.0 * maxw / w
			if f*h > maxh:
				f = 1.0 * maxh / h
			self.photoView.SetBitmap(wx.Bitmap(img.Scale(w*f, h*f)))
			self.displayedPhotoPath = fn
		else:
			self.photoView.SetBitmap(wx.Bitmap())
			self.displayedPhotoPath = ""
		self.DisplayPhotoTags(fn)

	def onPhotoClick(self, event):
		if self.displayedPhotoPath:
			v = "eog"
			if sys.platform == "win32": v = "start"
			os.system(v + " " + self.displayedPhotoPath)

	def onClose(self, event):
		if event.CanVeto() and self.changedTags:
			if wx.MessageBox("Tags changed. Really quit?", "Quit", wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
				event.Veto()
				return
		event.Skip()

if __name__ == '__main__':
	print(wx.version())
	print(sys.platform)
	app = wx.App(False)
	mainframe = PhotoTagger()
	mainframe.darkTheme = "--dark" in sys.argv
	mainframe.createWidgets()
	mainframe.Show()
	app.MainLoop()
