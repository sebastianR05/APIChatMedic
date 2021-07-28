from distutils.core import setup 
import py2exe 
 
setup(name="APIChatMedic", 
 version="1.0", 
 description="Breve descripcion", 
 author="autor", 
 author_email="email del autor", 
 url="url del proyecto", 
 license="tipo de licencia", 
 scripts=["app.py"],
 console=["app.py"] ,
 options={"py2exe": {"bundle_files": 1}}, 
 zipfile=None,
)