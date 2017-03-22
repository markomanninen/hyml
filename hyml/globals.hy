#!/usr/bin/python3
(eval-and-compile 
  ; without eval-and-compile setv variables doesn't work as a global variable for macros
  (setv variables {})
  (defclass HyMLError [Exception]))

; for example: (defvar x 1 y 2 z 3)
(defmacro defvar [&rest args]
  ; cast tuple to list to make removal of list items work
  (setv args (list args))
  ; only even number of arguments are accepted
  (if (even? (len args))
      (do
        (setv rtrn (second args))
        (while (pos? (len args))
             (do
               ; update dictionary key with a value
               (assoc variables (first args) (second args))
               ; remove first two arguments (key-value pair)
               (.remove args (get args 0))
               (.remove args (get args 0))))
        rtrn)
      (raise (HyMLError "defvar needs an even number of arguments"))))