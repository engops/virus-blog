#!/usr/bin/env python
import datetime
from flask import render_template, Flask
from flask import Flask
import io
import os
import shutil
import re

WEB_URL = os.environ.get('WEB_URL') or 'http://127.0.0.1:83'
document_root = os.environ.get('document_root') or '/var/www/html4'

basedir = os.path.abspath(os.path.dirname(__file__))
pages = os.path.join(basedir, 'pages')

for i in os.listdir( pages ):
  dest_dir = os.path.join(document_root, i )
  if os.path.isdir( dest_dir ):
    shutil.rmtree( dest_dir )
    os.mkdir( dest_dir )
  else:
    os.mkdir( dest_dir )

def Indexer_Time( filename ):
  x = datetime.datetime.now()
  f = io.open(filename,'r', encoding="utf-8")
  temp = f.read()
  f.close()
  if not re.search(r'##markdate##', temp): 
    f = open(filename, 'w')
    f.write("##markdate##\n")
    f.write("%s/%s/%s\n" % (x.day, x.month, x.year) )
    f.write("##markdate##\n")
    f.close()
    f = io.open(filename, 'a')
    f.write(temp)
    f.close()

def Indexer_Title( filename ):
  x = datetime.datetime.now()
  f = io.open(filename,'r', encoding="utf-8")
  temp = f.read()
  f.close()
  if not re.search(r'#title#', temp): 
    filename_path = os.path.split(filename)[-1].replace('.site','').replace('_',' ')
    f = open(filename, 'w')
    f.write("#title#\n")
    f.write("%s\n" % filename_path)
    f.write("#title#\n")
    f.close()
    f = io.open(filename, 'a')
    f.write(temp)
    f.close()

def Dirs():
  dirs = {}
  for item in os.listdir(pages):
    if os.listdir(os.path.join(pages, item)):
      pages_site = []
      for sts in os.listdir(os.path.join(pages, item)):
        if sts.endswith('.site'):
          pages_site.append(sts)
          dirs[item] = pages_site
  dirs = sorted(dirs.iteritems())
  return dirs

def Templates():
  for dirs,files in Dirs():
    suffix = ('.tif','.tiff','.bmp','.jpg','.jpeg','.gif','.png','.eps','.raw','.cr2','.nef','.orf','.sr2')
    source_dir = os.path.join(pages, dirs)
    the_dir = os.path.join( document_root, dirs)
    static_dir = os.path.join(document_root, 'static')
    if not os.path.isdir(the_dir): 
      os.mkdir( the_dir )
    for filename in os.listdir(source_dir):
      if filename.endswith(suffix):
        shutil.copyfile(os.path.join(source_dir, filename), os.path.join(the_dir, filename))
  if not os.path.isdir(static_dir): 
    shutil.copytree( os.path.join(basedir, 'static'), static_dir)
  return Dirs()

def Render(file_html, to_render):
  f = io.open( os.path.join(document_root, file_html), 'w')
  f.write(to_render)
  f.close()

def Parser(frompages):
  Indexer_Title( frompages )
  Indexer_Time( frompages )
  parsered_array = []
  marker=0
  dic={}
  each_line=[]
  f = io.open(frompages,'r', encoding="utf-8")
  the_file = f.read().split('\n')
  f.close()
  for i in the_file:
    foda='some string that never will have a match !!@@@@#### do caralho......'
    pattern = re.compile(r'#.*#')
    found = re.findall(pattern, i)
    if found:
      foda = found[0]
    if i == foda:
      pass
      marker += 1
      if marker == 2:
        pass
        order=[]
        tupl=foda, each_line
        parsered_array.append(tupl)
        marker = 0
        each_line=[]
    elif marker >= 1: 
      each_line.append(i)
    else:
      if i:
        tupl='line', [i]
        parsered_array.append(tupl)
  return parsered_array

def Getter_time():
  originalorder = []
  for dirs,sites in Dirs():
    for site in sites:
      source_page = os.path.join( pages,os.path.join( dirs,site ))
      for k,v in Parser( source_page ):
        if k == '##markdate##':
          for the_date in v:
            print(the_date)
            originalorder.append({'date':the_date, 'file':os.path.join( dirs,site )})
  return sorted( originalorder, key=lambda x: datetime.datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)

app = Flask('Blog')

if __name__ == "__main__":
  with app.app_context():
    for dirs,sites in Dirs():
      for site in sites:
        r_index = render_template( 'template.html', 
            WEB_URL=WEB_URL, 
            Dirs=Templates, #just because now who call the Dirs is the Templates function
            my_site_name=site.replace('.site',''),
            parsered=Parser( os.path.join( pages,os.path.join( dirs,site ))),
            )
        Render( os.path.join(dirs,site.replace('site','html')), r_index)

  with app.app_context():
    r_index = render_template('welcome.html', 
              WEB_URL=WEB_URL,
              Dirs=Dirs,
              Getter_time=Getter_time,
              )
    Render('index.html', r_index)

