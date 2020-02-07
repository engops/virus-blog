#
export WEB_URL := https://engops.github.io
export document_root := ../engops.github.io

build:
	git -C ../ clone https://github.com/engops/engops.github.io.git
	python ./blog.py

deps:
	pip install -r requirements.txt
