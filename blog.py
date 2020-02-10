#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from flask import render_template, Flask
from flask import Flask
import json
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

def Render(file_html, to_render):
  suffix = ('.tif','.tiff','.bmp','.jpg','.jpeg','.gif','.png','.eps','.raw','.cr2','.nef','.orf','.sr2')
  dst = os.path.join(document_root, os.path.split(file_html)[0])
  src = os.path.join(pages, os.path.split(file_html)[0])
  if not os.path.exists( dst ): 
    os.makedirs( dst )
  for filename in os.listdir( src ):
    if filename.endswith(suffix):
      shutil.copyfile(os.path.join(src, filename), os.path.join(dst, filename))
  if not os.path.isdir( os.path.join(document_root, 'static') ): 
    shutil.copytree( os.path.join(basedir, 'static'), os.path.join(document_root, 'static'))

  f = io.open( os.path.join(document_root, file_html), 'w')
  f.write(to_render)
  f.close()

def path_to_dict(path):
  foda = []
  if os.listdir(path):
    for the_dir1 in os.listdir(path):
      dic={}
      dir1_p = os.path.join(path,the_dir1)
      if os.path.isdir(dir1_p):
        #print dir1_p
        for a in os.listdir(dir1_p):
          fodinha = []
          if os.path.isdir( os.path.join(dir1_p, a)) or a.endswith('.site') :
            dic['name'] = the_dir1
            dic['type'] = 'directory'
            for b in os.listdir(dir1_p):
              if os.path.isdir( os.path.join(dir1_p, b)) or b.endswith('.site'):
                subfodinha = []
                dictinho = {}
                if os.path.isdir(os.path.join(dir1_p, b)):
                  dictinho['name'] = b
                  dictinho['type'] = 'directory'
                  for c in os.listdir(os.path.join(dir1_p, b)):
                    subdictinho = {}
                    if os.path.isdir( os.path.join(os.path.join(dir1_p, b), c) ) or c.endswith('.site'):
                      subdictinho['name'] = c
                      subdictinho['type'] = 'file'
                      subfodinha.append(subdictinho)
                    dictinho['children'] = subfodinha
                else:
                  dictinho['name'] = b
                  dictinho['type'] = 'file'
                fodinha.append(dictinho)
            dic['children'] = fodinha
            foda.append(dic)
            break
  return foda         

def treta():
  return path_to_dict(pages)
  #i = json.dumps(path_to_dict(pages), sort_keys=True)
  #o = json.loads(i)
  #print o
  #return o

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

def Parser(frompages):
  Indexer_Title( frompages )
  Indexer_Time( frompages )
  parsered_array = []
  marker=0
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

def all_sites():
  a_s =[]
  for pags in treta():
    for sub_or_f in pags['children']:
      if sub_or_f['type'] == 'file':
        a_s.append( os.path.join(  pags['name'], sub_or_f['name'] ))
      elif sub_or_f['type'] == 'directory':
        for sub_sub_f in sub_or_f['children']:
          a_s.append( os.path.join(  pags['name'], os.path.join( sub_or_f['name'], sub_sub_f['name'] )))
  return a_s

def Getter_time():
  originalorder = []
  title = ''
  for source_page in all_sites():
    for k,v in Parser(os.path.join(pages, source_page )):
      if k == '##markdate##':
        for the_date in v:
          date = the_date
      if k == '#title#':
        for the_title in v:
          title = the_title
          originalorder.append({'date':the_date, 'file':source_page, 'title':title })
  return sorted( originalorder, key=lambda x: datetime.datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)

app = Flask('Blog')
if __name__ == "__main__":
  with app.app_context():
    j=json.dumps(path_to_dict(pages), ensure_ascii=False)
    jl=json.loads(j, encoding="utf-8")
  
    for pags in treta():
      for sub_or_f in pags['children']:
        if sub_or_f['type'] == 'file':
          r_index = render_template( 'template.html', 
              WEB_URL=WEB_URL, 
              treta=treta,
              parsered=Parser( os.path.join( pages, os.path.join(  pags['name'], sub_or_f['name'] )) ),
              )
          Render( os.path.join(  pags['name'], sub_or_f['name'].replace('site','html') ), r_index )
        elif sub_or_f['type'] == 'directory':
          for sub_sub_f in sub_or_f['children']:
            if sub_sub_f['name'].endswith('.site'):
              r_index = render_template( 'template.html', 
                  WEB_URL=WEB_URL, 
                  treta=treta,
                  parsered=Parser( os.path.join( pages, os.path.join(  pags['name'], os.path.join( sub_or_f['name'], sub_sub_f['name'] ))) ),
                  )
              Render( os.path.join( pags['name'], os.path.join( sub_or_f['name'], sub_sub_f['name'] ).replace('site','html')), r_index)

#####################################################################################################################################################################
  with app.app_context():
    r_index = render_template('welcome.html', 
              WEB_URL=WEB_URL,
              treta=treta,
              Getter_time=Getter_time,
              )
    Render('index.html', r_index)

