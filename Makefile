#
export WEB_URL := https://engops.github.io
export document_root := ../engops.github.io

build:

ifeq "$(wildcard $(document_root) )" ""
	git -C ../ clone https://github.com/engops/engops.github.io.git
else
	cd ${document_root} && git pull
endif
	python ./blog.py

deps:
	pip install -r requirements.txt
