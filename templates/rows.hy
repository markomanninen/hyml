~@(list-comp* [row rows]
  `(tr (td ~(get row 0))
	   (td ~(get row 1))
	   (td ~(get row 2))))