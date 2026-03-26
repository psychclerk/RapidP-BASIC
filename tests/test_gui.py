import unittest
import tkinter as tk
from rp_runtime.gui import PForm, PButton, PLabel, PEdit

class TestGUI(unittest.TestCase):
    def test_qform(self):
        f = PForm()
        f.caption = "Test Form"
        f.width = 400
        f.height = 300
        
        # Check Tkinter widget underlying properties
        self.assertEqual(f.widget.title(), "Test Form")
        self.assertEqual(f.width, 400)
        self.assertEqual(f.height, 300)
        
        f.close()
        
    def test_qbutton(self):
        f = PForm()
        b = PButton(f)
        b.caption = "Click Me"
        
        self.assertEqual(b.widget.cget("text"), "Click Me")
        
        # event hook
        clicked = False
        def my_click():
             nonlocal clicked
             clicked = True
             
        b.onclick = my_click
        b.widget.invoke()
        self.assertTrue(clicked)
        f.close()
        
    def test_qedit(self):
         f = PForm()
         e = PEdit(f)
         e.text = "Hello Tkinter"
         self.assertEqual(e.text, "Hello Tkinter")
         f.close()

if __name__ == '__main__':
    unittest.main()
