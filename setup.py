from distutils.core import setup

install_requires = ['hy>=0.12.1']

#python setup.py register -r pypitest
#python setup.py register -r pypi
# next command not recommended but what can you do in Windows...
#python setup.py sdist upload -r pypitest
#python setup.py sdist upload

setup(
  name = 'hyml',
  
  packages = ['hyml'],
  package_dir = {'hyml': 'hyml'},
  package_data = {
    'hyml': ['*.hy']
  },
  
  version = 'v0.2.3',
  description = 'HyML - XML / (X)HTML generator for Hy',
  author = 'Marko Manninen',
  author_email = 'elonmedia@gmail.com',

  url = 'https://github.com/markomanninen/hyml',
  download_url = 'https://github.com/markomanninen/hyml/archive/v0.2.3.tar.gz',
  keywords = ['hylang', 'python', 'lisp', 'macros', 'markup language', 'dsl', 'xml', 'html', 'xhtml'],
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
