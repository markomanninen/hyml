from distutils.core import setup

install_requires = ['hy>=0.12.1']

setup(
  name = 'hyml',
  
  packages = ['hyml'],
  package_dir = {'hyml': 'hyml'},
  package_data = {
    'hyml': ['*.hy']
  },
  
  version = 'v0.1.1',
  description = 'HyML - XML / (X)HTML generator for Hy',
  author = 'Marko Manninen',
  author_email = 'elonmedia@gmail.com',

  url = 'https://github.com/markomanninen/hyml', # use the URL to the github repo
  download_url = 'https://github.com/markomanninen/hyml/archive/v0.1.1.tar.gz', # I'll explain this in a second
  keywords = ['hylang', 'python', 'markup language', 'dsl', 'xml', 'html', 'xhtml'], # arbitrary keywords
  platforms = ['any'],
  
  classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Lisp",
    "Topic :: Software Development :: Libraries",
  ]
)