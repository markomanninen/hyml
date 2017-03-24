#!/usr/bin/python3

(eval-and-compile 
  ; without eval-and-compile setv variables doesn't work as a global variable for macros
  (setv variables-and-functions {}))

; global variable handler
(defmacro defvar [&rest args]
  (setv l (len args) i 0)
  (while (< i l)
    (do
      (assoc variables-and-functions (get args i) (get args (inc i)))
      (setv i (+ 2 i)))))

; global function handler
(defmacro deffun [name func]
  (assoc variables-and-functions name (eval func)))
