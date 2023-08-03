#!/usr/bin/env python3

import os
import sys

import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension

import weasyprint
import re

import logging
logging.basicConfig(format='%(levelname)s: %(message)s' ,stream=sys.stderr, level=logging.INFO)
LOGGER = logging.getLogger('preprocess')

# sort the file order
def sort_func(x):
	# place "papers/" at the end (like an appendix)
	try:
		x.index('%sdoc%s' % (os.path.sep, os.path.sep))
	except ValueError:
		return 'z'
	
	# place readmes at the start of each section
	try:
		rm = x.index('README.md')
		return x[:rm] + '0'
	except ValueError:
		return x

# make the links work in-pdf
def fix_links(match):
	# images
	if os.path.splitext(match.group(2))[-1] == '.png':
		return '[%s](%s)' % (
			match.group(1),
			os.path.join(os.path.split(my_file)[0], match.group(2))
		)
	
	# urls to other files
	BASE_URL = 'https://github.com/tildearrow/furnace/tree/master/'
	if match.group(2).startswith(BASE_URL):
		file_path = match.group(2).split(BASE_URL)[-1]
		if os.path.splitext(file_path)[-1] == '':
			file_path += '/README.md'
		return '[%s](#%s)' % (
			match.group(1),
			file_path.replace('/','__')
		)
	
	# preserve external urls
	elif match.group(2).startswith('http'):
		return match.group(0)
	
	# fix paths
	act_path = os.path.split(my_file)[0] + '/' + match.group(2)
	act_path = os.path.relpath(os.path.abspath(act_path))
	return '[%s](#%s)' % (
		match.group(1),
		act_path.replace(os.path.sep,'__')
	)

def fix_headings(match):
	return '%s#' % (
		match.group(1)
	)

if __name__ == "__main__":
	#-- first, prepare the file list --#
	file_list = []
	for i in os.walk('papers'):
		base_dir, subfolders, files = i
		for file_ in filter(lambda x: x.lower().endswith('.md'), files):
			file_list.append(os.path.join(base_dir, file_))

	#-- then, create the document --#
	html = ''

	# perform sort
	file_list.sort(key=sort_func)

	for my_file in file_list:
		with open(my_file, 'r') as md:
			LOGGER.info("processing file %s" % my_file)
			data = md.read()
		
		# perform link fixing
		data = re.sub(r'\[(.+?)\]\((.+?)\)', fix_links, data)
		data = re.sub(r'^\s*(#+)', fix_headings, data, flags=re.MULTILINE)
		
		# each file is its own section
		html +='<section id="%s">%s</section>' % (
			my_file.replace(os.path.sep, "__"),
			markdown.markdown(data, extensions=[GithubFlavoredMarkdownExtension()])
		)

	# build html
	final_html = ('''
		<!DOCTYPE html>
		<html lang="en">
			<head>
				<meta charset="utf-8"/>
				<title>Furnace Manual</title>
				<style>
					@font-face {
						font-family: 'IBM Plex Sans';
						font-weight: normal;
						font-style: normal;
						src: url("fonts/IBMPlexSans-Regular.ttf") format("truetype");
					}
					@font-face {
						font-family: 'IBM Plex Sans';
						font-weight: bold;
						font-style: normal;
						src: url("fonts/IBMPlexSans-Bold.ttf") format("truetype");
					}
					@font-face {
						font-family: 'IBM Plex Sans';
						font-weight: normal;
						font-style: oblique;
						src: url("fonts/IBMPlexSans-Italic.ttf") format("truetype");
					}
					@font-face {
						font-family: 'IBM Plex Sans';
						font-weight: bold;
						font-style: oblique;
						src: url("fonts/IBMPlexSans-BoldItalic.ttf") format("truetype");
					}
					body {
						font-family: 'IBM Plex Sans';
						line-height: 1.3;
						font-size: 12pt;
						color: #000;
					}
					section {
						page-break-before:always;
						text-align: justify;
						hyphens: auto;
					}
					h1,h2,h3,h4,h5,h6 {
						hyphens: none;
						text-align: left;
					}
					img {
						max-width: 100%%;
					}
					a {
						color: #365788;
						text-decoration: none;
						letter-spacing: .01em;
						font-weight: bold;
					}
					a[href^='#']:after {
						content: ' (page ' target-counter(attr(href), page) ') ';
						color: #000;
					}
					#cover {
						height: 100%%;
						text-align: center;
						display: flex;
						flex-direction: column;
					}
					#cover * {
						flex-grow: 1;
					}
					#cover h1 {
						text-align: center;
						font-size: 2.25em;
					}
					pre {
						font-size: .8em;
					}
					table {
						display: block;
						width: 100%%;
						width: max-content;
						max-width: 100%%;
						overflow: auto;
						border-collapse: collapse;
						text-align: left;
					}
					table tr {
						border-top: 1pt solid #aaa;
					}
					th, td {
						padding: 3pt 6pt;
						border: 1pt solid #ccc;
					}
					th {
						hyphens: none;
						padding: 2pt 4pt;
						text-transform: uppercase;
						font-size: .8em
					}
					@page {
						margin:  1in 1.25in;
						@bottom-center {
							content: counter(page);
							font-family: 'IBM Plex Sans';
						}
						@top-left {
							content: 'furnace manual';
							font-family: 'IBM Plex Sans';
							font-style: oblique;
						}
					}
					@page:first {
						@bottom-center {
							content: '';
						}
						@top-left {
							content: '';
						}
					}
				</style>
			</head>
			<body>
				<section id="cover">
					<div>
					</div>
					<div>
						<img src="logo.png" style="width: 72pt;">
						<h1>Furnace <br>User Manual</h1>
					</div>
					<div>
						<i>tildearrow and contributors</i>
					</div>
				</section>
				%s
			</body>
		</html>
		''' % (
			html
		)
	)
	
	print(final_html)
