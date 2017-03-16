from browser import document, html, ajax
import json
import time
from datetime import datetime


class File(object):
    def __init__(self, files_list, name, is_dir=False, size=None, created=None, **kwargs):
        self.files_list = files_list
        self.name = name
        self.is_dir = is_dir
        self.size = size
        self.created = created.replace('-', '.') if created else created

        self.selected = False
        self.super_selected = False
        self.element = html.TR()
        self.element.bind('click', self.on_click)
        self.element.bind('dblclick', self.on_double_click)
        self.render()

    def __update(function=None):
        def wrapper(*args, **kwargs):
            self = args[0]
            event = args[1]
            result = function(*args, **kwargs)

            self.render()
            print(self.name, event.type)

            return result
        return wrapper

    def render(self):
        self.element.className = 'file' + (
            ' selected' if self.selected else ' super-selected' if self.super_selected else '')

        if not self.element.html:
            img = '<img src="/static/images/icons/%s.png"/>' % ('folder' if self.is_dir else 'file')
            args = (img, self.name, self.size, self.created)
            self.element.html = ''.join(['<td>%s</td>' % (a if a else '') for a in args])

    def reset_siblings_selection(self):
        for sibling in self.files_list.files:
            if sibling != self:
                sibling.selected = False
                sibling.super_selected = False
                sibling.render()

    @__update
    def on_click(self, event):
        self.selected = not self.selected
        if not event.ctrlKey:
            self.reset_siblings_selection()

    @__update
    def on_double_click(self, event):
        self.super_selected = True
        if not event.ctrlKey:
            self.reset_siblings_selection()

        if self.is_dir:
            # self.files_list.file_browser.path_bar.set_path(self.name)
            self.files_list.file_browser.open_dir(self.name)


class PathBar(object):
    def __init__(self):
        self.element = html.DIV(id='path-bar')
        self.path = '/'
        self.render()

    def render(self):
        self.element.html = self.path

    def set_path(self, path):
        if path == '..':
            self.path = '/'.join(self.path.split('/')[0:-1])
            self.path = '/' if not self.path else self.path
        else:
            self.path = self.path+'/'+path
            self.path = self.path.replace('//', '/')
        self.render()


class FilesList(object):
    def __init__(self, file_browser):
        self.file_browser = file_browser
        self.files_data = []
        self.files = []
        self.get_files_data()        
        self.element = html.TABLE(id='files-list')
        self.render()

    def get_files_data(self, path=''):
        def success(req):
            if req.status == 200:
                self.files_data = sorted(json.loads(req.text), key=lambda x: (not x['is_dir'], x['name'].lower()))
                print(self.files_data)
                self.render()

        req = ajax.ajax()
        req.bind('complete', success)
        req.open('GET', '/files'+path, True)
        req.set_timeout(5, 'timeout message')
        req.send()

    def load_files(self):
        if self.files_data:
            self.files = [File(self, **{'name': '..', 'is_dir': True})]

            for file_data in self.files_data:
                self.files.append(File(self, **file_data))

    def render(self):
        headers = ('', 'Name', 'Size', 'Created')
        self.element.html = '<tr>%s</tr>' % ''.join(['<th>%s</th>' % h for h in headers])

        self.load_files()
        for file in self.files:
            self.element.append(file.element)


class FileBrowser(object):
    def __init__(self):
        self.element = html.DIV(id='file-browser')
        self.path_bar = PathBar()
        self.files_list = FilesList(self)
        self.render()

    def render(self):
        self.element.append(self.path_bar.element)
        self.element.append(self.files_list.element)

    def open_dir(self, dir_name):
        self.path_bar.set_path(dir_name)
        self.files_list.get_files_data(path=self.path_bar.path)
        self.files_list.load_files()
        self.files_list.render()


file_browser = FileBrowser()
document['main'].append(file_browser.element)